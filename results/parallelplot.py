# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 19:13:38 2012

@author: jussi
"""

#!/usr/bin/python
from pylab import rcParams
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from math import sqrt
from random import gauss # Jitter

from pprint import pprint

def parallel_coordinates(data_sets, axislabels=None, style=None, lweight=None, labels=None, jitter_sd=None):

    #pprint(data_sets)  
    
    dims = len(data_sets[0])
    x    = range(dims)
    
    #print style
        
    if dims>4:        
        fsize = rcParams['figure.figsize']
        fsize = (fsize[0], fsize[1]*(1.0/(0.1*dims+0.7)))
        fig, axes = plt.subplots(1, dims-1, sharex=False, sharey=False, figsize=fsize)
    else:         
        fig, axes = plt.subplots(1, dims-1, sharex=False, sharey=False)
    
    if style is None:
        style = ['k-']*len(data_sets)
    if lweight is None:
        lweight = [1.0]*len(data_sets)
    #style = ['0.5-']*len(data_sets)
    #lweight = [2.0]*len(data_sets)
    jitter_sd = None
        
    # Calculate the limits on the data
    min_max_range = list()
    for m in zip(*data_sets):
        mn = min(m)
        mx = max(m)
        if mn == mx:
            if mn==0:
                mx = 1
            elif mx==1:
                mn = 0
            else:
                mn -= 0.5
                mx = mn + 1.
        r  = mx - mn
        min_max_range.append((mn, mx, r))

    # Normalize the data sets
    norm_data_sets = list()
    for ds in data_sets:
        nds = []
        for dimension,value in enumerate(ds):
            mn, mx, r = min_max_range[dimension]
            # If jitter is given, add some of it to the value
            if jitter_sd and isinstance(value, (int,long)):
                jitter = r*gauss(0.0, jitter_sd)
                jittered = value - mn + jitter
                nds.append( max(0.0, min(1.0, jittered / float(r) ) ) )
            else:
                nds.append( (value - mn) / float(r) )   
        norm_data_sets.append(nds)        
    data_sets = norm_data_sets
    
    #pprint(norm_data_sets)

    # Plot the datasets on all the subplots
    plotk = []
    plotl = []
    addedLabels = set()
    for i, ax in enumerate(axes):
        for dsi, d in enumerate(data_sets):
            label = None
            addk = False
            if i==len(axes)-1:
                if labels and labels[dsi] not in addedLabels:
                    label = labels[dsi]
                    addedLabels.add(label)
                    addk = True
                #print label
            
            #print x, d, style[dsi], lweight[dsi], label
            k = ax.plot(x, d, style[dsi], linewidth=lweight[dsi], label=label, zorder = 10000)
            
            if addk:
                plotk.append(k[0])
                plotl.append(label)
                
            
        ax.set_xlim([x[i], x[i+1]])
    
    #print axislabels
    if True:
        # Set the x axis ticks 
        # The last axis moves the final axis' ticks to the right-hand side
        allaxes = list(axes)+[plt.twinx(axes[-1])]
        allxxl = [[xx] for xx in x[:-1]] + [[x[-2], x[-1]]]
        
        for dimension, (axx,xxl) in enumerate(zip(allaxes,allxxl)):
            axx.xaxis.set_major_locator(ticker.FixedLocator(xxl))
            #axx.tick_params(labelsize='large')
            ticks = len(axx.get_yticklabels())
            ytlabels = list()
            mn   = min_max_range[dimension][0]
            if isinstance(mn, (int,long)):
                tick_pos = list()
                #print min_max_range[dimension]
                while min_max_range[dimension][2]%ticks!=0:
                    ticks-=1
                step = min_max_range[dimension][2] / max(1, ticks - 1)
                for i in xrange(ticks+1):
                    v = long(mn + long(i*step))
                    ytlabels.append('%d' % v)
                    tick_pos.append(1.0/(ticks)*i)
                #print tick_pos, xlabels
                axx.set_yticks(tick_pos)
                axx.set_yticklabels(ytlabels)
            else:
                step = float(min_max_range[dimension][2]) / (ticks - 1)
                for i in xrange(ticks):
                    v = mn + i*step
                    ytlabels.append('%4.1f' % v)
                axx.set_yticklabels(ytlabels)
            if axislabels:
                if dimension==dims-2:
                    axx.set_xticklabels( (axislabels[dimension],axislabels[dimension+1]) )
                elif dimension!=dims-1:
                    axx.set_xticklabels( (axislabels[dimension],) )
                    
    # Stack the subplots 
    plt.subplots_adjust(wspace=0)
    
    lgd = None
    if labels:
        plt.subplots_adjust(wspace=0, right=0.60)
        #fig.subplots_adjust()
        #print plotl, plotk 
        sortedlabels = zip(plotl, plotk)
        sortedlabels.sort()
        plotl, plotk = zip(*sortedlabels)
        #print plotl, plotk 
        lgd = fig.legend(tuple(plotk), tuple(plotl),loc='center right', bbox_to_anchor=(0.9,0.5))
        #print plotk, plotl
        #lgd = fig.legend(tuple(plotk), tuple(plotl), loc='upper center', bbox_to_anchor=(0.5,-0.1))
        
        
        
        #lgd = fig.legend(tuple(plotk), tuple(plotl), fancybox=True,
        #        loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3,)
        
    return plt, lgd


if __name__ == '__main__':
    import random
    
    base  = [0.0,   0,  5.0,   5,  0]
    scale = [1.5, 0.6, 1.0, 2., 2.]
    line_labels = ["red"]*10
    data = [[type(base[x])(base[x] + random.uniform(0., 1.)*scale[x])
            for x in xrange(5)] for y in xrange(10)]
    colors = ['k--'] * 10

    base  = [3.0,   1,  0.0,   1,  3]
    scale = [1.5, 0.6, 2.5, 2., 2.]
    line_labels.extend(["blue"]*10)
    data.extend([[type(base[x])(base[x] + random.uniform(0., 1.)*scale[x])
                 for x in xrange(5)] for y in xrange(10)])
    colors.extend(['0.9:'] * 10)
    coordinate_labels=["float", "true/false", "float", "big int", "sml int"]
     
    plt, lgd = parallel_coordinates(data, style=colors, labels=line_labels, jitter_sd=0.01)
    
    plt.show()