# -*- coding: utf-8 -*-
"""
Created on Wed Feb 06 20:05:38 2013

@author: juherask
"""

from pylab import *
    
from parse_results_for_extra_tables import _helper_read_evals
from parse_results import DEFAULT, EBS, EXTRA_EBS, TUNERS, VRPH_ALGOS, VRPSD_ALGOS
from parse_results import label_to_avgFunc,get_scaling_range, normalizeQualities
from collections import OrderedDict
import figgen
from os import path
import pickle

READ_FROM_CACHE = True
CREATE_CACHE = False

JOURNALSTYLE = True
style_name = "_bw"
#style_name = ""

FIG_WIDTH = 470

SPECIAL_EVALS = ["we", "testset"]
FOLDERS = [
    "christofides_3cv",
    "augerat_reruns",
    "iridia_reruns",
    ]
EVAL_FILES = "evals_*%s*.txt" 

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
         'lines.linewidth': 1.0,
         'legend.handlelength': 3}
    rcParams.update(params)

all_algos = []
all_t_nresults = OrderedDict()
all_v_nresults = OrderedDict()

pickle_files_exists = path.isfile(r"cache/plot_scatter_all_nresults.p")


if READ_FROM_CACHE and pickle_files_exists and not CREATE_CACHE:
    all_t_nresults,all_v_nresults,tuners,all_algos = pickle.load( open( r"cache/plot_scatter_all_nresults.p", "rb" ) )
else:
    for source in FOLDERS:
        uavgFunc = label_to_avgFunc('median')               
        t_results,tuners,algos,ebs = _helper_read_evals(source, "we", uavgFunc)
        minQ, maxQ, nmult = get_scaling_range("_we", source, scale_optimality_gap=True)
        t_nresults = normalizeQualities(t_results, minQ, maxQ, nmult)
        
        v_results,tuners,algos,ebs = _helper_read_evals(source, "testset", uavgFunc)
        minQ, maxQ, nmult = get_scaling_range("_testset", source, scale_optimality_gap=True)
        v_nresults = normalizeQualities(v_results, minQ, maxQ, nmult)
    
        all_algos+=algos
        all_t_nresults = OrderedDict( all_t_nresults.items() + t_nresults.items() )   
        all_v_nresults = OrderedDict( all_v_nresults.items() + v_nresults.items() )   

if CREATE_CACHE:
    pickle.dump( (all_t_nresults,all_v_nresults,tuners,all_algos), open( r"cache/plot_scatter_all_nresults.p", "wb" ) )

if JOURNALSTYLE:
    marker_color_style = 'journal'
else:
    marker_color_style = 'poster'

#t_keylist = list(all_t_nresults.keys())
#t_keylist.sort()
#for key in t_keylist:
#    print key, all_t_nresults[key][0], "repeats"
#print
#v_keylist = list(all_v_nresults.keys())
#v_keylist.sort()
#for key in v_keylist:
#    print key, all_v_nresults[key][0], "repeats"
#exit()

fig_tex_file = file("scatter_plots/scatter_figures.txt", 'w')

def _write_figure_env_latex(texf, target, filename):
    same_dir_fn = filename.replace("scatter_plots/", "")
    texf.write(r"\begin{figure}[!ht]\n")
    texf.write(r"\caption{Scatter plot of solution quality on validation vs. training set for %s results.}\n"%target)
    texf.write(r"\includegraphics[width=1.0\textwidth]{%s}\n"%same_dir_fn)
    texf.write(r"\end{figure}\n")
    texf.write(r"\n")


for plot_ext in [".png", ".eps"]:   
    
    for tuner in tuners:
        filename = "scatter_plots/scatter_training_vs_validation_"+tuner+style_name+plot_ext
        figgen.exportOverTunePlot(filename, all_t_nresults, all_v_nresults, all_algos, [tuner], [100,500,1000,5000], marker_color_style)
        if plot_ext==".eps":
            _write_figure_env_latex(fig_tex_file, tuner, filename)
    for algo in all_algos:
        filename = "scatter_plots/scatter_training_vs_validation_"+algo.replace(" ", "_")+style_name+plot_ext
        figgen.exportOverTunePlot(filename, all_t_nresults, all_v_nresults, [algo], tuners, [100,500,1000,5000], marker_color_style)    
        if plot_ext==".eps":
            _write_figure_env_latex(fig_tex_file, algo, filename)
    
    filename = "scatter_plots/scatter_training_vs_validation_ALL_VRPH"+style_name+plot_ext
    figgen.exportOverTunePlot(filename, all_t_nresults, all_v_nresults, VRPH_ALGOS, tuners, [100,500,1000,5000], marker_color_style, per="algo")
    if plot_ext==".eps":
        _write_figure_env_latex(fig_tex_file, "all", filename)
    
    filename = "scatter_plots/scatter_training_vs_validation_ALL_VRPSD"+style_name+plot_ext
    figgen.exportOverTunePlot(filename, all_t_nresults, all_v_nresults, VRPSD_ALGOS, tuners, [100,500,1000,5000], marker_color_style, per="algo")
    if plot_ext==".eps":
        _write_figure_env_latex(fig_tex_file, "all", filename)
    
    filename = "scatter_plots/scatter_training_vs_validation_ALL_TOGETHER"+style_name+plot_ext
    figgen.exportOverTunePlot(filename, all_t_nresults, all_v_nresults, all_algos, tuners, [100,500,1000,5000], marker_color_style)
    if plot_ext==".eps":
        _write_figure_env_latex(fig_tex_file, "all", filename)
    
fig_tex_file.close()

#pcfile = r"iridia\\result_*_vrpsd_ts_*eval_10repts.txt"
#results = parseResultsFromFiles(pcfile)
#_exportGraphs(results, ["VRPSD TS"] , "median", "_results", extension = "png", graph_type="parallel", journalstyle=JOURNALSTYLE)
#_exportGraphs(results, ["VRPSD TS"] , "median", "_results", extension = "eps", graph_type="parallel", journalstyle=JOURNALSTYLE)
