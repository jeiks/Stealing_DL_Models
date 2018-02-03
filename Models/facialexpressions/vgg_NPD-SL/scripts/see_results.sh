#!/bin/bash

[ $# -lt 1 ] && {
    echo "Use: $0 log_file [plot]"
    exit 1
}

awk '
{
    if ($(NF-1) == "=")
    {
        if ($(NF-2) == "accuracy")
            printf("Accuracy = %.5f ", $NF);
        else if ( $(NF-2) == "loss")
            printf("Loss = %.7f\n", $NF);
    }
    if ( $NF == "(#0)" && $(NF-1) == "net" && $(NF-2) == "Testing")
            printf("Iteration %s ", $(NF-3));
}' $1 | tee .results

[ -n "$2" ] && \
    echo "plot '.results' using 5 with lines title 'Accuracy', \
               '.results' using 8 with lines title 'Loss';
         set grid;" | gnuplot -persist
