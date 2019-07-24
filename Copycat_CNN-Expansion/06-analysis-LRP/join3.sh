#!/bin/bash

[ $# -ne 4 ] && {
    echo "Use: $0 image1 image2 image3 output_prefix"
    exit 0
}

SIZE=($(identify $1 | awk '{print $3}' | tr x \ ))
convert $1 $2 $3 +append -depth 16                                              \
    -stroke white -draw "line ${SIZE[0]},0 ${SIZE[0]},${SIZE[1]}"               \
    -stroke white -draw "line $((${SIZE[0]}*2)),0 $((${SIZE[0]}*2)),${SIZE[1]}" \
    $4.png
#convert $1 $2 $3 -append -depth 16 $4-2.png
