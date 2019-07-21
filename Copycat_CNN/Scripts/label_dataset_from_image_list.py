#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

from sys import argv, exit, stdout
import getopt
import caffe, lmdb
import numpy as np

opts, _ = getopt.getopt(argv[1:], 'm:f:w:i:s:b:o:g:t:h')
opts = dict(opts)


def getOpt(opt):
    global opts
    if opts.has_key(opt): return opts[opt]
    else: return ''


def checkPaths(imageList, model, weights, meanFile, outFile):
    from os.path import isdir, isfile
    for i in [[isfile(imageList), imageList], [isfile(model), model],
              [isfile(weights), weights], [isfile(meanFile),meanFile]]:
        if not i[0]:
            print("\nERROR: cannot access '{}'. Please check it.".format(i[1]))
            exit(1)
    if isfile(outFile):
        print("\nERROR: Output file '{}' already exists. Remove it to continue.".format(outFile))
        exit(2)


def getAllArgs():
    model     = getOpt('-m')
    imageList = getOpt('-f')
    weights   = getOpt('-w')
    meanFile  = getOpt('-i')
    batchSize = getOpt('-b')
    outFile   = getOpt('-o')
    gpuNumber = getOpt('-g')
    #modelType = getOpt('-t')

    if opts.has_key('-h') or ('' in [imageList, weights, meanFile, batchSize]):
        print('Use: {} \t\\'.format(argv[0]))
        print('\t-m model           \t\\')
        print('\t-f image_list_file \t\\')
        print('\t-w weights_file    \t\\')
        print('\t-i image_mean_file \t\\')
        print('\t-b batch_size      \t\\')
        print('\t[-o output_file]   \t\\')
        print('\t[-g gpu_number]    \t\\')
        #print('\t[-t facial|cifar] (default: facial)')
        exit(0)

    

    outFile   = 'results.txt' if outFile == '' else outFile
    checkPaths(imageList, model, weights, meanFile, outFile)
    #modelType = 'facial' if (modelType == '' or modelType == 'facial') else 'cifar'
    gpuNumber = 0 if gpuNumber == '' else int(gpuNumber)
    batchSize = int(batchSize)

    return model, imageList, weights, meanFile, batchSize, gpuNumber, outFile #, modelType


def getInput(image_info, transformer):
    f = image_info.split()[0]
    img = caffe.io.load_image(f)
    return {'input': transformer.preprocess('data', img), 'label': int(image_info.split()[1])}


def openCaffeMean(meanFile):
    data = open(meanFile, 'rb').read()
    blob = caffe.proto.caffe_pb2.BlobProto()
    blob.ParseFromString(data)
    mean = caffe.io.blobproto_to_array(blob)
    return mean


# Se checkTrust estiver habilitado, os valores do softmax com diferença
# menor que "margin" serão retornados com valor negativo
def netForward(net, batch, labels, batchSize, datasetShape, checkTrust=False):
    #if modelType == 'facial':
    #    net.blobs['data'].reshape(batchSize, 3, 224, 224)
    #else:
    #    net.blobs['data'].reshape(batchSize, 3, 32, 32)
    net.blobs['data'].reshape(batchSize, datasetShape[0], datasetShape[1], datasetShape[2])
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


def saveToFile(images_processed, results, outFile):
    f = open(outFile,'a')
    for i in range(len(images_processed)):
        f.write('{} {} {}\n'.format(images_processed[i].split()[0], results[i][0], results[i][1]))
    f.close()
    #print("Labels stored at `{}'".format(outFile))

def writeAccuracy(count, dataSize, correct, wrong):
    stdout.write('\r({}/{}) Correct: {} Wrong: {} '.format(count, dataSize, correct, wrong))
    stdout.flush()
    
if __name__ == '__main__':
    #model, imageList, weights, meanFile, batchSize, gpuNumber, outFile, modelType = getAllArgs()
    model, imageList, weights, meanFile, batchSize, gpuNumber, outFile = getAllArgs()

    print('Loading the network model...')
    caffe.set_mode_gpu()
    caffe.set_device(gpuNumber)
    net = caffe.Net(model, weights, caffe.TEST)

    print('Loading images file...')
    images_listing = open(imageList).readlines()

    print('Loading mean file...')
    try:
        mean = openCaffeMean(meanFile)
    except:
        print("ERROR: cannot load Mean File ('{}').".format(meanFile))
        exit(3)

    #if mean.shape == (224,224,3) or mean.shape == (32,32,3):
    #    mean = mean.transpose(2,0,1)
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_mean('data', mean[0])
    transformer.set_transpose('data', (2, 0, 1))
    transformer.set_channel_swap('data', (2, 1, 0))
    transformer.set_raw_scale('data', 255.0)

    datasetShape = mean.shape[1:]

    print('Testing data...')
    dataSize = len(images_listing)
    RESULTS  = np.zeros( (dataSize,2), dtype=int )

    # Counters:
    count      = 0
    correct    = 0
    wrong      = 0
    cannotOpen = 0
    # Net Inputs and Outputs:
    #if modelType == 'facial':
    #    batch = np.zeros((batchSize,3,224,224))
    #else:
    #    batch = np.zeros((batchSize,3,32,32))
    batch = np.zeros((batchSize, datasetShape[0], datasetShape[1], datasetShape[2]))
    labels = np.zeros((batchSize))
    images_processed = []
    for image_info in images_listing:
        try:
            data = getInput(image_info, transformer)
            images_processed.append(image_info)
            batch[count%batchSize]  = data['input']
            labels[count%batchSize] = data['label']
            del data
            count += 1
            if count % batchSize == 0:
                bCorrect, bWrong, outputs = netForward(net, batch, labels, batchSize, datasetShape)
                correct += bCorrect
                wrong   += bWrong
                writeAccuracy(count, dataSize-cannotOpen, correct, wrong)
                RESULTS[(count-batchSize):count] = np.concatenate( (labels, outputs) ).reshape(2,batchSize).transpose()
                saveToFile(images_processed[(count-batchSize):count], RESULTS[(count-batchSize):count], outFile)
        except:
            cannotOpen += 1
            if cannotOpen > 100:
                print "Be careful, there is a lot of images that couldn't be open."

    if count % batchSize != 0:
        batchSize = count % batchSize
        batch  = batch[:batchSize]
        labels = labels[:batchSize]
        bCorrect, bWrong, outputs = netForward(net, batch, labels, batchSize, datasetShape)
        correct += bCorrect
        wrong   += bWrong
        writeAccuracy(count,dataSize-cannotOpen,correct,wrong)
        RESULTS[(count-batchSize):count] = np.concatenate((labels, outputs)).reshape(2, batchSize).transpose()
        saveToFile(images_processed[(count-batchSize):count], RESULTS[(count-batchSize):count], outFile)
    else:
        writeAccuracy(count,dataSize-cannotOpen,correct,wrong)

    print('\nAccuracy: %.6f (%d images)' % (float(correct) / (dataSize-cannotOpen), dataSize-cannotOpen))
    #np.savetxt(outFile, RESULTS, fmt='%d')
    
