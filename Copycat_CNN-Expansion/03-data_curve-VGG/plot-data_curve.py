#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from matplotlib import pyplot as plt, rc
from sys import exit
import numpy as np

def plot(problem, legend, x, l, y_target, y_npd, y_npd_pd):
    fig, ax = plt.subplots()
    plt.title(problem)
    # The following 'x' axis was used to plot data with a
    # better view, but visually maintaining the impression
    # of the original distance between dataset sizes.
    x = np.array([-20, 10, 50, 100, 150, 250])
    plt.plot(x, y_target, color='sienna', linestyle='dashed')
    plt.plot(x, y_npd, color='blue', marker='^')
    plt.plot(x, y_npd_pd, color='green', marker='s')
    plt.legend(legend)
    plt.xlim(np.min(x), np.max(x))
    plt.ylim(0, 1.02)
    plt.yticks([0, 0.25, 0.50, 0.75, 1.0])
    plt.grid(True, which="both", ls="--")
    
    ax.set_xticks(x)
    ax.set_xticklabels(l)
    ax.get_xaxis().get_major_formatter().labelOnlyBase = False
    
    plt.savefig('{}.svg'.format(problem))
    #plt.show()

def read_problem(data, row):
    problem = data[row][0].split(": ")[1]
    legend = data[row+1][1:]
    start = row+2
    stop  = start+6
    x = [int(i) for i in data[start:stop, 0]]
    l = ['0k', '100k', '500k', '1M', '1.5M', '3M']
    y_target = [float(i) for i in data[start:stop, 1]]
    y_npd    = [float(i) for i in data[start:stop, 2]]
    y_npd_pd = [float(i) for i in data[start:stop, 3]]

    plot(problem, legend, x, l, y_target, y_npd, y_npd_pd)

if __name__ == '__main__':
    font = {'family' : 'normal',
            'weight' : 'bold',
            'size'   : 12}
    fontfig = {
            'titlesize': 16,
            'titleweight': 'bold'}

    rc('font', **font)
    rc('figure', **fontfig)

    data = np.array([i.replace('\n','').split(',') for i in open('data.csv').readlines()])

    max = data.shape[0]
    i=0
    while i < max:
        if data[i][0].find('Problem:') != -1:
            read_problem(data, i) 
        i+=1

