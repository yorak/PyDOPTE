# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 15:56:46 2016

@author: juherask

Plot cutoff results
"""

from parse_results import label_to_avgFunc, get_scaling_range
from figgen import _get_styles
from pylab import *
import scipy
from math import sqrt

import glob
import os
from collections import defaultdict
ROOTDIR = 'cutoff_tests'
AVGF = scipy.mean

PS_TYPES = ['default', 'median', 'best']
#PS_TYPES = ['best']
TARGETS = ['vrpsd_acs', 'vrpsd_ea', 'vrpsd_ils', 'vrpsd_sa', 'vrpsd_ts',
'vrph_rtr_c', 'vrph_sa_c', 'vrph_ej_c',
'vrph_rtr_a', 'vrph_sa_a', 'vrph_ej_a' ]

def _extract_datapoints_from_results(cutoff_data, avgf, minQ, maxQ, multiplierQ):
    exv = []
    eyv = []
    
    # TODO: Plot quality to the same plot (normalize)
    qxv = []
    qyv = []
    
    #print target
    cutoffs = sorted(cutoff_data.keys())
    for co in cutoffs:  
       
        repeats = cutoff_data[co] 
        if not co in cutoffs:
            continue
        
        elapsed_time_values = []
        aggregated_qs = []
        for rpt_idx, payloads in repeats.items():
            i_files, qs, ets = zip(*payloads)
            # sum of time spent on entire benchmark set (all instances)
            elapsed_time_values.append( sum(ets) )
            aggregated_qs.append( sum(qs) )
            
        if len(elapsed_time_values)==0: 
            print "no data for", co
            continue

        exv.append( co )
        eyv.append( avgf(elapsed_time_values)/14.0 )
        #print co, mean(elapsed_time_values)/14.0
            
        qxv.append( co )
        qyv.append( (avgf(aggregated_qs)-minQ)/(maxQ-minQ)*multiplierQ )    
    
    return exv, eyv, qxv, qyv
    
def plot_cutoff(results, targets, avgf, filename, pubstyle='journal'):
    """
    Pubstyle can be also 'poster'
    """
    print "ExportCuroffGraph", "line", filename
    
    colors, styles, markers = _get_styles(pubstyle, len(targets))
    
    fig, ax1 = subplots()
    ax2 = ax1.twinx()

    # ps_type -> target -> cutoff -> repeat -> payload (benchmark_name, q, wall_time)
   
    # Loop targets
    i = 0
    ls = '-'
    col = 'k'
    mk = ''
    
    # loop cutoff
    xv = []
    yv = []        
    cutoffs = sorted(results[targets[0]].keys())
    for co in cutoffs:
        ls = ':'
        col = 'k'
        mk = ''
        yv.append(co)
        xv.append(co)
    ax2.plot(xv, yv, c=col, label = "Timeout", marker=mk, linestyle = ls )
    
    q_line_style = None
    for target in targets:
        minQ, maxQ, multiplierQ = get_scaling_range("_tuneset", target, False, True)    
        
        exv, eyv, qxv, qyv = _extract_datapoints_from_results(results[target], avgf, minQ, maxQ, multiplierQ)        
            
        col = colors[mod(i,len(colors))]
        etls = styles[mod(i/len(colors),len(styles))]
        qls = styles[mod(i/len(colors)+1,len(styles))]
        if markers:
            mk = markers[mod(i,len(markers))]
        i+=1
        
        #DEBUG
        #if ("vrph" in target and "best" in filename):
        #    print target, minQ, maxQ, multiplierQ, qyv
        labelized = target.replace('_','-').upper()
        
        #print col, type(col), i, labelized, max(eyv)
        
        ax2.plot(exv, eyv, label = labelized, c=col, marker=mk, linestyle = etls )
        ax1.plot(qxv, qyv, c=col, marker=mk, linestyle = qls )
        #print(target, qyv)
        
        q_line_style = qls
    
    # legend for quality
    #handles, labels = ax1.get_legend_handles_labels()
    ax2.plot([2.0], [2.0], linestyle = q_line_style, label = 'Quality', c='k', marker=mk )
    #ax1.legend(handles, labels)
    
    ax1.set_xlim( (min(cutoffs), max(cutoffs)) )
    ax2.set_ylim( (min(cutoffs), max(cutoffs)) )
    ax1.set_ylim( (0.0, 2.0) )
    
    #yscale('log')
    ax1.set_xscale('log')
    ax2.set_xscale('log')
    
    ax1.set_xlabel('Set CPU cutoff (s)')
    ax2.set_ylabel('Average elapsed time (s)')
    ax1.set_ylabel('Average optimality gap (\%)')
    
    #ax2.axvline(linewidth=4, linestyle=q_line_style, color='w' )
    
    #lgd = ax1.legend(loc='upper left', bbox_to_anchor=(1.1, 1.0))
    lgd = ax2.legend(loc='upper center',ncol=2)
    fig.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')#, dpi=400)
    clf()  

def read_cutoff_test_evals(results, filename):
    lnr = 0;
    for l in file(filename, 'r').readlines():
        lnr += 1
        parts = l.split(';')
        if len(parts)!=8:
            print "Malformed line ", l
        else:
            # Unpack the payload
            #<key>;<cutoff>;<wall_time>;<repeat idx>;<benchmark_name>; (continues...)
            # (continues...) <seed>;<evaulation result>;<hash_of_the_parameter_set_seed_and_benchmark>
            tgt, cutoff_t, elapsed_t, rpt_idx = \
                parts[0], float(parts[1]), float(parts[2]), int(parts[3])
            instance_file, seed, q = \
                parts[4], int(parts[5]), float(parts[6])
                
            if (q>10000):
                print "Invalid Q on line", lnr 
                
            try:
                ps_hash = int(parts[7])
            except ValueError:
                try:
                    ps = eval(parts[7])
                    ps_hash = hash(parts[7])
                except SyntaxError:
                    print "Error parsing", parts[7]
                
            # QUICKFIX: numbering of the repeat idx in some files is 
            #  a little off.
            if "default" in filename:
                found_repeat_with_room_for_the_instance = False
                while len(results[tgt][cutoff_t][rpt_idx])>0 and\
                    not found_repeat_with_room_for_the_instance and\
                    rpt_idx<10:                    
                        
                    i_files, qs, ets = zip(*results[tgt][cutoff_t][rpt_idx])
                    if instance_file in i_files:
                        rpt_idx+=1
                    else:
                        found_repeat_with_room_for_the_instance=True
                 
                # Too many results
                if rpt_idx==10:
                    continue 
                
            #if results[tgt][cutoff_t][rpt_idx]:
            #    rpt_idx = max( results[tgt][cutoff_t].keys() )+1
                
            # add to results list
            results[tgt][cutoff_t][rpt_idx].append( (instance_file, q, elapsed_t) )

def read_and_validate(file_list, ps_type_list=None):
    if ps_type_list==None:
        ps_type_list = ["N/A"]*len(file_list)

    ## Initialize data structure ##
    # ps_type -> target -> cutoff -> repeat -> payload (benchmark_name, q, wall_time)
    results = defaultdict( # key = ps_type (str)
        lambda: defaultdict( # key = target (str)
            lambda: defaultdict( # key = cutoff (float)
                lambda: defaultdict( # key = repeat idx (int)
                    lambda: list() #list of all instance evaluations
        ))))        
        
    ## Read data ##
    for cf, ps_type in zip(file_list, ps_type_list):
        print "Reading lines from file", cf
        read_cutoff_test_evals(results[ps_type], cf)
    types = set(ps_type_list)
    
    # Validate
    for pst in types:
        for tgt in TARGETS:
            cutoffs = sorted(results[pst][tgt].keys())
            #print cutoffs
            for co in cutoffs:
                #print pst, tgt, co, len(results[pst][tgt][co])
                
                # todo: check that the same instance is not twice in a rep
                for rpt, values in results[pst][tgt][co].items():
                    i_files, qs, ets = zip(*values)
                    if len(set(i_files))!=14:
                        print "error: no 14 instances for", pst, tgt, co, rpt          
    return results
    
def main():
    
    file_list = []
    ps_type_list = []
    for subdir, dirs, files in os.walk(ROOTDIR):
        for d in dirs:
            seekpath = os.path.join(ROOTDIR, d, 'cutoff_*.csv')
            for cf in glob.glob(seekpath):
                #read_cutoff_test_evals(results[d], cf)
                file_list.append(cf)
                ps_type_list.append(d)
                
    results = read_and_validate(file_list, ps_type_list)
    
    pub_style = 'journal'        
    #pub_style = 'poster'
    
    
    set_plt_style = False
    if pub_style=='journal':
        style_specifier = "_bw"
        linewt = 1.0
        axeswt = 1.5
        fig_width_pt = 477.92834 # for JVRA
        set_plt_style = True
    elif pub_style=='poster':
        linewt = 2.5
        axeswt = 1.5
        fig_width_pt = 600 #??
        set_plt_style = True
    
    if set_plt_style:  
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
             'axes.linewidth': axeswt,
             'lines.linewidth': linewt,
             'legend.handlelength': 3}
        rcParams.update(params)
        
   
    #plot cutoffs 
    for pst in PS_TYPES:
        vrph_targets = [t for t in TARGETS if "vrph" in t]
        fn = os.path.join("plots", "cutoff", "vrph_%s_parameters%s.png"%(pst,style_specifier))
        plot_cutoff(results[pst], vrph_targets, AVGF, fn, pub_style )
        fn = os.path.join("plots", "cutoff", "vrph_%s_parameters%s.eps"%(pst,style_specifier))
        plot_cutoff(results[pst], vrph_targets, AVGF, fn,  pub_style)
    
        vrpsd_targets = [t for t in TARGETS if "vrpsd" in t]
        fn = os.path.join("plots", "cutoff", "vrpsd_%s_parameters%s.png"%(pst,style_specifier))
        plot_cutoff(results[pst], vrpsd_targets, AVGF, fn, pub_style)
        fn = os.path.join("plots", "cutoff", "vrpsd_%s_parameters%s.eps"%(pst,style_specifier))
        plot_cutoff(results[pst], vrpsd_targets, AVGF, fn, pub_style)
    

if __name__=="__main__":
    main()        
        