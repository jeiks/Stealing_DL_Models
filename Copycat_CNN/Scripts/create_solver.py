#!/usr/bin/env python
#-*- coding: utf-8 -*-
#Author: Jacson RC Silva <jacsonrcsilva@gmail.com>

from sys import argv, exit, stderr
import getopt

def help():
    stderr.write("""Use: {} --net train_prototxt_file \\
    [--epochs how_much_epochs]             \\
    [--display display]                    \\
    [--lr learning_rate]                   \\
    [--decay weight_decay]                 \\
    [--stepsize stepsize_porc (ex.: 0.33)] \\
    [--gamma gamma]                        \\
    [--snapshot snapshot_prefix]           \\
    [--cpu 1]                              \\
    [--help|-h]
    \n""".format(argv[0]))
    exit(0)

def getSizeLMDB(filename):
    import lmdb
    try:
        with lmdb.open(filename) as lmdb_env:
            size = lmdb_env.stat()['entries']
    except:
        stderr.write("Error loading `{}'\n".format(filename))
        exit(1)
    return size

def getPrototxt(fn):
    from caffe.proto import caffe_pb2
    import google.protobuf.text_format
    net = caffe_pb2.NetParameter()
    net = google.protobuf.text_format.Merge(str(open(fn, 'r').read()), net)
    return net

def getTrainLMDB(netCaffe):
    for i in netCaffe:
        try:
            if i.include[0].phase == 0:
                return i.data_param.source
        except:
            pass
    print("ERROR: cannot access TRAIN DB file.")
    exit(1)

def getTestLMDB(netCaffe):
    for i in netCaffe:
        try:
            if i.include[0].phase == 1:
                return i.data_param.source
        except:
            pass
    print("ERROR: cannot access TEST DB file.")
    exit(2)

def getTrainBatchSize(netCaffe):
    for i in netCaffe:
        try:
            if i.include[0].phase == 0:
                return i.data_param.batch_size
        except:
            pass
    print("ERROR: cannot get train batch_size.")
    exit(3)

def getTestBatchSize(netCaffe):
    for i in netCaffe:
        try:
            if i.include[0].phase == 1:
                return i.data_param.batch_size
        except:
            pass
    print("ERROR: cannot get test batch_size.")
    exit(3)
    
opts, _ = getopt.getopt(argv[1:], 'h',
        ['net=', 'epochs=', 'lr=', 'decay=', 'stepsize=', 'gamma=',
          'display=', 'snapshot=', 'momentum=', 'cpu=', 'help'])
opts = dict(opts)

def getOpt(opt):
    global opts
    if opts.has_key(opt): return opts[opt]
    else: return ''

if opts.has_key('--help'): help()

net         = getOpt('--net')
epochs      = getOpt('--epochs')
lr          = getOpt('--lr')
decay       = getOpt('--decay')
step_porc   = getOpt('--stepsize')
gamma       = getOpt('--gamma')
display     = getOpt('--display')
momentum    = getOpt('--momentum')
cpu         = getOpt('--cpu')
snapshot_prefix = getOpt('--snapshot')

if net == '': help()

netCaffe = getPrototxt(net)
train_lmdb  = getTrainLMDB(netCaffe.layer)
test_lmdb   = getTestLMDB(netCaffe.layer)
train_batch = getTrainBatchSize(netCaffe.layer)
test_batch  = getTestBatchSize(netCaffe.layer)

trainSize   = getSizeLMDB(train_lmdb)
testSize    = getSizeLMDB(test_lmdb)
train_batch = int(train_batch)
test_batch  = int(test_batch)
epochs      = 5 if epochs == '' else int(epochs)
step_porc   = 1./3 if step_porc == '' else float(step_porc)

test_iter     = int(testSize / test_batch)
test_interval = int(trainSize / train_batch)
display       = 200 if display == '' else int(display)
base_lr       = 0.01 if lr == '' else float(lr)
lr_policy     = "step"
stepsize      = int(epochs * (float(trainSize)/train_batch) * step_porc)
gamma         = 0.1 if gamma == '' else float(gamma)
max_iter      = int(epochs * (float(trainSize)/train_batch))
momentum      = 0.9 if momentum == '' else float(momentum)
weight_decay  = 0.0005 if decay == '' else float(decay)
snapshot      = test_interval
snapshot_prefix = "models/snapshot" if snapshot_prefix=='' else snapshot_prefix
solver_mode   = "GPU" if cpu == '' else "CPU"

if snapshot_prefix.find('/'):
    stderr.write("INFO: You have to create the folder `{}'\n".format(snapshot_prefix.split('/')[0]))

print("""net: "{}"
test_iter: {}
test_interval: {}
display: {}
base_lr: {}
lr_policy: "{}"
stepsize: {}
gamma: {}
max_iter: {}
momentum: {}
weight_decay: {}
snapshot: {}
snapshot_prefix: "{}"
solver_mode: {}""".format(
net,
test_iter,
test_interval,
display,
base_lr,
lr_policy,
stepsize,
gamma,
max_iter,
momentum,
weight_decay,
snapshot,
snapshot_prefix,
solver_mode
))
