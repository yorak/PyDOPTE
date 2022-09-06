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

from parse_results import DEFAULT, EBS, EXTRA_EBS, TUNERS, parseEvalsFromFiles, get_special_eval, calculateSignificances
from parse_results import medianFunc,label_to_avgFunc,get_scaling_range, normalizeQualities,_filterResults
from helpers import module_exists
import figgen
import argparse

if module_exists("pylab"):
    from pylab import *

import numpy as np

if module_exists("scipy"):
    import scipy

BLACKLIST_TUNERS = []
BLACKLIST_ALGOS = []
#BLACKLIST_TUNERS = ["REVAC"]
#BLACKLIST_ALGOS = ["VRPH EJ A","VRPH RTR A","VRPH SA A"]

SPECIAL_EVALS = ["we", "testset"]
FOLDERS = [
    "christofides_3cv",
    "augerat_reruns",
    "iridia_reruns",
    ]
EVAL_FILES = "evals_*%s*.txt" 
RESULT_FILES = "result_*repts.txt"

        
BEST_CMP_RAPORT_THLD = 1.0
BEST_CMP_TOL = 0.05
best_known = {
"B-n31-k5.vrp":672.0,
"B-n34-k5.vrp":788.0,
"B-n35-k5.vrp":955.0,
"B-n38-k6.vrp":805.0,
"B-n39-k5.vrp":549.0,
"B-n41-k6.vrp":829.0,
"B-n44-k7.vrp":909.0,
"B-n45-k5.vrp":751.0,
"B-n45-k6.vrp":678.0,
"B-n50-k7.vrp":741.0,
"B-n51-k7.vrp":1018.0,
"B-n56-k7.vrp":707.0,
"B-n57-k9.vrp":1598.0,
"B-n63-k10.vrp":1496.0,

"Christofides_01.vrp":524.61,
"Christofides_02.vrp":835.26,
"Christofides_03.vrp":826.14,
"Christofides_04.vrp":1028.42,
"Christofides_05.vrp":1291.29,
"Christofides_06.vrp":555.43,
"Christofides_07.vrp":909.68,
"Christofides_08.vrp":865.94,
"Christofides_09.vrp":1162.55,
"Christofides_10.vrp":1395.85,
"Christofides_11.vrp":1042.11,
"Christofides_12.vrp":819.56,
"Christofides_13.vrp":1541.14,
"Christofides_14.vrp":866.37,
}

VERBOSITY = 0

def _helper_get_key_values(results):
    tuners = set()
    algos = set()
    ebs = set()
    for task_key in results:        
        (tuner, algo, eb) = task_key
        if tuner in BLACKLIST_TUNERS or algo in BLACKLIST_ALGOS:
            continue
        tuners.add(tuner)
        algos.add(algo)
        ebs.add(eb)     
    tuners = list(tuners)
    tuners.sort()
    if DEFAULT[0] in tuners:
        tuners.remove(DEFAULT[0])
    algos = list(algos)
    algos.sort()
    ebs = list(ebs)
    ebs.sort()
    if 1 in ebs:
        ebs.remove(1)
    
    return tuners, algos, ebs
    
def _helper_read_evals(data_folder, special_eval, uavgFunc):
    #print "Read %s evaluations from %s" % (special_eval, data_folder)
    eval_files = EVAL_FILES % special_eval                 
    seekpath = os.path.join(data_folder, eval_files)
    results = parseEvalsFromFiles(seekpath, uavgFunc, False)
    
    tuners,algos,ebs = _helper_get_key_values(results)
    
    
    return results,tuners,algos,ebs


