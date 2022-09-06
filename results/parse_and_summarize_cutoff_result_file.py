# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 12:09:03 2016

@author: juherask
"""

from plot_cutoff_results import read_and_validate, _extract_datapoints_from_results, TARGETS
from parse_results import get_scaling_range
from numpy import mean, median
import numpy as np
from collections import defaultdict

ARGF = median #min, max, mean
FILE = "highlevel/evaluations_best_median_parameter_set_quality_10r.csv"
FILE = "eval_top5_vrpsd-sa_ej-c.txt"

# In some cases a cutoff result file was used to contain results of several parameter set repetitions.
pm_count = 1

    
if __name__=="__main__":
    r = read_and_validate([FILE])
    results = r["N/A"]
    #print results.keys()
    
    for target in TARGETS:
        target = target.replace("acs", "aco")
        ftarget=target+"_testset"

        if ftarget in results:
            minQ, maxQ, multiplierQ = get_scaling_range("_testset", target, False, True)    
            exv, eyv, qxv, qyv = _extract_datapoints_from_results(results[ftarget], ARGF, minQ, maxQ, multiplierQ)        
            
            print target, "%.2f"%qyv[0]
            
            # Check if there is (possibly) multiple parameter sets
            pmc = len(results[ftarget][10.0])/10
            if pmc>1:
                pm_count = pmc
                
    if pm_count>1:
        print     
        for target in TARGETS:
            ## Initialize data structure/ FOR REFERENCE ##
            # target -> cutoff -> repeat -> payload (benchmark_name, q, wall_time)
            results_per_pm = defaultdict( # key = target (str)
                    lambda: defaultdict( # key = cutoff (float)
                        lambda: defaultdict( # key = repeat idx (int)
                            lambda: list() #list of all instance evaluations
                )))  
                
            target = target.replace("acs", "aco")
            ftarget=target+"_testset"
    
            if ftarget in results:
                for pmid in range(pm_count):
                    results_per_pm[ftarget][10.0] = dict(
                        [(rptid%10, payload) for
                          rptid, payload in results[ftarget][10.0].items()
                          if (rptid>pmid*10 and rptid<pmid*10+10)])
                    #print ftarget, results_per_pm[ftarget].items(), len(results_per_pm[ftarget][10.0])
                    minQ, maxQ, multiplierQ = get_scaling_range("_testset", target, False, True)    
                    exv, eyv, qxv, qyv = _extract_datapoints_from_results(results_per_pm[ftarget], ARGF, minQ, maxQ, multiplierQ)        
                    
                    print target, "ps", pmid, "of top%d"%pm_count, "%.2f"%qyv[0]
                    print str( [sum(i[1] for i in results_per_pm[ftarget][10.0][k]) for k in results_per_pm[ftarget][10.0].keys()] )
        