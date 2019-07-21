#!/bin/bash
# Script to create LMDB and MEAN to train the network

[ $# -ne 4 ] && {
    echo "Use: $0 data_root train.txt test.txt val.txt"
    exit 1
}

exit_p() { echo -e "$1"; exit $2; }

DATA_ROOT=$1
TRAIN_FILE=$2
TEST_FILE=$3
VAL_FILE=$4

test -d $DATA_ROOT || exit_p "Directory not found: \`$DATA_ROOT'" 2
for i in "$TRAIN_FILE" "$TEST_FILE" "$VAL_FILE";do
 test -f $i || exit_p "File not found: \`$i'" 3
 D=${i%.txt}_lmdb
 test -d "$D" && exit_p "Directory \`$D' already exists.\nRemove it to continue." 4
done

#VGG:
VGG_PATH='/home/jeiks/Doutorado/VGG_FACE/vgg_face_caffe'

#CAFFE:
CAFFE_TOOLS='/home/jeiks/Downloads/caffe/build/tools'
LMDB_TOOL="$CAFFE_TOOLS/convert_imageset.bin"
MEAN_TOOL="$CAFFE_TOOLS/compute_image_mean.bin"

#DATASETS TO CREATE:
DATA_PATH="$VGG_PATH/data"
DATA_TRAIN="$DATA_PATH/train_lmdb"
DATA_TEST="$DATA_PATH/test_lmdb"
DATA_VAL="$DATA_PATH/val_lmdb"
DATA_MEAN="$DATA_PATH/train.mean"

# OPTIONS:
RESIZE_HEIGHT='-resize_height=224'
RESIZE_WIDTH='-resize_width=224'
SHUFFLE='-shuffle'

create_lmdb() {
    echo "Creating lmdb for '$1'..."
    $LMDB_TOOL $RESIZE_HEIGHT $RESIZE_WIDTH $SHUFFLE \
        $DATA_ROOT "$1" "$2"
}

create_lmdb $TRAIN_FILE $DATA_TRAIN
create_lmdb $TEST_FILE  $DATA_TEST
create_lmdb $VAL_FILE   $DATA_VAL

$MEAN_TOOL $DATA_TRAIN $DATA_MEAN
