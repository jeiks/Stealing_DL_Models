#!/bin/bash

[ $# -ne 1 ] && {
    echo "Use: $0  weights.caffemodel"
    exit 1
}

#CAFFE:
CAFFE_BIN='/home/jeiks/Downloads/caffe/build/tools/caffe'

#VGG:
VGG_PATH='/home/jeiks/Doutorado/VGG_FACE/vgg_face_caffe'

#PROTOTXT FILES:
PROTOTXT_PATH="$VGG_PATH/prototxt"
MODEL_TEST="$PROTOTXT_PATH/train_test.prototxt"
MODEL_VAL="$PROTOTXT_PATH/val.prototxt"
WEIGHTS=$1

echo Testing the network...
$CAFFE_BIN test --model $MODEL_TEST --weights $WEIGHTS -gpu=1 &> .log-test
echo Validating the network...
$CAFFE_BIN test --model $MODEL_VAL  --weights $WEIGHTS -gpu=1 &> .log-val

echo Test:
grep -A 2 'Loss: ' .log-test | cut -d\] -f2
echo Validation:
grep -A 2 'Loss: ' .log-val  | cut -d\] -f2

