#!/bin/bash

#CAFFE:
CAFFE_BIN='/home/jeiks/Doutorado/caffe/build/tools/caffe'

#VGG:
ALEXNET_PATH=$PWD

#PROTOTXT FILES:
PROTOTXT_PATH="$ALEXNET_PATH/prototxt"
SOLVER="$PROTOTXT_PATH/solver.prototxt"
WEIGHTS='bvlc_alexnet.caffemodel'

LOG_FILE=$(date "+log-%Y_%m_%d-%H_%M.txt")

CARD=1

echo "Using:
ALEXNET_PATH = $ALEXNET_PATH
SOLVER       = $SOLVER
WEIGHTS      = $WEIGHTS
CARD         = $CARD
"
read -n1 -p 'Press ENTER to start training... '

$CAFFE_BIN train --solver=$SOLVER --weights=$WEIGHTS -gpu=$CARD 2>&1 | tee $LOG_FILE
