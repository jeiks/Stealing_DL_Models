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
    outFile   = getOpt('-o')
    gpuNumber = getOpt('-g')
    color     = getOpt('-c')

    if opts.has_key('-h') or ('' in [imageList, weights]):
        print('Use: {} \t\\'.format(argv[0]))
        print('\t-m model             \t\\')
        print('\t-f image_list_file   \t\\')
        print('\t-w weights_file      \t\\')
        print('\t[-i image_mean_file] \t\\')
        print('\t[-o output_file]     \t\\')
        print('\t[-c 1 (1 to default/colored, 0 to grayscale]')
        print('\t[-g gpu_number (-1 to use CPU)]')
        exit(0)

    

    outFile   = 'results.txt' if outFile == '' else outFile
    checkPaths(imageList, model, weights, outFile, meanFile)
    gpuNumber = 0 if gpuNumber == '' else int(gpuNumber)
    color = False if color is '0' else True

    return model, imageList, weights, meanFile, gpuNumber, outFile, color


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


def netForward(net, batch, which_layer):
    net.blobs['data'].reshape(*batch.shape)
    net.blobs['data'].data[...] = batch
    net_output = net.forward()
    output = np.argmax(net_output['loss'])

    return (net.blobs[which_layer].data, output)



def saveToFile(image_processed, outFile):
    f = open(outFile,'a')
    name = image_processed[0]
    fmap = ' '.join(['0.0' if i == 0.0 else '%.8f'%i for i in image_processed[1][0]])
    output = image_processed[2]
    f.write('{} {} {}\n'.format(name, output, fmap))
    f.close()

def writeAccuracy(count, dataSize, correct, wrong, onlyStatus=False):
    if onlyStatus:
        stdout.write('\r({}/{}) '.format(count, dataSize))
    else:
        stdout.write('\r({}/{}) Correct: {} Wrong: {} '.format(
                     count, dataSize, correct, wrong))
    stdout.flush()
    
if __name__ == '__main__':
    model, imageList, weights, meanFile, gpuNumber, outFile, color = getAllArgs()
    
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

    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    if meanFile != '':
        print('Loading mean file...')
        try:
            mean = openCaffeMean(meanFile)
            transformer.set_mean('data', mean[0] if len(mean.shape) == 4 else mean)
        except:
            print("ERROR: cannot load Mean File ('{}').".format(meanFile))
            exit(3)

    transformer.set_transpose('data', (2, 0, 1))
    if color: transformer.set_channel_swap('data', (2, 1, 0))
    transformer.set_raw_scale('data', 255.0)

    datasetShape = net.blobs['data'].data.shape[1:]
    #which_layer = 'fc8_elq'
    which_layer = 'fc7'
    layer_size  = net.blobs[which_layer].count
    print('Getting outputs from "%s"...' % which_layer)

    # Counters:
    count      = 0
    correct    = 0
    wrong      = 0
    # Net Inputs and Outputs:

    c = ['.','·']
    pos = 0
    count = 0
    print('\nProcessing:')
    for data in getInput(imagesFile, transformer, color):
        img_input = np.array([data['input']])
        feature_map, output = netForward(net, img_input, which_layer)
        image_processed = (data['filename'],  )
        
        saveToFile( (data['filename'], feature_map, output), outFile )

        ### STATUS (I am not freezed..lol)
        stdout.write(c[pos])
        stdout.flush()
        count+=1
        if count % 100 == 0:
            #count = 0
            pos = (pos+1) % 2
            stdout.write('\r {}:'.format(count))
    print('')
