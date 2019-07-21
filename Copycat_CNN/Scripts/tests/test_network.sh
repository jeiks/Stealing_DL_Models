#!/bin/bash
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

[ $# -lt 1 ] && {
    echo "Use: $0 weights"
    exit 0
}

DIR=$PWD
cd "${0%/*}"

CAFFE='/home/jeiks/Doutorado/caffe/build/tools/caffe.bin'
case "$2" in 1) GPU=1;; *) GPU=0;;esac
WEIGHTS="$DIR/$1"


case $WEIGHTS in
    ####################### CIFAR #####################################
    *[Cc][Ii][Ff][Aa][Rr]*)
       case $WEIGHTS in
            ##### CIFAR VGG #####
            *vgg*)
            PROTOTXT='prototxt/cifar_vgg.prototxt'
            BATCH=100
            LMDB_DIR='cifar_vgg'
            ;;
            ##### CIFAR ALEXNET #####
            *alexnet*)
            PROTOTXT='prototxt/cifar_alexnet.prototxt'
            BATCH=1000
            LMDB_DIR='cifar_alexnet'
            ;;
        esac
        TEST0=('Cifar train data'     "$LMDB_DIR/cifar_train_lmdb")
        TEST1=('Cifar test data'      "$LMDB_DIR/cifar_test_lmdb")
        MSGS=("${TEST0[0]}" "${TEST1[0]}")
        TEST=( ${TEST0[1]}   ${TEST1[1]})
        N=2
        DATA_MEAN="$LMDB_DIR/cifar_train.mean"
        #EXTRA_OPT="-t cifar"
    ;;
    ####################### CROSSWALK #################################
    *[cC][rR][oO][sS][sS][wW][aA][lL][kK]*)
        TEST0=('Crosswalk train data' 'crosswalk_vgg/train_lmdb')
        TEST1=('Crosswalk test data'  'crosswalk_vgg/test_lmdb')
        MSGS=("${TEST0[0]}" "${TEST1[0]}")
        TEST=( ${TEST0[1]}   ${TEST1[1]})
        N=2
        DATA_MEAN='crosswalk_vgg/train.mean'
        PROTOTXT='prototxt/crosswalk_vgg.prototxt'
        BATCH=128
    ;;
    ####################### FacialExpressions #########################
    *)
        TEST0=('Fold1 sem kdef e ck+ (treino RNA 1)'  'data/train_lmdb')
        TEST1=('CK+ de todos folds (validação RNA 1)' 'data/test_lmdb')
        TEST2=('CK Puro'                              'data/CK_lmdb')
        TEST3=('KDEF Puro'                            'data/KDEF_lmdb')
        #MSGS=("${TEST0[0]}" "${TEST1[0]}" "${TEST2[0]}" "${TEST3[0]}")
        #TEST=( ${TEST0[1]}   ${TEST1[1]}   ${TEST2[1]}   ${TEST3[1]})
        MSGS=("${TEST0[0]}" "${TEST2[0]}")
        TEST=(${TEST0[1]}   ${TEST2[1]})
        N=2
        DATA_MEAN='data/train.mean'
        #EXTRA_OPT="-t facial"
        case $WEIGHTS in
            ##### FacialExpressions Alexnet ######
            *alexnet*)
            PROTOTXT='prototxt/alex.prototxt'
            BATCH=1000
            ;;
            ##### FacialExpressions VGG #####
            *)
            PROTOTXT='prototxt/vgg.prototxt'
            BATCH=100
            ;;
        esac
    ;;
esac

for ((i=0;i<$N;i++));do
    test -d ${TEST[$i]} || { echo "ERROR: cannot access \`${TEST[$i]}'";exit 1; }
done

for ((i=0;i<$N;i++));do
#for ((i=$N-1;i<$N;i++));do #only test dataset
    echo -e "\033[1;2mTesting '${MSGS[$i]}':\033[0m"
    ./test_dataset.py -m $PROTOTXT -l ${TEST[$i]} -w $WEIGHTS -i $DATA_MEAN -b $BATCH -g $GPU $EXTRA_OPT -c 1 2> /tmp/.log_test_net
    echo
done

cd "$DIR"
