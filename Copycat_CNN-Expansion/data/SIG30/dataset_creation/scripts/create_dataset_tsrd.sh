#!/bin/bash

LABELS='TT100K-TSRD.txt'
ZIP_TRAIN='tsrd-train.zip'
ZIP_TEST='TSRD-Test.zip'
TRAIN='train'
TEST='test'
IMAGES='images'

for i in $ZIP_TRAIN $ZIP_TEST;do
    test -f $i -o -h $i || {
        echo "Please download '$ZIP_TRAIN' and '$ZIP_TEST' before continue..." >&2
        echo 'http://www.nlpr.ia.ac.cn/pal/trafficdata/recognition.html'
        exit 1
    }
done

for i in $TRAIN $TEST $IMAGES;do
    test -d $i && {
        echo "Please remove the folder '$TRAIN', '$TEST', and '$IMAGES' before continue..." >&2
        exit 2
    }
done

mkdir -p $TRAIN $TEST $IMAGES/train $IMAGES/test
unzip -d test/  $ZIP_TEST  &> /dev/null
unzip -d train/ $ZIP_TRAIN &> /dev/null

fdupes -rdN train/ test &> removed_files || {
    echo "Please install 'fdupes' before continue"
    echo "sudo apt install fdupes"
    exit 3
}

> images_train.txt
> images_test.txt
while read TT100K TSRD;do
    for i in $TRAIN/${TSRD}_*;do
        case "$i" in *\**) continue;;esac #no match
        TRG=$IMAGES/${TT100K}-${i#*/} #target

        echo "$TRG $TT100K" >> images_train.txt
        mv $i $IMAGES/${TT100K}-${i#*/} 2>> errors
   done
    for i in $TEST/${TSRD}_*;do
        case "$i" in *\**) continue;;esac #no match
        TRG=$IMAGES/${TT100K}-${i#*/} #target

        echo "$TRG $TT100K" >> images_test.txt
        mv $i $IMAGES/${TT100K}-${i#*/} 2>> errors
   done

done < $LABELS

rm -rf $TRAIN $TEST 2>> errors > /dev/null
[ $(wc -l < errors) -eq 0 ] && rm -f errors #no errors
