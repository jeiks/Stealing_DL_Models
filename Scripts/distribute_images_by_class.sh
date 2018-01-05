#!/bin/bash
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

[ $# -lt 1 ] && {
    echo "Use: $0 file1.txt [file2.txt ... fileN.txt]"
    echo -e "\nFile example:\n\timg.jpg\t0\n\t...\n\taij.jpg\t6"
    exit 0
}

MAX_IMAGES=$(awk '{classes[$NF]++;}END{min=classes[0];for (i=1;i<=6;i++) if (classes[i] < min) min = classes[i];print min;}' $@)
echo "Max images by class: $MAX_IMAGES" >&2

N=$(awk '{print $NF}' $@ | sort -n | tail -n1)

for ((i=0;i<=$N;i++));do
    grep -h "[[:space:]]${i}$" $@ | shuf | head -n $MAX_IMAGES
done | shuf
