#!/bin/bash

#CAFFE:
CAFFE_BIN='/home/jeiks/Downloads/caffe/build/tools/caffe'

#VGG:
VGG_PATH=$PWD

#PROTOTXT FILES:
PROTOTXT_PATH="$VGG_PATH/prototxt"
SOLVER="$PROTOTXT_PATH/solver.prototxt"
WEIGHTS='VGG_FACE.caffemodel'

LOG_FILE=$(date "+log-%Y_%m_%d-%H_%M.txt")

echo "Using:
VGG_PATH = $VGG_PATH
SOLVER   = $SOLVER
WEIGHTS  = $WEIGHTS
"
read -n1 -p 'Press ENTER to start training... '

$CAFFE_BIN train --solver=$SOLVER --weights=$WEIGHTS -gpu=1 2>&1 | tee $LOG_FILE
