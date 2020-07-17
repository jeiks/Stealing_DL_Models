#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from matplotlib import pyplot as plt, rc
from sys import exit, argv
import numpy as np

def plot(problem, legend, x, l, y_npd):
    fig, ax = plt.subplots()
    #plt.title(problem)
    # The following 'x' axis was used to plot data with a
    # better view, but visually maintaining the impression
    # of the original distance between dataset sizes.
    x = np.array([-20, 10, 50, 100, 150, 250])
    ##plt.plot(x, y_target, color='sienna', linestyle='dashed')
    plt.plot(x, y_npd, color='blue', marker='.')#'^')
    plt.legend(legend)
    plt.xlim(np.min(x), np.max(x))
    plt.ylim(y_npd[0], 1.0)
    #plt.yticks([0.16, 0.56, 0.68, 0.90, 0.96])
    plt.yticks(y_npd[:-1])
    ax.set_yticklabels(['{:.1f}%'.format(x*100) for x in y_npd[:-1]])
    plt.grid(True, which="both", ls="--")
    
    ax.set_xticks(x)
    ax.set_xticklabels(l)
    ax.get_xaxis().get_major_formatter().labelOnlyBase = False
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(x)
    #https://azure.microsoft.com/en-us/pricing/details/cognitive-services/face-api/
    prices = [100, 500, 1000, 1400, 2600]
    ax2.set_xticklabels([''                          , #0k
                         '\${:.0f}'.format(prices[0]), #100k
                         '\${:.0f}'.format(prices[1]), #500k
                         '\${:.0f}'.format(prices[2]), #1M
                         '\${:.0f}'.format(prices[3]), #1.5M
                         '\${:.0f}'.format(prices[4])  #3M
                       ])
    
    #plt.savefig('{}.svg'.format(problem))
    plt.show()

def read_problem(data, row):
    problem = data[row][0].split(": ")[1]
    legend = data[row+1][1:]
    start = row+2
    stop  = start+6
    x = []
    y_npd = []
    for i in data[start:stop]:
        x.append(int(i[0]))
        y_npd.append(float(i[1]))
    #x = [int(i) for i in data[start:stop, 0]]
    #y_npd = [float(i) for i in data[start:stop, 1]]
    l = ['0k', '100k', '500k', '1M', '1.5M', '3M']

    plot(problem, legend, x, l, y_npd)

if __name__ == '__main__':
    assert len(argv) == 2, 'Use: {} azure_results.csv'.format(argv[0])
    results_fn = argv[1]

    font = {#'family' : 'DejaVu Sans',
            'family' : 'normal',
            #'weight' : 'bold',
            'size'   : 11}
    fontfig = {'titlesize': 16,
               'titleweight': 'bold'}

    rc('font', **font)
    rc('figure', **fontfig)
    ##rc('text', usetex=True)
    ##rc('text.latex', preamble=r'\usepackage{amsmath}')

    data = np.array([i.replace('\n','').split(',') for i in open(results_fn).readlines()])

    max = data.shape[0]
    i=0
    while i < max:
        if data[i][0].find('Problem:') != -1:
            read_problem(data, i) 
        i+=1

