#!/bin/bash

[ $# -lt 3 ] && {
    echo "Use: $0 image_file_list.txt suffix_to_heatmap.png raw_heatmap_pathname [1:use_log,0:no_use_log]"
    exit 1
}

LIST=$1
SUFFIX="${2%%.png}.png"
SUFFIX="_${SUFFIX#_}"
DIR=${3}
USE_LOG=1
if [ $# = 4 ];then USE_LOG=$4;fi
HEATMAP='./scripts/apply_heatmap.py'

function check() {
    test -f $1 || {
        echo "ERROR: cannot access $1"
        exit 1
    }
}

##./scripts/apply_heatmap.py orig.png raw_heatmap.txt output.png [0|1] (0: escuro, 1: claro)
while read IMG _;do
    IMG=${IMG##*/}
    SOURCE="$DIR/${IMG}_as_inputted_into_the_dnn.png"
    RAW="$DIR/${IMG}_rawhm.txt"
    TARGET="$DIR/${IMG}${SUFFIX}"
    check $SOURCE
    check $RAW

    echo "$IMG -> $TARGET"
    $HEATMAP $SOURCE $RAW $TARGET $USE_LOG
done < "$LIST"