def calculate_optimality_gap_close(special_eval, data_folder, avgfl):
    uavgFunc = label_to_avgFunc(avgfl)
    results,tuners,algos,ebs = _helper_read_evals(data_folder, special_eval, uavgFunc)
                      
    minQ, maxQ, nmult = get_scaling_range("_"+special_eval, data_folder, scale_optimality_gap=True)
    nresults = normalizeQualities(results, minQ, maxQ, nmult)

    gapdict = {}    
    
    imp_keys = ['best', 'worst', 'mean', 'median']
    absolute_imps_all_algos = {'median':[], 'mean':[], 'best':[], 'worst':[]}
    relative_imps_all_algos = {'median':[], 'mean':[], 'best':[], 'worst':[]}
    
    for algo in algos:
        #close 
        dkey = ("Defaults", algo, 1)
        baselevel = nresults[dkey][2] #meq
        print algo, baselevel
        
        #if "we" in special_eval and "3cv" in data_folder:
        #    baselevel = baselevel*2
        
        algo_improvements = []
        algo_sumimprovement = 0.0
        algo_sumcnt = 0
        algo_biq = 0.0
        algo_bik = None
        algo_wiq = 0.0
        algo_wik = None
        
        for eb in ebs:
            improvements = []
            sumimprovement = 0.0
            sumcnt = 0
            biq = 0.0
            bik = None
            wiq = 0.0
            wik = None
            for tuner in tuners:
                tkey = (tuner, algo, eb)                
                if tkey not in nresults:
                    continue
                
                #         0   1    2     3    4    5   6
                # unpack (ar, mev, meq, seq, tpl, ql, evl ) 
                tlevel = nresults[tkey][2] #meq
                
                # best and worst of the repetitions
                btlevel = min(nresults[tkey][5])
                wtlevel = max(nresults[tkey][5])
                
                #if avgfl=='best' and min(nresults[tkey][5])<tlevel:
                #    print "best does not work?"
                
                improvement = baselevel-tlevel
                bimprovement = baselevel-btlevel
                wimprovement = baselevel-wtlevel
                
                
                gapkey = (tuner, algo, eb)
                gapdict[gapkey] = improvement
                
                if VERBOSITY>1:
                    print "%s;%s;%s;%s;%.2f;%.2f%%;best_repeat;%.2f;%.2f;%.2f%%;" % (avgfl,str(tkey[0]),str(tkey[1]),str(tkey[2]), improvement, improvement/baselevel*100, btlevel, bimprovement, bimprovement/baselevel*100)
                    print baselevel
                sumimprovement+=improvement 
                improvements.append(improvement)
                sumcnt+=1
                
                if not bik or bimprovement > biq:
                    bik = tkey
                    biq = bimprovement 
                if not wik or wimprovement < wiq:
                    wik = tkey
                    wiq = wimprovement 
                    
            if sumcnt>0:
                if VERBOSITY>0:
                    print "Best and worst are from the best/worst configuration out of the tuning repetitions"
                    print "Best %s improvement by %s: %.2f (%.2f %% better than defaults)" % (avgfl,str(bik), biq, biq/baselevel*100)
                    print "Worst %s improvement  by %s: %.2f (%.2f %% better than defaults)" % (avgfl,str(wik), wiq, wiq/baselevel*100)
                    meanimp = sumimprovement/sumcnt
                    print "Mean %s improvement for %s: %.2f (%.2f %% better than defaults)" % (avgfl,str((algo, eb)), meanimp, meanimp/baselevel*100)
                    medianimp = scipy.median(improvements)
                    print "Median %s improvement for %s: %.2f (%.2f %% better than defaults)" % (avgfl,str((algo, eb)), medianimp, medianimp/baselevel*100)
                    print
                
                algo_sumimprovement += sumimprovement
                algo_improvements += improvements
                algo_sumcnt += sumcnt 
                if not algo_bik or biq > algo_biq:
                    algo_biq = biq
                    algo_bik = bik
                if not algo_wik or wiq > algo_wiq:
                    algo_wiq = wiq
                    algo_wik = wik

        if algo_sumcnt>0:
            if VERBOSITY>0:
                print "---------------------------------------"
            print "Best and worst are from the best/worst configuration out of the tuning repetitions"
            absolute_imps_all_algos['best'].append(algo_biq)
            relative_imps_all_algos['best'].append(algo_biq/baselevel*100)
            print "Best %s improvement for %s by %s: %.2f (%.2f %% better than defaults)" % (avgfl,str((algo)), str(algo_bik), algo_biq, algo_biq/baselevel*100)
            absolute_imps_all_algos['worst'].append(algo_wiq)
            relative_imps_all_algos['worst'].append(algo_wiq/baselevel*100)
            print "Worst %s improvementfor %s by %s: %.2f (%.2f %% better than defaults)" % (avgfl,str((algo)), str(algo_wik), algo_wiq, algo_wiq/baselevel*100)
            algo_meanimp = algo_sumimprovement/algo_sumcnt
            absolute_imps_all_algos['mean'].append(algo_meanimp)
            relative_imps_all_algos['mean'].append(algo_meanimp/baselevel*100)
            print "Mean %s improvement for %s: %.2f (%.2f %% better than defaults)" % (avgfl,str((algo)), algo_meanimp, algo_meanimp/baselevel*100)
            algo_medianimp = scipy.median(algo_improvements)
            absolute_imps_all_algos['median'].append(algo_medianimp)
            relative_imps_all_algos['median'].append(algo_medianimp/baselevel*100)
            print "Median %s improvement for %s: %.2f (%.2f %% better than defaults)" % (avgfl,str((algo)), algo_medianimp, algo_medianimp/baselevel*100)
            if VERBOSITY>0:
                print "---------------------------------------"
                print
            print 
    
    print "*"*20
    for k in imp_keys:
        mai = scipy.mean(absolute_imps_all_algos[k])
        mri = scipy.mean(relative_imps_all_algos[k])
        print "Mean ", k, "for all algorithms  %.2f (%.2f %% better than defaults)" % (mai, mri)
    
    print "*"*20
    print
    print
    
    
    return gapdict
                
                    
                

        

