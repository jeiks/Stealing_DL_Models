#!/usr/bin/env python2

from sys import argv, exit

if len(argv) != 3:
    print('Use: {} classInd.txt file.txt'.format(argv[0]))
    exit(1)

pat = dict( [[i.split()[1], i.split()[0]] for i in open(argv[1]).readlines()] )
f = [i.replace('\n','') for i in open(argv[2]).readlines()]

for i in f:
    try:
        num = pat[i.split('/')[1]]
    except:
        num = pat[i.split('/')[2]]
    num = int(num) - 1
    print('{} {}'.format(i, num))
