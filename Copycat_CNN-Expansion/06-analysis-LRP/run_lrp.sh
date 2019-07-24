#!/bin/bash

[ $# -ne 1 ] && {
    echo "Use: $0 ROOT_PATH"
    exit 1
}

### LSRP SPECIFIC PARAMS ###
EPS=1
ALPHABETA=1
#FORMULAS WITH BETTER VISUALIZATION ON OUTPUT: 26, 100
FORMULA=26
#LASTLAYERINDEX:
#-1 finds lowest softmax layer and inserts at the layer below in the top vector
#-2 find the highest innerproduct layer and inserts at this layer in the top vector
LASTLAYERINDEX=-1
#APPLY LOGARITHM:
USE_LOG=1
############################

LRP_BIN='./source/lrp_demo'
HEATMAP_BIN='./scripts/heatmap.sh'
CREATE_HTML=0

apply_lrp(){
    echo -e "param_file\n$PARAM_FILE
    \b\b\b\b\nmodel_file\n$MODEL_FILE
    \b\b\b\b\nmean_file\n$MEAN_FILE
    \b\b\b\b\nsynsetfile\n$SYNSETFILE
    \b\b\b\b\nuse_mean_file_asbinaryprotoblob\n1
    \b\b\b\b\nlastlayerindex\n$LASTLAYERINDEX
    \b\b\b\b\nfirstlayerindex\n0
    \b\b\b\b\nnumclasses\n$NUMCLASSES
    \b\b\b\b\nbaseimgsize\n$IMGSIZE
    \b\b\b\b\nstandalone_outpath\n$OUTPATH
    \b\b\b\b\nstandalone_rootpath\n$ROOTPATH
    \b\b\b\b\nepsstab\n$EPS
    \b\b\b\b\nalphabeta_beta\n$ALPHABETA
    \b\b\b\b\nrelpropformulatype\n$FORMULA
    \b\b\b\b\nauxiliaryvariable_maxlayerindexforflatdistinconv\n0
    " > $CONFIG

    $LRP_BIN $CONFIG $IMAGE_LIST ./ 2>&1 | tee ${LOG_FILE}_lrp.txt
    $HEATMAP_BIN $IMAGE_LIST heatmap $OUTPATH/$ROOTPATH $USE_LOG 2>&1 | tee ${LOG_FILE}_heatmap.txt

    if [ $CREATE_HTML -ne 0 ];then
        D=$PWD
        cd $OUTPATH/$ROOTPATH || exit 2
        mkdir -p new/
        for i in *rawhm.txt;do
            i=${i%_rawhm.txt}
            echo "<div><img src='${i}_as_inputted_into_the_dnn.png'><img src='${i}_heatmap.png'></div>"
        done > new/lrp.html
        cp *.png new/
        mogrify -resize 100x100 new/*.png
        cd $D
    fi
}

check_images() {
    case ${1^^} in
        ORIGINAL*) WHICH=2;;
        COPYCAT*) WHICH=3;;
        *) return
    esac
    IMG_LABELS_FN="$ROOT/images-with-labels.txt"
    cp $IMG_LABELS_FN $IMG_LABELS_FN.backup$WHICH
    for i in $OUTPATH/$ROOTPATH/*top*txt;do
        IMG=${i##*/}
        IMG=${IMG%_*}
        LRP_LABEL=$(grep -om1 '[0-9]\+ ' $i)
        LABELS=($(grep -m1 $IMG $IMG_LABELS_FN))
        if [ ${#LABELS[@]} -eq 0 ];then continue;fi
        if [ $LRP_LABEL -eq ${LABELS[$WHICH]} ];then
            echo ${LABELS[@]}
        fi
    done > $IMG_LABELS_FN.temp
    cat $IMG_LABELS_FN.temp > $IMG_LABELS_FN
    while read IMG _;do
        echo "${ROOT##*/}/images/${IMG##*/} -1"
    done < $IMG_LABELS_FN > $ROOT/images.txt
    rm -f $IMG_LABELS_FN.temp
}

##EQUAL FOR BOTH MODELS:
if [ "${1:0:1}" = '/' ];then
    ROOT=${1%/}
else
    ROOT="$PWD/${1%/}"
fi

# model:
PARAM_FILE="$ROOT/net_sequential.prototxt"
# classes:
SYNSETFILE="$ROOT/synset_words.txt"
# image list (images inside rootpath)
IMAGE_LIST="$ROOT/images.txt"
# images path present in IMAGE_LIST
ROOTPATH="${ROOT##*/}/images"

NUMCLASSES=$(grep num_output: $ROOT/net_sequential.prototxt | tail -n1 | grep -o '[0-9]\+$')
IMGSIZE=$(grep dim: $ROOT/net_sequential.prototxt | tail -n1 | grep -o '[0-9]\+$')
echo "Num. Classes: $NUMCLASSES"
echo "Img. Size:... $IMGSIZE"
echo "ROOT:........ $ROOT"
read -p 'Press ENTER to continue...'
##

#ORIGINAL MODEL:
MODEL_FILE="$ROOT/original.caffemodel"
MEAN_FILE="$ROOT/train.mean"

OUTPATH="$ROOT/original_lrp_output"
CONFIG="$ROOT/config_original.txt"
LOG_FILE=$(date "+$ROOT/log-original-%Y_%m_%d-%H_%M")
apply_lrp

check_images original

#COPYCAT MODEL:
MODEL_FILE="$ROOT/copycat.caffemodel"
MEAN_FILE="$ROOT/NPD.mean"

OUTPATH="$ROOT/copycat_lrp_output"
CONFIG="$ROOT/config_copycat.txt"
LOG_FILE=$(date "+$ROOT/log-copycat-%Y_%m_%d-%H_%M")
apply_lrp

check_images copycat

for i in 0k 100k 500k 1m 1.5m;do
    #COPYCAT 0k:
    MODEL_FILE="$ROOT/copycat-$i.caffemodel"
    if [ ! -f $MODEL_FILE ];then
        echo "cannot find '$MODEL_FILE'"
        continue
    fi
    MEAN_FILE="$ROOT/NPD.mean"

    OUTPATH="$ROOT/copycat-${i}_lrp_output"
    CONFIG="$ROOT/config_copycat-$i.txt"
    LOG_FILE=$(date "+$ROOT/log-copycat-$i-%Y_%m_%d-%H_%M")
    apply_lrp
    GPU=${GPU:=0}
    echo "Generating TD's labels for '$MODEL_FILE'..."
    $HD/Scripts/label_dataset_from_image_list.py    \
            -m $ROOT/deploy.prototxt                \
            -f $ROOT/images.txt                     \
            -w $MODEL_FILE -b 120 -g $GPU           \
            -o $ROOT/TD_copycat-$i.txt  2> $(date "+$ROOT/log-td-$i-%Y_%m_%d-%H_%M")
done