def performance_compared_to_sampling(special_eval, data_folder, avgf="median", better_than=True, by=None):
    """
    by=None|'eb'|'algo'|'tuner'

    """
    
    uavgFunc = label_to_avgFunc(avgf)
    results,tuners,algos,ebs = _helper_read_evals(data_folder, special_eval, uavgFunc)    

    #tuners.remove("REVAC")
    #for a in ["VRPH RTR A", "VRPH SA A", "VRPH EJ A"]:
    #    if a in algos:
    #        algos.remove(a)
    #results = _filterResults(results, tuners, algos)
        
    sfms = calculateSignificances(results, algos)
    
    key_list = []
    label_list = []
    if by=='tuner-eb':
        for tuner in tuners:
            if tuner=="URS":
                continue       
            for eb in ebs:
                if eb<=1:
                    continue
                for algo in algos:
                    key_list.append( (tuner, algo, eb) )
                # signal to print counts
                key_list.append( (None,None,None) )
                label_list.append( str(tuner)+","+str(eb) ) 
    if by=='eb':
        for eb in ebs:
            if eb<=1:
                continue            
            for algo in algos:
                for tuner in tuners:
                    if tuner=="URS":
                        continue                    
                    key_list.append( (tuner, algo, eb) )
            # signal to print counts
            key_list.append( (None,None,None) )
            label_list.append( str(eb) ) 
            
    if by=='algo':
        for algo in algos:
            for eb in ebs:
                if eb<=1:
                    continue            
                for tuner in tuners:
                    if tuner=="URS":
                        continue                    
                    key_list.append( (tuner, algo, eb) )
            # signal to print counts
            key_list.append( (None,None,None) )
            label_list.append( str(algo) ) 
        
    if by=='tuner':
        for tuner in tuners:
            if tuner=="URS":
                continue       
            for algo in algos:
                for eb in ebs:
                    if eb<=1:
                        continue            
                    key_list.append( (tuner, algo, eb) )
            # signal to print counts
            key_list.append( (None,None,None) )
            label_list.append( str(tuner) ) 
    else:
         for algo in algos:
            for eb in ebs:
                if eb<=1:
                    continue            
                for tuner in tuners:
                    if tuner=="URS":
                        continue                    
                    key_list.append( (tuner, algo, eb) )
        
    total_nbrbtr = 0
    total_comparisons = 0 
    
    imc = 0
    imt = 0
    imi = 0
    for key in key_list:
        tuner, algo, eb = key
        
        # Signal for print intermediate results        
        if tuner==None and algo==None and eb==None:
            if imc!=0:
                print by, "=", label_list[imi], ":", ("%.2f" % (imt/float(imc)*100)), "%"
            imc = 0
            imt = 0
            imi+=1
            
        
        task_key=(tuner, algo, eb)
        urs_key=("URS", algo, eb)
        
        if (task_key not in sfms) or (urs_key not in sfms[task_key]):
            continue
        
        statistic, p_value = sfms[task_key][urs_key]

        if better_than:
            if results[task_key][2]<results[urs_key][2] and p_value<0.05:
                total_nbrbtr+=1
                imt+=1
                if VERBOSITY>0:
                    print task_key, ">", urs_key, "stat. better"
            else:
                if VERBOSITY>0:
                    print task_key, "=", urs_key, "stat. insificant"
        else: # not better_than, aka. not worse
            if results[task_key][2]>results[urs_key][2] and p_value<0.05:
                if VERBOSITY>0:
                    print task_key, "<", urs_key, "stat. worse"
            else:
                total_nbrbtr+=1
                imt+=1
                if VERBOSITY>0:
                    print task_key, "=", urs_key, "stat. insificant"
        
        total_comparisons+=1
        imc+=1
    return total_nbrbtr, total_comparisons
    
