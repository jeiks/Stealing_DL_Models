#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

from sys import argv, exit, stdout
import getopt
import lmdb
import numpy as np
from PIL import Image

opts, _ = getopt.getopt(argv[1:], 'm:f:w:i:s:b:o:g:t:c:h')
opts = dict(opts)

def getNumLines(fileName):
    return sum(1 for line in open(fileName))


def getOpt(opt):
    global opts
    if opts.has_key(opt): return opts[opt]
    else: return ''


def checkPaths(imageList, model, weights, outFile, meanFile):
    from os.path import isdir, isfile
    lf = [[isfile(imageList), imageList], [isfile(model), model], [isfile(weights), weights]]
    if meanFile != '': lf.append([isfile(meanFile), meanFile])
    
    for i in lf:
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
    color     = getOpt('-c')

    if opts.has_key('-h') or ('' in [imageList, weights, batchSize]):
        print('Use: {} \t\\'.format(argv[0]))
        print('\t-m model             \t\\')
        print('\t-f image_list_file   \t\\')
        print('\t-w weights_file      \t\\')
        print('\t-b batch_size        \t\\')
        print('\t[-i image_mean_file] \t\\')
        print('\t[-o output_file]     \t\\')
        print('\t[-c 1 (1 to default/colored, 0 to grayscale]')
        print('\t[-g gpu_number (-1 to use CPU)]')
        exit(0)

    

    outFile   = 'results.txt' if outFile == '' else outFile
    checkPaths(imageList, model, weights, outFile, meanFile)
    gpuNumber = 0 if gpuNumber == '' else int(gpuNumber)
    batchSize = int(batchSize)
    color = False if color is '0' else True

    return model, imageList, weights, meanFile, batchSize, gpuNumber, outFile, color


def getInput(fileHandler, transformer, color=True):
    while True:
        data = fileHandler.readline()
        if not data: break
        image_info = data.split()
        f = image_info[0]
        n_f = len(data.split())
        img = caffe.io.load_image(f, color=color)
        if n_f == 2:
            ret = {
                   'filename': f,
                   'input': transformer.preprocess('data', img),
                   'label': int(image_info[1])
                  }
        else:
            ret = {
                   'filename': f,
                   'input': transformer.preprocess('data', img),
                   'label': -1
                  }
        
        yield ret

def openCaffeMean(meanFile):
    data = open(meanFile, 'rb').read()
    blob = caffe.proto.caffe_pb2.BlobProto()
    blob.ParseFromString(data)
    mean = caffe.io.blobproto_to_array(blob)
    return mean


def netForward(net, batch, labels, batchSize, datasetShape):
    net.blobs['data'].reshape(*batch.shape)
    net.blobs['data'].data[...] = batch
    net_output  = net.forward()
    # softmax
    e = np.exp(net_output['loss'])
    softmax = (e.transpose() / e.sum(axis=1)).transpose()
    output = softmax.argmax(axis=1)

    correct = np.sum(output == labels)
    wrong   = batchSize - correct
    return correct, wrong, output


def saveToFile(images_processed, results, outFile):
    f = open(outFile,'a')
    if results[0][0] == -1:
        for i in range(len(images_processed)):
            f.write('{} {}\n'.format(
                images_processed[i],
                results[i][1]))
    else:
        for i in range(len(images_processed)):
            f.write('{} {} {}\n'.format(
                images_processed[i],
                results[i][0],
                results[i][1]))
    f.close()

def writeAccuracy(count, dataSize, correct, wrong, onlyStatus=False):
    if onlyStatus:
        stdout.write('\r({}/{}) '.format(count, dataSize))
    else:
        stdout.write('\r({}/{}) Correct: {} Wrong: {} '.format(
                     count, dataSize, correct, wrong))
    stdout.flush()
    
if __name__ == '__main__':
    model, imageList, weights, meanFile, batchSize, gpuNumber, outFile, color = getAllArgs()
    
    print('Loading the network model...')
    if gpuNumber == -1:
        import caffe_cpu as caffe
        caffe.set_mode_cpu()
    else:
        import caffe
        caffe.set_device(gpuNumber)
        caffe.set_mode_gpu()
    net = caffe.Net(model, weights, caffe.TEST)

    print('Loading images file...')
    dataSize = getNumLines(imageList)
    imagesFile = open(imageList)

    if meanFile != '':
        print('Loading mean file...')
        try:
            mean = openCaffeMean(meanFile)
        except:
            print("ERROR: cannot load Mean File ('{}').".format(meanFile))
            exit(3)

    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    if meanFile != '':
        if len(mean.shape) == 4:
            transformer.set_mean('data', mean[0])
        else:
            transformer.set_mean('data', mean)
    transformer.set_transpose('data', (2, 0, 1))
    if color:
        transformer.set_channel_swap('data', (2, 1, 0))
    transformer.set_raw_scale('data', 255.0)

    datasetShape = net.blobs['data'].data.shape[1:]
    print('Testing data...')

    # Counters:
    count      = 0
    correct    = 0
    wrong      = 0
    # Net Inputs and Outputs:
    batch = np.zeros(
            (batchSize,datasetShape[0], datasetShape[1], datasetShape[2]))
    labels = np.zeros((batchSize), dtype=int)
    
    images_processed = []
    for data in getInput(imagesFile, transformer, color):
        images_processed.append(data['filename'])
        batch[count%batchSize]  = data['input']
        labels[count%batchSize] = data['label']
        count+=1
        
        if (count % batchSize == 0) and (count != 0):
            bCorrect, bWrong, outputs = \
                netForward(net, batch, labels, batchSize, datasetShape)
            
            correct += bCorrect
            wrong   += bWrong
            writeAccuracy( count, dataSize, correct, wrong,
                           onlyStatus=(labels[0]==-1) )
            
            saveToFile(
                images_processed,
                np.vstack( [labels, outputs] ).transpose(),
                outFile)
            
            images_processed = []


    if count % batchSize != 0:
        del net
        net = caffe.Net(model, weights, caffe.TEST)

        batchSize = count % batchSize
        batch  = batch[:batchSize]
        labels = labels[:batchSize]
        
        bCorrect, bWrong, outputs = \
            netForward(net, batch, labels, batchSize, datasetShape)
        
        correct += bCorrect
        wrong   += bWrong
        writeAccuracy( count, dataSize, correct, wrong,
                       onlyStatus=(labels[0]==-1))
        
        saveToFile(
            images_processed,
            np.vstack( [labels, outputs] ).transpose(),
            outFile)
    else:
        writeAccuracy( count, dataSize, correct, wrong,
                       onlyStatus=(labels[0]==-1) )

    stdout.write('\n')
    if labels[0] != -1:
        stdout.write('Accuracy: %.6f (%d images)\n' % (float(correct)/dataSize, dataSize))
    stdout.flush()
