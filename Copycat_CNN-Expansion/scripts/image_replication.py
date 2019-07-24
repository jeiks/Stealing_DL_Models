#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from sys import exit
import numpy as np
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, help='source_file', required=True)
    parser.add_argument('-n', type=int, default=False, required= True,
                              help='target size of dataset (default: rows number in source_file)')
    args = parser.parse_args()

    source_file = args.s
    contents = np.genfromtxt(source_file, usecols=(0,1), dtype=['S80', int])
    filenames = contents['f0']
    classes = contents['f1']
    n_classes = len(np.unique(classes))

    dataset_size = classes.shape[0] if args.n == False else args.n
    max_N = dataset_size // n_classes

    for c in range(n_classes):
        n_batch = np.ceil(max_N / (classes == c).sum())
        aux = filenames[classes == c].copy()
        if n_batch != 0:
            aux = aux.repeat(n_batch)
        np.random.shuffle(aux)
        for i in aux[:max_N]:
            print("{} {}".format(str(i,'utf-8'), c))

if __name__ == '__main__':
    main()