def number_of_times_beat_defaults(special_eval, data_folder, avgf="median", print_table=False):
    
    uavgFunc = label_to_avgFunc(avgf)               
    results,tuners,algos,ebs = _helper_read_evals(data_folder, special_eval, uavgFunc)
    minQ, maxQ, nmult = get_scaling_range("_"+special_eval, data_folder, scale_optimality_gap=True)
    nresults = normalizeQualities(results, minQ, maxQ, nmult)
    
    improvements_over_defaults = []
    
    total_nbrbtr = 0
    total_comparisons = 0 
    for algo in algos:
        per_algo_improvements_over_defaults = []
        per_algo_nbrbtr = 0
        per_algo_comparisions = 0
        for eb in ebs:
            if eb<=1:
                continue
                
            for tuner in tuners:
                task_key=(tuner, algo, eb)
                default_key=(DEFAULT[0], algo, 1)
                if task_key in nresults and default_key in nresults:
                    # unpack
                    (ar, mev, meq, seq, tpl, ql, evl ) = nresults[task_key]
                    dmeq = nresults[default_key][2]
                    
                    # Warning, the assumption of 10 paramter confs is made
                    nbrbtr = 0
                    for i in range(10):
                        #print len(ql[i*10:i*10+10])
                        if (i*10+10<len(ql)):
                            pseq = uavgFunc(evl, ql[i*10:i*10+10])[1]
                            # also store by how much 
                            per_algo_improvements_over_defaults.append( (dmeq-pseq)/dmeq*100.0 )
                            #print task_key, i, dmeq-pseq, "(", dmeq, ",",pseq,")"
                            
                            if pseq< dmeq:
                                nbrbtr += 1
                                total_nbrbtr += 1
                                per_algo_nbrbtr += 1
                            per_algo_comparisions += 1
                            total_comparisons += 1
                            
                    #print task_key, len(ql), nbrbtr

                    # repack
                    nresults[task_key] = (ar, mev, nbrbtr, [], tpl, ql, evl)
        
        improvements_over_defaults+=per_algo_improvements_over_defaults
        if not print_table and per_algo_comparisions!=0:
            print algo, special_eval, data_folder, per_algo_nbrbtr/float(per_algo_comparisions)*100, "%"
            print algo, special_eval, data_folder, scipy.mean(per_algo_improvements_over_defaults), "% points"
    
    if print_table:
        special_evals, special_evals_label = get_special_eval(special_eval)
        target = data_folder.capitalize()
        table_sbs = 1
        table_ebs = EBS+EXTRA_EBS
        tableLabel=data_folder+"_results_better_than_defaults_on"+special_evals+"_"+avgf
                    
        #tableTitle=r"""Tuning results for %s targets with %s. %s aggregated solution quality is normalized between best known and worst encountered result, where smaller value is better. %ss are listed in parentheses. Statistically better results are bolded. Evaluation budget (EB) violations of more than 15\%% are italicized.""" % (target, special_evals_label, avgf.capitalize(), sddevlabel.capitalize())
        tableTitle=r"""Number of times tuned parameters bested default %s results for %s targets with %s.""" % (avgf, target, special_evals_label)
        tableNotes=r"""Evaluation budget (EB) violations of more than 15\%% are italicized."""
        figgen.produceLatexTable(nresults,tableTitle, tableNotes, tableLabel, table_ebs, algos, tuners,
                                 sbs=table_sbs, warn_ebd=True, vert=True, printSd=False, printDefaultsRow=False)
        
    return total_nbrbtr, total_comparisons, scipy.mean(improvements_over_defaults)
    #print
    #print "TOTAL", special_eval, data_folder, total_nbrbtr/float(total_comparisons)*100, "%"
    #print

