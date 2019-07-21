#!/bin/bash
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

[ $# -ne 1 ] && {
    echo "Use: $0 log_file.txt"
    exit 0
}

awk 'BEGIN { epoch=0; loss=0;}
{
    if ($(NF-1) == "=")
        if ($(NF-2) == "accuracy")
        {
            printf("Accuracy = %.6f (%d epoch)\n", $NF, epoch);
            epoch++;
            loss=0;
        }
        else if ($(NF-2) == "loss")
        {
            if (epoch == 0) epoch++;
            printf("  (%03d) Loss = %.8f\n", loss, $NF);
            loss++;
        }
}
END{ print "Runned epochs: "(epoch-1); }' $1
