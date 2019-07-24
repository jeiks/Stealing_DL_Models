#!/bin/bash

[ $# -lt 2 ] && {
    echo "Use: $0 N_INSTANCES_BY_CLASS FILE1 [FILE2 FILE3 ...] > output_file.txt"
    exit 1
}

N=$1
shift
FILES=$@

cat $FILES | shuf | awk '
BEGIN{
N = '$N';
for (i=0;i<=150;i++)
    imgs[i] = N;
}
{
    if (imgs[$2] > 0)
    {
        imgs[$2]--;
        print
    }
}'
