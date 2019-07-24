#!/bin/bash

[ $# -lt 1 ] && {
    echo "Use: $0 FILE1 [FILE2 FILE3 ...]"
    exit 0
}

awk 'BEGIN{total=0;}
          {
             class[$2]++;
             total++;
          }
          END {
            for (i in class)
                printf("%10d (%05.2f%%) for class %s\n", class[i], class[i]/total*100, i);
            printf("Total: %d\n", total);
          }' "$@"
