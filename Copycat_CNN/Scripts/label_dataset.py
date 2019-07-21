#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

from sys import argv, exit, stdout
import getopt
import caffe, lmdb
import numpy as np

opts, _ = getopt.getopt(argv[1:], 'm:l:w:i:s:b:o:g:t:h')
opts = dict(opts)


def getOpt(opt):
    global opts
    if opts.has_key(opt): return opts[opt]
    else: return ''


def checkPaths(lmdb, model, weights, meanFile):
    from os.path import isdir, isfile
    for i in [[isdir(lmdb),lmdb], [isfile(model),model],
              [isfile(weights), weights], [isfile(meanFile),meanFile]]:
        if not i[0]:
            print("\nERROR: cannot access '{}'. Please check it.".format(i[1]))
            exit(1)


def getAllArgs():
    model     = getOpt('-m')
    lmdbPath  = getOpt('-l')
    weights   = getOpt('-w')
    meanFile  = getOpt('-i')
    batchSize = getOpt('-b')
    outFile   = getOpt('-o')
    gpuNumber = getOpt('-g')
    modelType = getOpt('-t')

    if opts.has_key('-h') or ('' in [lmdbPath, weights, meanFile, batchSize]):
        print('Use: {} \t\\'.format(argv[0]))
        print('\t-m model\t\\')
        print('\t-l lmdb_dir \t\t\\')
        print('\t-w weights_file \t\\')
        print('\t-i image_mean_file \t\\')
        print('\t-b batch_size \t\t\\')
        print('\t[-o output_file]')
        print('\t[-g gpu_number]')
        print('\t[-t facial|cifar] (default: facial)')
        exit(0)

    checkPaths(lmdbPath, model, weights, meanFile)

    outFile   = 'results.txt' if outFile == '' else outFile
    modelType = 'facial' if (modelType == '' or modelType == 'facial') else 'cifar'
    gpuNumber = 0 if gpuNumber == '' else int(gpuNumber)
    batchSize = int(batchSize)

    return model, lmdbPath, weights, meanFile, batchSize, gpuNumber, outFile, modelType


def getInput(datum, value, mean):
    datum.ParseFromString(value)
    data = caffe.io.datum_to_array(datum) - mean
    if modelType == 'facial':
        return {'input': data.reshape(1,3,224,224), 'label': datum.label}
    else:
         return {'input': data.reshape(1,3,32,32), 'label': datum.label}


def openCaffeMean(meanFile):
    data = open(meanFile, 'rb').read()
    blob = caffe.proto.caffe_pb2.BlobProto()
    blob.ParseFromString(data)
    mean = caffe.io.blobproto_to_array(blob)
    return mean


# Se checkTrust estiver habilitado, os valores do softmax com diferença
# menor que "margin" serão retornados com valor negativo
def netForward(net, batch, labels, batchSize, checkTrust=False):
    if modelType == 'facial':
        net.blobs['data'].reshape(batchSize, 3, 224, 224)
    else:
        net.blobs['data'].reshape(batchSize, 3, 32, 32)
    net.blobs['data'].data[...] = batch
    net_output  = net.forward()
    # softmax
    e = np.exp(net_output['loss'])
    softmax = (e.transpose() / e.sum(axis=1)).transpose()
    if checkTrust:
        # trusted outputs
        margin = 0.1
        trusted = np.sort(softmax, axis=1)
        trusted = np.array((trusted[:,-1]-margin) > trusted[:,-2], dtype = 'int8')
        #trusted[-1] = False
        #trusted.dtype='int8'
        trusted[trusted == 0] = softmax.shape[1]+1
        trusted[trusted == 1] = 0
        output = softmax.argmax(axis=1) - trusted
    else:
        output = softmax.argmax(axis=1)

    correct = np.sum(output == labels)
    wrong   = batchSize - correct
    return correct, wrong, output


if __name__ == '__main__':
    model, lmdbPath, weights, meanFile, batchSize, gpuNumber, outFile, modelType = getAllArgs()

    print('Loading the network model...')
    caffe.set_mode_gpu()
    caffe.set_device(gpuNumber)
    net = caffe.Net(model, weights, caffe.TEST)

    print('Loading lmdb file...')
    lmdb_env = lmdb.open(lmdbPath)
    lmdb_txn = lmdb_env.begin()
    lmdb_cursor = lmdb_txn.cursor()
    datum = caffe.proto.caffe_pb2.Datum()

    print('Loading mean file...')
    try:
        mean = openCaffeMean(meanFile)
    except:
        print("ERROR: cannot load Mean File ('{}').".format(meanFile))
        exit(2)

    if mean.shape == (224,224,3) or mean.shape == (32,32,3):
        mean = mean.transpose(2,0,1)

    print('Testing data...')
    dataSize = lmdb_env.stat()['entries']
    RESULTS  = np.zeros( (dataSize,2), dtype=int )

    # Counters:
    count   = 0
    correct = 0
    wrong   = 0
    # Net Inputs and Outputs:
    if modelType == 'facial':
        batch = np.zeros((batchSize,3,224,224))
    else:
        batch = np.zeros((batchSize,3,32,32))
    labels = np.zeros((batchSize))
    for key, value in lmdb_cursor:
        data = getInput(datum, value, mean)
        batch[count%batchSize]  = data['input']
        labels[count%batchSize] = data['label']
        del data
        count += 1
        if count % batchSize == 0:
            bCorrect, bWrong, outputs = netForward(net, batch, labels, batchSize)
            correct += bCorrect
            wrong   += bWrong
            stdout.write('\r({}/{}) Correct: {} Wrong: {} '.format(count, dataSize, correct, wrong))
            stdout.flush()
            RESULTS[(count-batchSize):count] = np.concatenate( (labels, outputs) ).reshape(2,batchSize).transpose()

    if count % batchSize != 0:
        batchSize = count % batchSize
        batch  = batch[:batchSize]
        labels = labels[:batchSize]
        bCorrect, bWrong, outputs = netForward(net, batch, labels, batchSize)
        correct += bCorrect
        wrong   += bWrong
        stdout.write('\r({}/{}) Correct: {} Wrong: {} '.format(count, dataSize, correct, wrong))
        stdout.flush()
        RESULTS[(count - batchSize):count] = np.concatenate((labels, outputs)).reshape(2, batchSize).transpose()

    print('\nAccuracy: %.6f (%d images)' % (float(correct) / dataSize, dataSize))
    np.savetxt(outFile, RESULTS, fmt='%d')
    print("Labels stored at `{}'".format(outFile))
