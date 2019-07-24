#!/bin/bash

D=$PWD
for i in [[:upper:]]*;do
    LOCK="${i,,}.lock"
    if mkdir "$LOCK";then
        cd $i
        for v in *.avi;do
            DO=$PWD
            DD=${v%.*}
            mkdir $DD
            cd $DD
            pwd
            mplayer -ao null -vo jpeg ../$v
            cd $DO
        done
        cd $D
   fi
done