def tuner_robustness_by_mad(special_eval, data_folders, avgf="median"):   
    uavgFunc = label_to_avgFunc(avgf)               

    tuner_utility_variations = {}
    for tuner in TUNERS:  
        tuner_utility_variations[tuner] = []

    for data_folder in data_folders:
        results,tuners,algos,ebs = _helper_read_evals(data_folder, special_eval, uavgFunc)
        minQ, maxQ, nmult = get_scaling_range("_"+special_eval, data_folder, scale_optimality_gap=True)
        nresults = normalizeQualities(results, minQ, maxQ, nmult)
                
        for tuner in tuners:  
            for algo in algos:
                for eb in ebs:
                    if eb<=1:
                        continue
                    task_key=(tuner, algo, eb)
                    if task_key in nresults:
                        # unpack
                        (ar, mev, meq, seq, tpl, ql, evl ) = nresults[task_key]
                        tuner_utility_variations[tuner].append(seq)
    
    sorted_by_variation = list( tuner_utility_variations.items() )
    sorted_by_variation.sort(key=lambda x: scipy.mean(x[1]))
    for tuner, tuv in sorted_by_variation:
        print "Mean utility variation on", special_eval, "for", tuner, scipy.mean(tuv)

def tuner_rankings(special_eval, data_folder, avgf="median"):
    uavgFunc = label_to_avgFunc(avgf)               
    results,tuners,algos,ebs = _helper_read_evals(data_folder, special_eval, uavgFunc)
    minQ, maxQ, nmult = get_scaling_range("_"+special_eval, data_folder, scale_optimality_gap=True)
    nresults = normalizeQualities(results, minQ, maxQ, nmult)
    
    for algo in algos:
        print algo, "on", special_eval
        for eb in ebs:
            tuner_mql = []
            for tuner in TUNERS: 
                task_key=(tuner, algo, eb)
                if not task_key in nresults:
                    continue
                
                (ar, mev, meq, seq, tpl, ql, evl ) = nresults[task_key]
                tuner_mql.append((meq, tuner))
            if tuner_mql:
                tuner_mql.sort()
                meqss, tunerss = zip(*tuner_mql)
                pointsl = zip(meqss, tunerss, range(1,len(tuner_mql)+1))
                pointsl.sort(key=lambda x: x[1]) #by tuner (alphabetical)
                print "\t","\t".join( [str(x[1]) for x in pointsl] )
                print eb, "\t"+"\t".join( [str(x[2]) for x in pointsl] )
        print


