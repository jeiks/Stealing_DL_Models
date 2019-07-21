#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

from sys import argv, exit, stdout
import getopt
import caffe, lmdb
import numpy as np
from sklearn.metrics import f1_score

opts, _ = getopt.getopt(argv[1:], 'm:l:w:i:s:b:o:g:t:c:h')
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
    confMat   = getOpt('-c')

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
        print('\t[-c 0|1] (conf. mat. - default: 0)')
        exit(0)

    checkPaths(lmdbPath, model, weights, meanFile)

    gpuNumber = 0 if gpuNumber == '' else int(gpuNumber)
    modelType = 'facial' if (modelType == '' or modelType == 'facial') else 'cifar'
    confMat   = True if confMat == '1' else False
    batchSize = int(batchSize)

    return model, lmdbPath, weights, meanFile, batchSize, gpuNumber, outFile, modelType, confMat


def getInput(datum, value, mean, modelType, datasetShape):
    datum.ParseFromString(value)
    data = caffe.io.datum_to_array(datum) - mean
    return {'input': data.reshape(1,datasetShape[0],datasetShape[1],datasetShape[2]), 'label': datum.label}


def openCaffeMean(meanFile):
    data = open(meanFile, 'rb').read()
    blob = caffe.proto.caffe_pb2.BlobProto()
    blob.ParseFromString(data)
    mean = caffe.io.blobproto_to_array(blob)
    return mean


def netForward(net, batch, labels, batchSize, modelType, datasetShape):
    net.blobs['data'].reshape(batchSize,datasetShape[0],datasetShape[1],datasetShape[2])
    net.blobs['data'].data[...] = batch
    output  = net.forward()
    correct = np.sum(output['loss'].argmax(axis=1) == labels)
    wrong   = batchSize - correct
    return correct, wrong, output['loss'].argmax(axis=1)


def printConfMat(RESULTS):
    nClasses = np.max(RESULTS)+1
    cm = np.zeros((nClasses,nClasses))
    for i,j in RESULTS: cm[i,j]+=1
    stdout.write('Confusion Matrix:\n')
    stdout.write('   ')
    for i in range(nClasses): stdout.write('%9d' % i)
    stdout.write('\n')
    for i in range(nClasses):
        stdout.write('%2d: '%i)
        for j in range(nClasses):
            stdout.write('%8d ' % cm[i,j])
        stdout.write('\n')


if __name__ == '__main__':
    model, lmdbPath, weights, meanFile, batchSize, gpuNumber, outFile, modelType, confMat = getAllArgs()
    
    #print('Loading...')
    #print('Loading the network model...')
    caffe.set_mode_gpu()
    caffe.set_device(gpuNumber)
    net = caffe.Net(model, weights, caffe.TEST)

    #print('Loading lmdb file...')
    lmdb_env = lmdb.open(lmdbPath)
    lmdb_txn = lmdb_env.begin()
    lmdb_cursor = lmdb_txn.cursor()
    datum = caffe.proto.caffe_pb2.Datum()

    #print('Loading mean file...')
    try:
        mean = openCaffeMean(meanFile)
    except:
        print("ERROR: cannot load Mean File ('{}').".format(meanFile))
        exit(2)

    if mean.shape[-1] == 3:
        mean = mean.transpose(2,0,1)

    datasetShape = mean.shape[1:]

    #print('Testing data...')
    dataSize = lmdb_env.stat()['entries']
    RESULTS  = np.zeros( (dataSize,2), dtype=int )

    # Counters:
    count   = 0
    correct = 0
    wrong   = 0
    # Net Inputs and Outputs:
    batch = np.zeros((batchSize,datasetShape[0],datasetShape[1],datasetShape[2]))
    labels = np.zeros((batchSize))
    for key, value in lmdb_cursor:
        data = getInput(datum, value, mean, modelType, datasetShape)
        batch[count%batchSize]  = data['input']
        labels[count%batchSize] = data['label']
        del data
        count += 1
        if count % batchSize == 0:
            bCorrect, bWrong, outputs = netForward(net, batch, labels, batchSize, modelType, datasetShape)
            correct += bCorrect
            wrong   += bWrong
            stdout.write('\r({}/{}) Correct: {} Wrong: {} '.format(count, dataSize, correct, wrong))
            stdout.flush()
            RESULTS[(count-batchSize):count] = np.concatenate( (labels, outputs) ).reshape(2,batchSize).transpose()

    if count % batchSize != 0:
        batchSize = count % batchSize
        batch  = batch[:batchSize]
        labels = labels[:batchSize]
        bCorrect, bWrong, outputs = netForward(net, batch, labels, batchSize, modelType, datasetShape)
        correct += bCorrect
        wrong   += bWrong
        stdout.write('\r({}/{}) Correct: {} Wrong: {} '.format(count, dataSize, correct, wrong))
        stdout.flush()
        RESULTS[(count - batchSize):count] = np.concatenate((labels, outputs)).reshape(2, batchSize).transpose()

    micro_avg = f1_score(RESULTS[:,0], RESULTS[:,1], average='micro')
    macro_avg = f1_score(RESULTS[:, 0], RESULTS[:, 1], average='macro')
    print(('\nAverage: %.6f (%d images)' % (float(correct) / dataSize, dataSize)).replace('.',','))
    print(('Micro Average: %.6f' % micro_avg).replace('.',','))
    print(('Macro Average: %.6f' % macro_avg).replace('.',','))
    if confMat:
        printConfMat(RESULTS)

    if outFile != '':
        f = open(outFile,'w')
        f.write('Total Average: {}\n'.format(float(correct) / dataSize, '.6f'))
        f.write('Micro Average: {}\n'.format(micro_avg,'.6f'))
        f.write('Macro Average: {}\n'.format(macro_avg,'.6f'))
        f.close()
