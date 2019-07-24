#!/bin/bash

mv imagenet12 decathlon_imagenet12
mv unlabeled2017 Microsoft_COCO

while read O _ T;do
    install -m644 -D $O $T
    echo $T
done < images.index.txt > images.txt
