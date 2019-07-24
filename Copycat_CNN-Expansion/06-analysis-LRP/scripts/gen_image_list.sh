#!/bin/bash -e

if [ $# -eq 1 ];then
    ######Generating outputs for Original and Copycat models...
    test -f "$1" || { echo "ERROR: cannot access '$1'";exit 1; }
    TD=$1
    LABEL="$HD/Scripts/label_dataset_from_image_list.py"

    #cleaning...
    rm -rf images images.txt images-with-labels.txt
    GPU=${GPU:=0}
    rm -f TD_original.txt TD_copycat.txt
    $LABEL -m deploy.prototxt -f $TD -w original.caffemodel -b 120 -o TD_original.txt -g $GPU -i train.mean 2> log
    $LABEL -m deploy.prototxt -f $TD -w  copycat.caffemodel -b 120 -o  TD_copycat.txt -g $GPU 2> log
fi

#joining results...
paste TD_original.txt TD_copycat.txt | awk '{if ($1 == $4) print $1" "$2" "$3" "$NF}' > TD-join.txt
##output: [img_fn  y  ŷ_orig  ŷ_copycat]

#selecting N images from each case (and completing 3*N with random images):
#cc=correct correct
#wc=wrong correct
#cw=correct wrong
N_IMAGES=${N_IMAGES:=100}
echo "Selecting $(($N_IMAGES*3)) images..."
shuf TD-join.txt | awk '
    BEGIN{
        N='$N_IMAGES';
        found_cc=N;found_wc=N;found_cw=N;
        MAX=N*3;pos=0;
    }{
        if ( ($2 == $3) && ($2 == $4) && (found_cc != 0) )
        {
            print
            found_cc--;
            MAX--;
        }else if ( ($2 != $3) && ($2 == $4) && (found_wc != 0)){
            print
            found_wc--;
            MAX--;
        }else if ( ($2 == $3) && ($2 != $4) && (found_cw != 0)){
            print
            found_cw--;
            MAX--;
        }else{
            img_list[pos] = $0;
            pos++
        }
    }END{
        for (i=0;i<pos && i < MAX;i++)
            print img_list[i];
    }
' > images-with-labels.txt

#copying images...
mkdir -p images
while read IMG _;do
    if [ "${IMG:0:1}" != '/' ];then
        IMG=$PWD/$IMG
    fi
    ln -sf $IMG images/${IMG##*/}
done < images-with-labels.txt
#creating images.txt to LRP...
find images -type l -exec echo ${PWD##*/}/{} -1 \; > images.txt
