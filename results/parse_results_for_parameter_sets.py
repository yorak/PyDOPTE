# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 09:48:16 2015

@author: juherask

This script is used to get the parameter set together with
the mean / median / best / worst etc. result
"""

from parse_results import ALGO_GROUP, ALGO_GROUP_RESULT_SUBFOLDERS, CACHE_FOLDER, TUNERS
from parse_results import VERBOSE
from parse_results import label_to_avgFunc, get_special_eval, get_scaling_range
from parse_results import parseResultsFromFiles, parseEvalsFromFiles, normalizeQualities
from collections import defaultdict
from pprint import pprint
from random import choice
from helpers import *
from numpy import median,mean
import numpy as np
import os
import pickle
import operator


                
selection_method = "with_best_median"
#"median_of_medians" / "with_best_median" / "median_over_all" / "with_best_single"
avgf = "median"

data_source = "Evals_testset"

USE_CACHE = False
WRITE_CACHE = True
NORMALIZE = True
RANGES_WITHOUT_OUTLIERS = False
RANGES_PERCENTAGE_OPT = True
REPEATS = 10
VERBOSE = 1

#TUNERS = ["Defaults"]

PRINT_TOP_N = False # True
N = 5 # 3



def mad(arr):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variabililty of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation 
    """
    arr = np.ma.array(arr).compressed() # should be faster to not use masked arrays.
    med = median(arr)
    return median(np.abs(arr - med))
    
rresults = {}
eresults = {}

cachefilen = "results_with_tpss_cache_%s_%s.pickle" % (data_source, selection_method+"_with_"+avgf)
cachefilepath = os.path.join(CACHE_FOLDER, cachefilen)
if USE_CACHE:
    print "Reading from pickled..."
    pfile = open( cachefilepath, 'rb' )
    eresults = pickle.load( pfile )
    pfile.close()
    print "..done"
else:
    print "Reading from files..."
    for ag in ALGO_GROUP:
        uavgFunc = label_to_avgFunc(avgf)
        special_evals, special_evals_label, special_evals_short_label = \
            get_special_eval(data_source)
        
        data_folder = ALGO_GROUP_RESULT_SUBFOLDERS[ag]    
    
        isCV = False
        # TODO: This is QUCIKFIX. Find a better way to find out it is cross 
        #  validation file
        if "_3cv" in data_folder:
            isCV = True
            
        # == Load results data from files ==    
        seekpath = os.path.join(data_folder, "result_*repts*.txt")
        print seekpath
        
        
        results = parseResultsFromFiles(files=seekpath, avgFunc=uavgFunc, crossValidation=isCV)
        rresults.update( results )
            
        # == Load evaluations data from files ==    
        
                
        #Ugly quickfix. Christofides does not have test set.
        if isCV and ag=="VRPH_CHRISTOFIDES":
            seekpath = os.path.join(data_folder, "evals_*_fullset.txt")
            print seekpath
            results = parseEvalsFromFiles(files=seekpath, avgFunc=uavgFunc, results_with_pcs=rresults)            
        elif not isCV and ag=="VRPH_CHRISTOFIDES" and special_evals=="_testset":
            seekpath = os.path.join(data_folder, "evals_*.txt")
            print seekpath
            results = parseEvalsFromFiles(files=seekpath, avgFunc=uavgFunc, results_with_pcs=rresults)
        else:
            seekpath = os.path.join(data_folder, "evals_*"+special_evals+".txt")
            print seekpath
            results = parseEvalsFromFiles(files=seekpath, avgFunc=uavgFunc, results_with_pcs=rresults)
        
        if NORMALIZE:
            minQ, maxQ, nmult = get_scaling_range(special_evals, ag, RANGES_WITHOUT_OUTLIERS, RANGES_PERCENTAGE_OPT)
            nresults = normalizeQualities(results, minQ, maxQ, nmult)
            eresults.update( nresults )
        else:
            eresults.update( results )
        
    if WRITE_CACHE:
        print "..and pickling..."
        pfile = open( cachefilepath, 'wb' )
        pickle.dump( eresults, pfile )
        pfile.close()
    print "..done"

print "the database contains", len(eresults), "results"

# == Output cache == 
tuned_for_target = defaultdict(list)
for key, payload in eresults.items():
    tuner, target, eb = key
    #if " C" in target:
    #    continue
    if tuner in TUNERS:
        (ar, mev, meq, seq, tpl, ql, evl ) = payload
        #print key, len(tpl), len(ql)
        #pprint( tpl )
        #pprint( ql )
        #break
        print key, "%.2f" % meq, "(%.2f)" % seq
        
        for qi, q in enumerate(ql):            
            if selection_method=="median_of_medians" or selection_method=="with_best_median":
                if (qi%REPEATS==REPEATS-1):
                    median_over_pt_repeats = median(ql[qi-REPEATS+1:qi+1])
                    mad_over_pt_repeats = mad(ql[qi-REPEATS+1:qi+1])
                    tuned_for_target[target].append( (median_over_pt_repeats, mad_over_pt_repeats, tpl[qi/REPEATS], key ) )
                    
            elif selection_method=="median_over_all" or selection_method=="with_best_single":
                tpidx = qi/REPEATS
                mad_over_pt_repeats = mad(ql[tpidx * REPEATS:(tpidx+1) * REPEATS])
                tuned_for_target[target].append( (q, mad_over_pt_repeats, tpl[tpidx], key ) )
        
#target = tuned_for_target.keys()[0]
#aql, aqtpl = zip(*tuned_for_target[target])
#print target, aql[0], aqtpl[0]
#quit()

for target in tuned_for_target:
    aql, madql, aqtpl, keys = zip(*tuned_for_target[target])
    
    midx = None
    if selection_method=="median_over_all" or selection_method=="median_of_medians":
        midxs = median_idxs(aql)
        midx = choice(midxs)
        median_val = sum( (aql[idx] for idx in midxs) )/len(midxs)
        
        if PRINT_TOP_N:
            d_to_median = [ (i, abs(median_val-q)) for i, q in enumerate(aql)]
            closest_list = sorted(d_to_median, key=operator.itemgetter(1))
        
    elif selection_method=="with_best_single" or selection_method=="with_best_median":
        #if BEST_OF_PSQ_MEDIANS:
        #    pass
        #else:
        midx, _ = min(enumerate(aql), key=operator.itemgetter(1))
        #print midx, aql[midx], keys[midx]
        
        if PRINT_TOP_N:
            closest_list = sorted(list(enumerate(aql)), key=operator.itemgetter(1))
    
    if PRINT_TOP_N:
        print "TOP%d for "%N, target, ":"
        for i in range(N):
            top_idx = closest_list[i][0]
            print ";".join([str(target) + " " + str(i+1),keys[top_idx][0], str(aql[top_idx]), str(madql[top_idx]), str(aqtpl[top_idx])])
        print
    else:
        print ";".join( [str(target), str(aql[midx]), str(madql[midx]), keys[midx][0], str(aqtpl[midx])] ) 
    #print
    
             #(ar, mev, meq, seq, tpl, ql, evl ) = results_with_parameter_configurations[task_key]
             #(ar_per_fold, rl, fl, mev, meq, seq, tpl, ql, evl, ctsl, cvsl ) = results_with_parameter_configurations[task_key]
    # TODO: Get all tuned results (excluding Defaults)
    #  take the median tp?
    #result = (ar, mev, meq, seq, tpl, ql, evl )

#print eresults.keys()
#print eresults[eresults.keys()[3]]
    
