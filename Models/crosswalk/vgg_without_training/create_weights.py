#!/usr/bin/env python2

import caffe
caffe.set_mode_gpu()
caffe.set_device(1)
net = caffe.Net('vgg_crosswalk.prototxt', 'VGG_ILSVRC_16_layers.caffemodel', caffe.TRAIN)
net.save('weights.caffemodel')
