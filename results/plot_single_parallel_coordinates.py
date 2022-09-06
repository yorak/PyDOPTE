# -*- coding: utf-8 -*-
"""
Created on Wed Feb 06 20:05:38 2013

@author: juherask
"""

from pylab import *
    
from parse_results import parseResultsFromFiles, _exportGraphs

JOURNALSTYLE = True
FIG_WIDTH = 470

if JOURNALSTYLE:
    # 469.75499
    fig_width_pt = FIG_WIDTH  # Get this from LaTeX using \showthe\columnwidth
    inches_per_pt = 1.0/72.27               # Convert pt to inch
    golden_mean = (sqrt(5)-1.0)/2.0         # Aesthetic ratio
    fig_width = fig_width_pt*inches_per_pt  # width in inches
    fig_height = fig_width*golden_mean      # height in inches
    fig_size =  [fig_width,fig_height]
    params = {'backend': 'ps',
         'axes.labelsize': 10,
         'text.fontsize': 10,
         'legend.fontsize': 8,
         'xtick.labelsize': 8,
         'ytick.labelsize': 8,
         #'text.usetex': True,
         'text.usetex': False,
         'font.family': 'serif',
         'figure.figsize': fig_size,
         'axes.linewidth': 1.5,
         'lines.linewidth': 1.5}
    rcParams.update(params)


pcfile = r"result_IRace_vrph_augerat_sa_10sec_optimal_1000eval_1repts.txt"
results = parseResultsFromFiles(pcfile)
_exportGraphs(results, ["VRPH SA A"] , "median", "_optimal", extension = "png", graph_type="parallel", journalstyle=JOURNALSTYLE)
_exportGraphs(results, ["VRPH SA A"] , "median", "_optimal", extension = "eps", graph_type="parallel", journalstyle=JOURNALSTYLE)


#pcfile = r"iridia\\result_*_vrpsd_ts_*eval_10repts.txt"
#results = parseResultsFromFiles(pcfile)
#_exportGraphs(results, ["VRPSD TS"] , "median", "_results", extension = "png", graph_type="parallel", journalstyle=JOURNALSTYLE)
#_exportGraphs(results, ["VRPSD TS"] , "median", "_results", extension = "eps", graph_type="parallel", journalstyle=JOURNALSTYLE)
