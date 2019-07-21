#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

import caffe, lmdb
from os import access, R_OK
from sys import exit, argv
from random import randint
import numpy as np

if len(argv) > 1:
    lmdbPath = argv[1]
else:
    lmdbPath = raw_input('Enter the directory containing mdb: ')

if not access(lmdbPath, R_OK):
    print 'Could not access directory `%s\'' % lmdbPath
    exit(1)

lmdb_env = lmdb.open(lmdbPath)
lmdb_txn = lmdb_env.begin()
lmdb_cursor = lmdb_txn.cursor()
datum = caffe.proto.caffe_pb2.Datum()

R = randint(0, lmdb_env.stat()['entries']) #lmdb_env.max_key_size() )
S = 0
for key, value in lmdb_cursor:
    if S >= R: break
    S += 1

datum.ParseFromString(value)
data = caffe.io.datum_to_array(datum)
L = datum.channels*datum.width*datum.height

print '''\033[0;1m     LMDB Info\033[0m
     Channels: %d
        Width: %d
       Height: %d
   Image Size: %d (%s)

Total Entries: %d
''' % (datum.channels,
       datum.width,
       datum.height,
       len(datum.data),
       'Correct' if len(datum.data) == L else ('Incorrect, must be %d' % L),
       lmdb_env.stat()['entries'])

if len(datum.data) == L:
    resp = raw_input('Do you want to see an example [y|N]? ')
    try:
        if resp.upper()[0] == 'Y':
            from matplotlib import pyplot as plt
            title = 'Example at position {}'.format(R)
            try:    title += ' - Label: {}'.format(datum.label)
            except: pass

            if datum.channels == 3:
                print( 'Data shape: {}'.format(data.shape) )
                image = np.transpose(data, (1,2,0))
                print('Image shape: {}'.format(image.shape))
                plt.imshow( image.reshape((datum.height,datum.width,datum.channels)) )
            else:
                plt.imshow( data.reshape((datum.height,datum.width)) )

            plt.title(title)
            plt.show()
    except:
        pass
