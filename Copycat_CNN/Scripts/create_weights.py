#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

from sys import argv, exit

if len(argv) != 3:
    print("Use: {} prototxt caffemodel".format(argv[0]))
    print("\ninfo: New layers must have xavier as 'weight_filler'")
    exit(0)

import caffe
caffe.set_mode_gpu()
caffe.set_device(1)
net = caffe.Net(argv[1], argv[2], caffe.TRAIN)
net.save('weights.caffemodel')
