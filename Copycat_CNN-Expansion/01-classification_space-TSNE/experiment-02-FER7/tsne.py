#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial.distance import pdist
from matplotlib.ticker import NullFormatter
from sklearn import manifold, datasets
from time import time

from sys import exit, argv, stdout

def read_file(fn):
    #row's format: [name class dimensions...]
    dimensions = len(open(fn).readline().split()) - 2
    data = np.genfromtxt(fn, dtype=['S80', np.int]+[np.float for x in range(dimensions)])

    X = np.array([data['f%d'%i] for i in range(2,dimensions+2)]).T
    y = np.array(data['f1'])
    return X, y

def preprocess(X):
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    return scaler.fit_transform(X)

def run_tsne(X,n_components=2, perplexity=30, n_iter=5000, learning_rate=200.0, verbose=1):
    print('Running T-SNE...')
    tsne = manifold.TSNE(n_components=n_components, perplexity=perplexity, verbose=1, n_iter=5000, learning_rate=100)
    t0 = time()
    Y = tsne.fit_transform(X)
    t1 = time()
    return Y, t1-t0

def plot_points(Y, y, colors, markers, perplexity, t):
    print('Plotting...')
    plt.title("FER (Perplexity=%d, time: %.2g sec)" % (perplexity, t))
    N = len(colors)
    p = [None for i in range(N)]
    for i in range(N//2):
        if np.array(y == i, dtype=int).sum() > 0:
            p[i]  = plt.scatter(Y[y==i, 0], Y[y==i, 1], c='%s95'%colors[i], marker=markers[0])
        i2 = i+N//2
        if np.array(y == i2, dtype=int).sum() > 0:
            p[i2] = plt.scatter(Y[y==i2, 0], Y[y==i2, 1], c=colors[i2], marker=markers[1])

    l = np.array([[str('ODD:%d'%x),str('NPDD:%d'%(x))] for x in range(N//2)])
    plt.legend( l.reshape(N) )
    plt.axis('tight')

    plt.show()


def count_num_classes(y):
    num = set(y)
    return len(num), num

def select_n_closer_points(origin, to_select, n_to_select, c):
    used_points = []
    count = 0
    for j in origin:
        stdout.write('%03d: ' % count)
        count+=1
        #aux <- distance between X_npd[y_npd==i] and j:
        aux = np.array([[x,float(pdist([x,j]))] for x in to_select])
        s = aux[:,1].argsort()
        aux = aux[s,0]
        aux = np.array([x for x in aux if list(x) not in used_points])
        aux = aux[:n_to_select]
        for x in aux:
            used_points.append(list(x))
            stdout.write('.')
            stdout.flush()
        stdout.write('\r')
        stdout.flush()
    print('')
    ret = np.array(used_points)
    #ret = np.unique( ret, axis=0 )
    return ret

def join_datasets(X_od, y_od, X_npd, y_npd, n_od=100, n_npd=3):
    #getting classes information:
    n_classes, classes = count_num_classes(y_od)
    #selecting n_orig random samples from each class of X1:
    #and calculating the means:
    new_X = np.zeros([n_od*n_classes, X_od.shape[-1]])
    new_y = np.zeros([n_od*n_classes], dtype=np.int)
    new_X_npd = []
    new_y_npd = []
    for i in classes:
        print('Class: %d'%i)
        #shuffling n_od samples:
        r = np.random.permutation(len(y_od[y_od==i]))[:n_od]
        new_X[i*n_od:i*n_od+n_od, ...] = X_od[y_od==i][r]
        new_y[i*n_od:i*n_od+n_od] = y_od[y_od==i][r]
        
        aux = select_n_closer_points(X_od[y_od==i][r], X_npd[y_npd==i], n_npd, i)
        for x in aux:
            new_X_npd.append(x)
            new_y_npd.append(i+n_classes)

    X = np.vstack([new_X, new_X_npd])
    y = np.hstack([new_y, new_y_npd])
    return X,y
    

if __name__ == "__main__":
    if len(argv) != 3:
        print('Use: {} FILE_OD FILE_NPD'.format(argv[0]))
        exit(1)

    filenames = [argv[1], argv[2]]
    perplexity = 30

    markers = ['.', 'x']
    colors = [
              '#ec5bea', '#dddf1e', '#06c606', '#62696e', '#e71f24',
              '#5054fd', '#87f587',
              '#bf00bf', '#bfbf00', '#008000', '#000000', '#a80b0f',
              '#0000ff', '#00ff00'
            ]

    print('Reading files...')
    X1, y1 = read_file(filenames[0])
    print('  "{}".. ok'.format(filenames[0]))
    X2, y2 = read_file(filenames[1])
    print('  "{}".. ok'.format(filenames[1]))
    X1 = preprocess(X1)
    X2 = preprocess(X2)
    X, y = join_datasets(X1, y1, X2, y2)
    del X1, y1, X2, y2
    print('Shape:\n\tX:{}\n\ty:{}'.format(X.shape, y.shape))
    
    Y, t = run_tsne(X,perplexity=perplexity)
    plot_points(Y,y,colors, markers, perplexity, t)
