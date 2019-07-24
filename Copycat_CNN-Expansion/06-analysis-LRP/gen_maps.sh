#!/bin/bash

[ $# -ne 1 ] && {
    echo "Use: $0 source_dir"
    exit  1
}

ROOT="${1%/}"
ORIG_D="$ROOT/original_lrp_output/${ROOT##*/}/images/"
COPY_D="$ROOT/copycatREPLACE_lrp_output/${ROOT##*/}/images/"
COPY_TD="$ROOT/TD_copycatREPLACE.txt"
TARGET_D=$ROOT/target
IMG_LIST="$ROOT/images-with-labels.txt"
COPYCATS_SIZE="-0k -100k -500k -1m -1.5m"
mkdir -p $TARGET_D

get_copycat_heatmaps(){
    IMG=$1
    COPYCATS=()
    for i in $COPYCATS_SIZE;do
        C=${COPY_D/REPLACE/$i}/${IMG}_heatmap.png
        if test -f $C;then
            COPYCATS=(${COPYCATS[@]} $C)
        else
            echo "Cannot find '$C'.. exiting"
            exit 2
        fi
    done
    C=${COPY_D/REPLACE/}/${IMG}_heatmap.png
    COPYCATS=(${COPYCATS[@]} $C)
    if [ ${#COPYCATS[@]} -eq 0 ];then
        echo "No copycat found. Exiting..."
        exit 2
    fi
    echo ${COPYCATS[@]}
}

get_copycat_outputs(){
    IMG=$1
    COPY_OUTPUTS=()
    for i in $COPYCATS_SIZE;do
        C_TD=${COPY_TD/REPLACE/$i}
        COPY_OUTPUTS=(${COPY_OUTPUTS[@]} $(grep $IMG $C_TD | awk '{print $NF}'))
    done
    C_TD=${COPY_TD/REPLACE/}
    COPY_OUTPUTS=(${COPY_OUTPUTS[@]} $(grep $IMG $C_TD | awk '{print $NF}'))
    echo ${COPY_OUTPUTS[@]}
}

while read IMG CORRECT_OUTPUT OUTPUT_ORIG OUTPUT_COPY;do
    IMG=${IMG##*/}
    B=$ORIG_D/${IMG}_as_inputted_into_the_dnn.png
    O=$ORIG_D/${IMG}_heatmap.png
    ##COPYCATS: "0k 100k 500k 1m 1.5m"
    COPYCATS=($(get_copycat_heatmaps $IMG))
    COPY_OUTPUTS=($(get_copycat_outputs $IMG))

    IMG_HEADER="$TARGET_D/header"
    IMG_TEMP="$TARGET_D/temp.png"
    SIZE=$(identify $B | awk '{print $3}' | sed 's;\([0-9]\+\)x.*;\1x25;')
    
    ########################### IMAGE WITH DATA CURVE ###########################
    TARGET="$TARGET_D/$CORRECT_OUTPUT-$OUTPUT_ORIG-$OUTPUT_COPY-data_curve-$IMG"
    echo "Creating '$TARGET'..."
    #joining images
    convert $B $O ${COPYCATS[@]} +append -depth 16 $IMG_TEMP
    #creating headers:
    rm -f $IMG_HEADER*
    HEADERS=($CORRECT_OUTPUT $OUTPUT_ORIG ${COPY_OUTPUTS[@]})
    LABELS=("Desired label:" "Target Network:" \
            "Copycat 0k:" "Copycat 100k:" "Copycat 500k:"\
            "Copycat 1M:" "Copycat 1.5M:" "Copycat 3M:")
    case "$(identify $B)" in
        *224x224*) FONT_SIZE=20 ;;
        *200x200*) FONT_SIZE=18 ;;
                *) FONT_SIZE=12;;
    esac
    for i in `seq 0 $((${#LABELS[@]}-1))`;do
        convert -background white               \
            -fill       black                   \
            -pointsize  $FONT_SIZE              \
            -define png:preserve-colormap=true  \
            -size $SIZE                         \
            caption:"${LABELS[$i]} ${HEADERS[$i]}"     \
            $IMG_HEADER-${i}.png
    done
    convert $IMG_HEADER-*.png  \
            +append        \
            -depth 16      \
            -define png:preserve-colormap=true  \
            $IMG_HEADER.png
    #header + image:
    convert $IMG_HEADER.png $IMG_TEMP \
            -append                   \
            -depth 16                 \
            $TARGET
    rm -f $IMG_HEADER* $IMG_TEMP
    
    ###################### IMAGE WITH ORIGINAL AND COPYCAT ######################
    TARGET="$TARGET_D/$CORRECT_OUTPUT-$OUTPUT_ORIG-$OUTPUT_COPY-$IMG"
    echo "Creating '$TARGET'..."
    #joining images
    convert $B $O ${COPYCATS[5]} +append -depth 16 $IMG_TEMP
    #creating headers:
    rm -f $IMG_HEADER*
    HEADERS=($CORRECT_OUTPUT $OUTPUT_ORIG ${COPY_OUTPUTS[5]})
    LABELS=("Desired label:" "Target Network:" "Copycat 3M:")
    case "$(identify $B)" in
        *224x224*) FONT_SIZE=20 ;;
        *200x200*) FONT_SIZE=18 ;;
                *) FONT_SIZE=12;;
    esac
    for i in 0 1 2;do
        convert -background white               \
            -fill       black                   \
            -pointsize  $FONT_SIZE              \
            -define png:preserve-colormap=true  \
            -size $SIZE                         \
            caption:"${LABELS[$i]} ${HEADERS[$i]}"     \
            $IMG_HEADER-${i}.png
    done
    convert $IMG_HEADER-*.png  \
            +append        \
            -depth 16      \
            -define png:preserve-colormap=true  \
            $IMG_HEADER.png
    #header + image:
    convert $IMG_HEADER.png $IMG_TEMP \
            -append                   \
            -depth 16                 \
            $TARGET
    rm -f $IMG_HEADER* $IMG_TEMP
    
done < $IMG_LIST
