# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 11:24:34 2013

@author: juherask
"""

from parse_results_for_extra_tables import _helper_read_evals
from figgen import _labelize, _get_styles
from parse_results import ALGOS, TUNERS, label_to_avgFunc, get_scaling_range, normalizeQualities

from operator import sub
from pylab import *

FOLDER = "plots/gapbox/"
def export_gap_bplot(filename, results, merge_algos=True, eb=1000):
        
    # Data compared to UCS 
    data_vs_urs = []
    data_vs_def = []
    labels = []
    
    if merge_algos:
        for tuner in TUNERS:
            per_tuner_vs_urs = []
            per_tuner_vs_def = []
            for algo in ALGOS:
                urskey = ("URS", algo, eb)
                defkey = ("Defaults", algo, 1)
                if urskey not in results or defkey not in results:
                    continue
                ursmq = results[urskey][2]
                defmq = results[defkey][2]
            
                key = (tuner, algo, eb)
                (repts, mev, meq, seq, tpl, ql, evl ) = results[key]
                tql = list(ql)
                
                per_tuner_vs_urs+=map(sub, [ursmq]*len(tql), tql )
                per_tuner_vs_def+=map(sub, [defmq]*len(tql), tql )
            data_vs_urs.append( per_tuner_vs_urs )
            data_vs_def.append( per_tuner_vs_def )            
            labels.append( _labelize(tuner) )      
    else:
        for algo in ALGOS:
            urskey = ("URS", algo, eb)
            defkey = ("Defaults", algo, 1)
            if urskey not in results or defkey not in results:
                continue
            ursmq = results[urskey][2]
            defmq = results[defkey][2]
            
            for tuner in TUNERS:
                key = (tuner, algo, eb)
                (repts, mev, meq, seq, tpl, ql, evl ) = results[key]
                tql = list(ql)
                
                data_vs_urs.append( map(sub, [ursmq]*len(tql), tql ) )
                data_vs_def.append( map(sub, [defmq]*len(tql), tql ) )
                labels.append( _labelize(tuner)+" "+algo )
            
    data_vs_urs.reverse()
    data_vs_def.reverse()
    labels.reverse()
     
    #xlabel(Y_LABEL.capitalize())      
    for data, flabel in [(data_vs_urs, "vs_urs_"), (data_vs_def, "vs_def_")]:
        #if len(labels)>22:        
        #    fsize = rcParams['figure.figsize']
        #    fsize = (fsize[0], fsize[1]*2.0)
        #    print len(labels)
        #    boxwidth = 1.4
        #    fig = figure(1, figsize=fsize)
        #    print fsize
        #else:
        boxwidth = 0.4
        #    fig = figure(1)
        fig = figure(1)
        
        ax = fig.add_subplot(111)
        bp = ax.boxplot(data, vert=False, widths=boxwidth)     
        xlim( (-1.75,1.75) )    
        ax.xaxis.grid(True) 
        #grid(True)
        
        
        colors, styles, markers = _get_styles('poster')
            
        BBLINE = 1.0
        setp(bp['boxes'], color=colors[3], linewidth=BBLINE)
        setp(bp['whiskers'], color=colors[2], linestyle = 'solid', linewidth=BBLINE)
        setp(bp['fliers'], color=colors[2]) #, alpha = 0.9, marker= 'o', markersize = 2)
        setp(bp['medians'], color=colors[0], linewidth=BBLINE*1.5)
            
        yticks(range(1, len(labels)+1), labels)
        xlabel( "Optimality gap closed vs. defaults (%)") 
        savefig(FOLDER+flabel+filename, pad_inches=0.1, bbox_inches='tight', dpi=400)
        print "saved figure: ", FOLDER+flabel+filename
        clf()


SPECIAL_EVALS = ["testset"] #, we]
FOLDERS = [
    "christofides",
    "augerat",
    "iridia",
    ]
    
for se in SPECIAL_EVALS:#[1:]:
    allnresults = {}
    for df in FOLDERS:    
        ase=se
        #quickfix for missing testset on christofides (results shown twice)
        if "test" in se and df=="christofides":
            ase = "we"
            
        uavgFunc = label_to_avgFunc("median")
        results,tuners,algos,ebs = _helper_read_evals(df, ase, uavgFunc)
                          
        minQ, maxQ, nmult = get_scaling_range("_"+ase, df, scale_optimality_gap=True)
        nresults = normalizeQualities(results, minQ, maxQ, nmult)
        
        allnresults = dict(allnresults.items() + nresults.items())
    
    inches_per_pt = 1.0/72.27               # Convert pt to inch
    golden_mean = (sqrt(5)-1.0)/2.0         # Aesthetic ratio
    fig_width = 430.0*inches_per_pt  # width in inches
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
             #'axes.linewidth': linewt,
             #'lines.linewidth': linewt,
             'legend.handlelength': 3}
    rcParams.update(params)
    
    #Plot
    filename = "box_plot_gap_close_%s.png" % (ase)
    export_gap_bplot("merged-"+filename, allnresults, merge_algos=True, eb=1000)
    #export_gap_bplot("varied-"+filename, allnresults, merge_algos=False, eb=1000)
        
        
            
            
        
    