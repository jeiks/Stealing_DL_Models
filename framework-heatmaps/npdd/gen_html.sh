#!/bin/bash

HEADER="<html><title>PROBLEM</title><script src='./heatmaps.js'></script><link rel='stylesheet' href='./heatmaps.css'><body>"
FOOTER="</body></html>"
for P in ???;do
    echo ${HEADER/PROBLEM/$P} > $P.html
    for IMG in $P/*.jpg;do
        echo "<div><img src='$IMG' onclick=\"window.open('$IMG')\" ></div>"
    done >> $P.html
    echo $FOOTER >> $P.html
done
