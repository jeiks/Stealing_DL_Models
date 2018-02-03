#!/bin/bash

#CAFFE:
CAFFE_BIN='/home/jeiks/Doutorado/caffe/build/tools/caffe'

#PROTOTXT FILES:
PROTOTXT_PATH="$PWD/prototxt"
SOLVER="$PROTOTXT_PATH/solver.prototxt"
WEIGHTS='VGG_FACE.caffemodel'
GPU=1
LOG_FILE=$(date "+log-%Y_%m_%d-%H_%M.txt")

echo "Using:
PROTOTXT_PATH = $PROTOTXT_PATH
SOLVER        = $SOLVER
WEIGHTS       = $WEIGHTS
GPU           = $GPU
"
read -n1 -p 'Press ENTER to start training... '

#$CAFFE_BIN train --solver=$SOLVER --weights=$WEIGHTS -gpu=$GPU 2>&1 | tee $LOG_FILE
$CAFFE_BIN train --solver=$SOLVER --snapshot=models/snapshot_iter_320685.solverstate -gpu=$GPU 2>&1 | tee $LOG_FILE
