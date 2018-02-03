#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

from sys import argv, exit, stdout
import getopt

opts, _ = getopt.getopt(argv[1:], 'l:w:i:s:b:o:h')
opts = dict(opts)

def getOpt(opt):
    global opts
    if opts.has_key(opt): return opts[opt]
    else: return ''

model = 'prototxt/deploy.prototxt'

lmdbPath  = getOpt('-l')
weights   = getOpt('-w')
meanFile  = getOpt('-i')
batchSize = getOpt('-b')
outFile   = getOpt('-o')

if opts.has_key('-h') or ('' in [lmdbPath, weights, meanFile, batchSize]):
    print('Use: {} \t\\\n\t-l lmdb_dir \t\t\\\n\t-w weights_file \t\\\n\t-i image_mean_file \t\\\n\t-b batch_size \t\t\\\n\t[-o output_file]'.format(argv[0]))
    print('\nNote:\tthe batch size can uncover some images.')
    print('\tExample: with batch size of 10, we can have 123 % 10 = 3 images out')
    exit(0)

def checkPaths(lmdb, model, weights, meanFile):
    from os.path import isdir, isfile
    if not isdir(lmdb) or not isfile(model) or not isfile(weights) or not isfile(meanFile):
        print('\nERROR: cannot access all files. Please check them:')
        print('LMDB Directory: {}\nGeneric Model File: {}\nWeights File: {}\nImage Mean File:{}'.format(
               lmdb, model, weights, meanFile))
        exit(1)
    
checkPaths(lmdbPath, model, weights, meanFile)

outFile = 'results.txt' if outFile == '' else outFile
batchSize = int(batchSize)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

import caffe, lmdb
import numpy as np
from scipy import misc

def getInput(datum, value, mean):
    datum.ParseFromString(value)
    data = caffe.io.datum_to_array(datum) - mean
    return {'input': data.reshape(1,3,224,224), 'label': datum.label}

def openCaffeMean(meanFile):
    data = open(meanFile, 'rb').read()
    blob = caffe.proto.caffe_pb2.BlobProto()
    blob.ParseFromString(data)
    mean = caffe.io.blobproto_to_array(blob)
    #mean = np.array(mean, dtype=np.uint8)
    return mean

#lmdbPath = '../data/test_lmdb/'
#model    = 'prototxt/deploy.prototxt'
#weights  = 'acc_0.850-loss_0.00008.caffemodel'

print('Loading the network model...')
caffe.set_mode_gpu()
caffe.set_device(0)
net = caffe.Net(model, weights, caffe.TEST)

print('Loading lmdb file...')
lmdb_env = lmdb.open(lmdbPath)
lmdb_txn = lmdb_env.begin()
lmdb_cursor = lmdb_txn.cursor()
datum = caffe.proto.caffe_pb2.Datum()

print('Loading mean file...')
try:
    #if meanFile.split('.')[-1] == 'png':   mean = misc.imread(meanFile)
    #elif meanFile.split('.')[-1] == 'npy': mean = np.load(meanFile)
    #else:
    mean = openCaffeMean(meanFile)
except:
    print("ERRO: cannot load Mean File ('{}').".format(meanFile))
    #print("Please provide a 'png' or 'npy' or caffe's mean file")
    exit(2)

if mean.shape == (224,224,3):
    mean = mean.transpose(2,0,1)

print('Testing data...')
dataSize = lmdb_env.stat()['entries']
testSize = dataSize - (dataSize % batchSize)

RESULTS = np.zeros( (testSize,2), dtype=int )
count = 0
correct = 0
wrong = 0
net.blobs['data'].reshape(batchSize,3,224,224)
batch = np.zeros((batchSize,3,224,224))
labels = np.zeros((batchSize))
for key, value in lmdb_cursor:
    data = getInput(datum, value, mean)
    batch[count%batchSize]  = data['input']
    labels[count%batchSize] = data['label']
    del data
    count += 1
    if count % batchSize == 0:
        net.blobs['data'].data[...] = batch
        output = net.forward()
        aux = np.sum(output['loss'].argmax(axis=1) == labels)
        correct += aux
        wrong += batchSize - aux
        stdout.write('\r({}/{}) Correct: {} Wrong: {}'.format(count, testSize, correct, wrong))
        stdout.flush()
        RESULTS[(count-batchSize):count] = np.concatenate( (labels, output['loss'].argmax(axis=1)) ).reshape(2,batchSize).transpose()

    if count == testSize: break

print('\nAccuracy: %.6f (%d images)' % (float(correct) / testSize, testSize))
np.savetxt(outFile, RESULTS, fmt='%d')
print("Labels stored at `{}'".format(outFile))
