#!/bin/bash -e

function copy(){
    S=$1
    T=$2
    while read FILE CLASS;do
        FILE=${S%/*}/$FILE
        #if file exists and is greater than zero
        if [ -s "$FILE" ];then
            # link it to avoid using unnecessary disk space
            ln $FILE $T/
            # prints the new localization and class
            echo $T/${FILE[0]##*/} $CLASS
        fi
    done < <(grep -f <(awk '{print $1"$"}' TT100K-TSRD.txt) "$S")
}

# unzip TSRD and move this files to a name
# compatible with TT100K
function prepare_tsrd(){
    echo TSRD...
    mkdir TSRD
    D=$PWD
    cd TSRD
    ln -s ../datasets/TSRD-Test.zip
    ln -s ../datasets/tsrd-train.zip
    ln -s ../TT100K-TSRD.txt
    ../scripts/create_dataset_tsrd.sh > tsrd.log
    cd $D
}

# crop all images using TT100K annotation
function prepare_tt100k(){
    D=$PWD
    echo TT100K...
    mkdir TT100K
    cd TT100K
    ln -s ../datasets/data.zip
    unzip data.zip &> /dev/null
    ../scripts/crop_images_tt100k.py data/annotations.json images &> tt100k.log
    cd $D
}

function create_dataset() {
    NAME=$1
    SRC=$2
    echo "$NAME..."
    mkdir $NAME
    > $NAME.txt
    copy $SRC $NAME > $NAME.txt
}

function imgaug() {
    IMG_LIST=$1
    TRG="$IMG_LIST-imgaug"
    N=$2
    ./scripts/image-augmentation.py $IMG_LIST $TRG $N
    find $TRG -type f | sed 's;\(.*class_\)\([0-9]\+\)\(-.*\);\1\2\3 \2;' > $TRG.txt
}

prepare_tsrd
prepare_tt100k

# Generating dataset:
create_dataset OD TT100K/images_train.txt
create_dataset TD TT100K/images_test.txt
cat TSRD/images_train.txt TSRD/images_test.txt | sort | uniq > TSRD/images.txt
create_dataset PD TSRD/images.txt

sed -i.bck -f <(awk 'BEGIN{n=0;}{print "s/ "$1"$/ "n"/"; n++;}' TT100K-TSRD.txt) {OD,TD,PD}.txt

imgaug OD.txt 1000
imgaug PD.txt 1000
