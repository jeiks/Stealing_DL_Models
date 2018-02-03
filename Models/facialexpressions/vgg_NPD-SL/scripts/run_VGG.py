#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

from sys import argv, exit
import getopt

opts, _ = getopt.getopt(argv[1:], 'l:m:w:n:i:hr')
opts = dict(opts)

if opts.has_key('-h'):
    print('Use: {} -l lmdb_dir -m network_model -w weights_file -i image_mean_file [-n test_size]'.format(argv[0]))
    exit(0)

def getOpt(opt):
    global opts
    if opts.has_key(opt): return opts[opt]
    else: return ''


lmdbPath  = getOpt('-l')
model     = getOpt('-m')
weights   = getOpt('-w')
meanFile = getOpt('-i')

testSize = getOpt('-n')
testSize = 0 if testSize == '' else int(testSize)

if lmdbPath  == '': lmdbPath  = raw_input('LMDB Directory: ')
if model     == '': model     = raw_input('Network Model File: ')
if weights   == '': weights   = raw_input('Network Weights File: ')
if meanFile == '': meanFile = raw_input('Image Mean file: ')

def checkPaths(lmdb, model, weights, meanFile):
    from os.path import isdir, isfile
    if not isdir(lmdb) or not isfile(model) or not isfile(weights) or not isfile(meanFile):
        print('\nERROR: cannot access all files. Please check them:')
        print('LMDB Directory: {}\nModel File: {}\nWeights File: {}\nImage Mean File:{}'.format(
               lmdb, model, weights, meanFile))
        exit(1)
    
checkPaths(lmdbPath, model, weights)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

import caffe, lmdb
import numpy as np

def getInput(datum, value, mean):
    datum.ParseFromString(value)
    data = caffe.io.datum_to_array(datum) - mean
    return {'input': data.reshape(1,3,224,224), 'label': datum.label}

#lmdbPath = '../data/test_lmdb/'
#model    = 'prototxt/deploy.prototxt'
#weights  = 'acc_0.850-loss_0.00008.caffemodel'

print('Loading the network model...')
caffe.set_mode_gpu()
caffe.set_device(1)
net = caffe.Net(model, weights, caffe.TEST)
print('Loading lmdb file...')
lmdb_env = lmdb.open(lmdbPath)
lmdb_txn = lmdb_env.begin()
lmdb_cursor = lmdb_txn.cursor()
datum = caffe.proto.caffe_pb2.Datum()
print('Loading mean file...')
if meanFile.split('.')[-1] == 'png':
    from scipy import misc
    mean = misc.imread(meanFile)
elif meanFile.split('.')[-1] == 'npy':
    mean = np.load(meanFile)
if mean.shape == (224,224,3):
    mean = mean.transpose(2,0,1)
print('Testing data...')
if testSize == 0:
    testSize = lmdb_env.stat()['entries']

count = 0
if testSize == 1:
    from random import randint
    R = randint(0, lmdb_env.stat()['entries'])
    for key, value in lmdb_cursor:
        count += 1
        if count == R: break
    data = getInput(datum, value, mean)
    net.blobs['data'].data[...] = data['input']
    output = net.forward()
    output = output['loss'].argmax()
    print('Desired Answer: {} '.format(data['label']) +
          '     Estimated: {} '.format(output) )
else:
    import numpy
    #Falta verificar as imagens que ficaram foram do batch
    #Ex.: 123 % 10 -> 12 batchs e faltam 3 imagens
    RESULTS = numpy.zeros((testSize,2), dtype=int)
    correct = 0
    wrong = 0
    step = 100
    net.blobs['data'].reshape(step,3,224,224)
    batch = np.zeros((step,3,224,224))
    labels = np.zeros((step))
    for key, value in lmdb_cursor:
        data = getInput(datum, value, mean)
        batch[count%step]  = data['input']
        labels[count%step] = data['label']
        del data
        count += 1
        if count % step == 0:
            net.blobs['data'].data[...] = batch
            output = net.forward()
            aux = np.sum(output['loss'].argmax(axis=1) == labels)
            correct += aux
            wrong += 100 - aux
            print('Correct: {} Wrong: {}'.format(correct, wrong))
            RESULTS[(count-step):count] = numpy.concatenate( (labels, output['loss'].argmax(axis=1)) ).reshape(2,step).transpose()
        if count == testSize: break
    print('Accuracy: %.2f' % (correct / (correct+wrong)))
    numpy.savetxt('results.txt', RESULTS, fmt='%d')
# Th values that are tested by Net are in: net.blobs['data'].data
# net.blobs['data'].data.shape -> (1,3,224,224)
#                                  1 to run with one image 
    
#datum.ParseFromString(value)
#data = caffe.io.datum_to_array(datum)
#data = data.reshape(1,3,224,224)
#label = datum.label

#net.blobs['data'].data[...] = data
#output = net.forward()
#print('Desired Answer: {} '.format(label) +
      #'     Estimated: {} '.format(output['loss'].argmax()) )
