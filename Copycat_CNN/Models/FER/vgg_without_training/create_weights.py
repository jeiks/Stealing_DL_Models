#!/usr/bin/env python2

import caffe
caffe.set_mode_gpu()
caffe.set_device(1)
net = caffe.Net('facial_vgg.prototxt', 'VGG_FACE.caffemodel', caffe.TRAIN)
net.save('weights.caffemodel')