def parse_cmd_arguments():
    parser = argparse.ArgumentParser(description='A script to produce high level results from the tuning results.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', help='Output verbosity', dest='verbosity', type=int, default=0)
    parser.add_argument('-btu', help='Compare tuner performance to URS (better than)', dest='better_than_urs', action='store_true')
    parser.add_argument('-nwu', help='Compare tuner performance to URS (not worse than)', dest='not_worse_than_urs', action='store_true')
    parser.add_argument('-cog', help='Calculate how much optimality gap was closed', dest='closed_gap', action='store_true')
    parser.add_argument('-tec', help='Produce additional for the above uses tuner-eb -combinations', dest='tuner-eb_urs', action='store_true')
    parser.add_argument('-btd', help='Compare tuned configuration performance to Defaults', dest='against_defaults', action='store_true')    
    parser.add_argument('-tvd', help='Produce table of tuned configuration performance to Defaults', dest='table_vs_defaults', action='store_true')
    parser.add_argument('-tro', help='Estimate tuner robustness by producing mean MAD per tuner', dest='tuner_robustness', action='store_true')
    parser.add_argument('-tra', help='Show tuner rankings per tuning task in an ascii table', dest='tuner_rankings', action='store_true')
    return vars(parser.parse_args())
    
if __name__ == "__main__":
    args = parse_cmd_arguments()
    VERBOSITY = args['verbosity']    
    bys = ['eb','tuner', 'algo']
    if args['tuner-eb_urs']:
        bys.append('tuner-eb')
        
    
    for se in SPECIAL_EVALS:#[1:]:
        all_mean_closed = []
        all_median_closed = []
        
        total_total_nbrbtr = 0
        total_total_comparisons = 0
        total_total_improvement_od = 0.0
        for t in FOLDERS:
            
            ase=se
            #quickfix for missing testset on christofides (results shown twice)
            if (not "3cv" in t) and ("test" in se) and (t=="christofides"):
                ase = "we"
            
            tn = 0
            tc = 0
            
            if args['tuner_rankings']:
                tuner_rankings( ase, t )
            

            if args['closed_gap']:
                for avgfl in ['mean', 'median', 'best', 'worst']:
                    gapdict = calculate_optimality_gap_close(ase, t, avgfl)
                    if avgfl=='mean':
                        all_mean_closed+=gapdict.values()
                    if avgfl=='median':
                        all_median_closed+=gapdict.values()

            if args['better_than_urs']:
                for by in bys:
                    print t, ase
                    tn, tc = performance_compared_to_sampling(ase, t, by=by, better_than=True)
                    if tc>0:
                        print "subtotal:",  ("%.2f" % (tn/float(tc)*100)), "%"
                        print
            if args['not_worse_than_urs']:
                for by in bys:
                    print t, ase
                    tn, tc = performance_compared_to_sampling(ase, t, by=by, better_than=False)
                    if tc>0:
                        print "subtotal:",  ("%.2f" % (tn/float(tc)*100)) , "%"
                        print
            
            if args['against_defaults']:
                tn, tc, im = number_of_times_beat_defaults(ase, t, print_table=False)
                total_total_improvement_od += im*tc
            
            if args['table_vs_defaults']:
                tn, tc = number_of_times_beat_defaults(ase, t, print_table=True)
                
            
                
            total_total_nbrbtr+=tn
            total_total_comparisons+=tc
            
        if args['tuner_robustness']:
                tuner_robustness_by_mad(ase, FOLDERS)
                
        if args['against_defaults']:
            print "TOTAL improvement over defaults on", se, ":", ("%.2f" % (total_total_improvement_od/total_total_comparisons)), "%"          
        if total_total_comparisons>0:
            print "TOTAL on", se, ":",  ("%.2f" % (total_total_nbrbtr/float(total_total_comparisons)*100)), "%"
            print "=============="+"="*len(se)
            print        
            
        if args['closed_gap']:
            #print all_mean_closed
            print "Mean closed mean gap on", se, ":",  scipy.mean(all_mean_closed), "%"
            print "Mean closed median gap on", se, ":",  scipy.mean(all_median_closed), "%"
            print "========================="+"="*len(se)
            print 
    
    
    
    