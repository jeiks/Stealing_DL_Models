#!/bin/bash

#CAFFE:
CAFFE_BIN='/home/jeiks/Doutorado/caffe/build/tools/caffe'

#VGG:
VGG_PATH=$PWD

#PROTOTXT FILES:
PROTOTXT_PATH="$VGG_PATH/prototxt"
SOLVER="$PROTOTXT_PATH/solver.prototxt"
WEIGHTS='VGG_ILSVRC_16_layers.caffemodel'

LOG_FILE=$(date "+log-%Y_%m_%d-%H_%M.txt")
GPU=1

echo "Using:
VGG_PATH = $VGG_PATH
SOLVER   = $SOLVER
WEIGHTS  = $WEIGHTS
GPU      = $GPU

$CAFFE_BIN train -weights $WEIGHTS --solver=$SOLVER -gpu=$GPU
"
read -n1 -p 'Press ENTER to start training... '

$CAFFE_BIN train -weights $WEIGHTS --solver=$SOLVER -gpu=$GPU 2>&1 | tee $LOG_FILE
