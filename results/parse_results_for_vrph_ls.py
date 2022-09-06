# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 20:27:13 2012

@author: juherask

This file has routines that do all kinds of validation for tuning results.
See the function documentations for more info.
"""

#from evaluate_results import evaluate_results        
import os
from pprint import pprint

from collections import defaultdict
from parse_results import parseEvalsFromFiles, parseResultsFromFiles
from parse_results import medianFunc,meanFunc,bestFunc,worstFunc
from helpers import module_exists, median

if module_exists("pylab"):
    from pylab import *

import numpy as np

if module_exists("scipy"):
    import scipy

AVFGS = {medianFunc,meanFunc,bestFunc,worstFunc}
SPECIAL_EVALS = ["we", "testset"]
FOLDERS = [
    "augerat_reruns",
    "christofides_3cv"
    ]
EVAL_FILES = "evals_*%s*.txt" 
RESULT_FILES = "result_*repts*.txt"

LS_OPS = [
    "-h_1pm",
    "-h_2pm",
    "-h_two",
    "-h_oro",
    "-h_tho",
    "-h_3pm",
]

def _get_styles(journalstyle):
    if journalstyle:
        colors = ['0.8',
                  '0.4', 
                  '1.0']           
        styles = ["","//","--","xx","++"]
        
    else:
        colors = [(216/255.0,66/255.0,0.0), # Bright red                   
                   (62/255.0,84/255.0,151/255.0), # Blue
                   (194/255.0,194/255.0,194/255.0), # Gray
                   (166/255.0,50/255.0,0.0), # Dark red
                   (29/255.0,38/255.0,71/255.0), # Dark blue
                   (97/255.0,97/255.0,97/255.0), #Dark grey
                  ]
        colors.reverse()
        styles = [""]
        
    return colors, styles

def plot_stacked_ls_bar_plot(fn, ls_with_q, all_algos, journalstyle):
    
    colors, styles = _get_styles(journalstyle)
              
    # a stacked bar plot with errorbars    
    N = len(all_algos)
    ind = np.arange(N)+0.35    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence
    
    uses_per_ls = defaultdict(list)
    aal = list(all_algos)
    aal.sort()
    for algo in aal:
        cidx = 0
        
        # FILTER AND COUNT
        ps_count_per_ls = defaultdict(int)
        total_ps_count = 0
        for key, lofq in ls_with_q.items():
            (kt, ka, keb) = key
            if ka!=algo: #and keb==1000:
                continue
            total_ps_count += len(lofq)
            for ls in LS_OPS:
                for q,tp in lofq:
                    if ls in tp and tp[ls]==1:
                        ps_count_per_ls[ls]+=1

        # Plot
        for ls in LS_OPS:
            uses_per_ls[ls].append( ps_count_per_ls[ls]/float(total_ps_count)*100)
    
    fsize = rcParams['figure.figsize']
    fsize = (fsize[0]*(1.4), fsize[1])
    fig = plt.figure(figsize=fsize)
    
    ax = plt.subplot(111)
    
    ax.yaxis.grid(True, linestyle='--')
    
    plots = []
    cidx = 0
    sum_so_far = [0]*len(aal)
    ls_labels = []
    for ls in reversed(LS_OPS):
        #print sum_so_far
        #print uses_per_ls[ls]
        c = colors[cidx%len(colors)] 
        s = styles[cidx/len(colors)]       
        
        if cidx==0:
            plots.append( ( ax.bar(ind, uses_per_ls[ls], width, color=c, hatch=s))[0] )
        else:
            plots.append( ( ax.bar(ind, uses_per_ls[ls], width,  color=c, hatch=s, bottom=sum_so_far))[0] )
            
        sum_so_far = [sum(a) for a in zip(*[uses_per_ls[ls], sum_so_far])]
        cidx+=1
        ls_labels.append(ls.replace("-h_", ""))
    
    plt.ylabel('Used in % of configurations')
    #plt.title('Scores by group and gender')
    xtind = ind+width/2.
    xtind = np.insert(xtind, 0, [0.0])
    plt.xticks(xtind, tuple([""]+aal) )    
    
    #plt.yticks(np.arange(0,max(sum_so_far),100))
    
    # Shink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
    # Put a legend to the right of the current axis
    ax.legend(tuple(reversed(plots)), tuple(reversed(ls_labels)), loc='center left', bbox_to_anchor=(1, 0.5))

    #plt.legend( tuple(plots), tuple(ls_labels) )
    
    print "ExportGraph", "stacked", all_algos, fn   
    fig.savefig(fn,bbox_inches='tight' )#, dpi=300)
    #plt.show()

def number_of_times_reached_optima():
    pass

def count_ls_activitations(data_folder, special_eval, top_percent=25):
    print "Read %s evaluations from %s" % (special_eval, data_folder)
    eval_files = EVAL_FILES % special_eval                 
    seekpath = os.path.join(data_folder, eval_files)
    evaluations = parseEvalsFromFiles(seekpath, medianFunc, True)    
    
    print "Read results from %s" % (data_folder)
    seekpath = os.path.join(data_folder, RESULT_FILES)
    results = parseResultsFromFiles(seekpath, medianFunc)
    
    ls_with_q = defaultdict(list)
    ## 1. ITERATE TUNING TASKS
    tuners = set()
    algos = set()
    ebs = set()
    
    for task_key, tuning_task_evaluations in evaluations.items():        
        (tuner, algo, eb) = task_key
        tuners.add(tuner)
        algos.add(algo)
        ebs.add(eb)
        
        ## 2. ITERATE PARAMETER CONFIGURATIONS OF A TUNING TASK
        for ps_idx, repeats in tuning_task_evaluations.items():
            evalq_results = []
            
            ## 3. ITERATE EVALUATION REPETITIONS OF A TASK AND OF A PARAMETER SET
            for repetition in repeats:
                benchmark_q = 0.0
                for evaluation in repetition:
                    payload = evaluation
                    #unpack (tuned_ps_idx,benchmark_name,instance_quality,ps_actual_evals,ps_hash)
                    (ps_idx,instance_name,q,ps_evals,ps_hash) = payload
                    #print ps_idx," ", 
                    benchmark_q += q
                        
                evalq_results.append(benchmark_q)
        
            #print task_key
            (ar, mev, meq, seq, tpl, ql, evl ) = results[task_key]
            #print "mymed =", median(evalq_results), "meq =",meq
            ls_with_q[task_key].append( (median(evalq_results), tpl[int(ps_idx)]) )              
    
    if top_percent!=100:
        all_by_q = {}
        for algo in algos:
            # Gather all results of this algo into a 
            
            all_by_q[algo] = []
            
            for k,pl in ls_with_q.items():
                key_algo = k[1]
                if key_algo!=algo:
                    continue
                for p in pl:
                    all_by_q[algo].append( p+k )
            all_by_q[algo].sort()
            
        # clear all old data
        ls_with_q.clear()
        for algo in algos:
            nbrtosel = int( len(all_by_q[algo])*(top_percent/100.0) )
            for q_psi_key in all_by_q[algo][:nbrtosel]:
                #print q_psi_key
                key = (q_psi_key[2], q_psi_key[3], q_psi_key[4])
                #print key
                ls_with_q[key].append( (q_psi_key[0], q_psi_key[1]) )
                
    #print ls_with_q
    #return
    
    for algo in algos:
        ps_count_per_ls = defaultdict(int)
        total_ps_count = 0
        
        for key, lofq in ls_with_q.items():
            (kt, ka, keb) = key
            if ka!=algo: #and keb==1000:
                continue
                
            total_ps_count += len(lofq)
            
            for ls in LS_OPS:
                for q,tp in lofq:
                    if ls in tp and tp[ls]==1:
                        ps_count_per_ls[ls]+=1
        
        if top_percent!=100:
            print "top %d%%"%top_percent
        else:
            print "all"
        print algo        
        for ls in LS_OPS:
            if total_ps_count==0:
                print "ERROR, no results for", ls
            else:
                print ls, "%d, %.2f%%" % (ps_count_per_ls[ls], ps_count_per_ls[ls]/float(total_ps_count)*100)
        print
        
    return ls_with_q, algos
            
            
if __name__ == "__main__":
    
    JOURNALSTYLE = False
    FIG_WIDTH = 470
    
    style_specifier = ""
    if JOURNALSTYLE:
        style_specifier = "_bw"
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

    #count_ls_activitations("augerat", "we", top25=False)
    #count_ls_activitations("augerat", "we", top25=True)
    #count_ls_activitations("augerat", "testset", top25=False)
    lswq_a, algos_a = count_ls_activitations("augerat_reruns", "testset", top_percent=10)
    
    #count_ls_activitations("christofides", "we", top25=False)
    lswq_c, algos_c = count_ls_activitations("christofides_3cv", "testset", top_percent=10)
    
    all_lswq = dict( lswq_a.items()+lswq_c.items() )
    all_algos = list(algos_a)+list(algos_c)
    
    print all_lswq
    print all_algos
    
    #plot_stacked_ls_bar_plot("plots\\local_search_stacked.svg", all_lswq, all_algos, journalstyle=JOURNALSTYLE)
    plot_stacked_ls_bar_plot("plots/local_search_stacked%s.eps" % style_specifier, all_lswq, all_algos, journalstyle=JOURNALSTYLE)
    plot_stacked_ls_bar_plot("plots/local_search_stacked%s.png" % style_specifier, all_lswq, all_algos, journalstyle=JOURNALSTYLE)
    
