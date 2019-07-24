#!/bin/bash

#CAFFE:
CAFFE_BIN=`which caffe`

#PROTOTXT FILES:
PROTOTXT_PATH="$PWD/prototxt"
SOLVER="$PROTOTXT_PATH/solver.prototxt"
WEIGHTS='snapshot_iter_15623.caffemodel'
GPU=2

LOG_FILE=$(date "+log-%Y_%m_%d-%H_%M.txt")

echo "Using:
SOLVER   = $SOLVER
WEIGHTS  = $WEIGHTS
GPU      = $GPU
"
read -n1 -p 'Press ENTER to start training... '

$CAFFE_BIN train --solver=$SOLVER --weights=$WEIGHTS -gpu=$GPU 2>&1 | tee $LOG_FILE
