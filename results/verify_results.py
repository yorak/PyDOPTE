# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 20:27:13 2012

@author: juherask

This file has routines that do all kinds of validation for tuning results.
See the function documentations for more info.
"""

import glob
#from evaluate_results import evaluate_results        
import os
import argparse
import difflib
from pprint import pprint
    

from collections import defaultdict
from parse_results import parseEvalsFromFiles, parseResultsFromFiles
from parse_results import medianFunc,meanFunc,bestFunc,worstFunc
from helpers import MAX_FLOAT, module_exists, list_Z_outliers, remove_outliers

if module_exists("scipy"):
    import scipy
    from scipy.stats import mannwhitneyu
if module_exists("statlib"):
    from statlib.stats import kruskalwallish
    import statlib.stats as stats

AVFGS = {medianFunc,meanFunc,bestFunc,worstFunc}        
SPECIAL_EVALS = ["we", "testset"]
FOLDERS = [
    #"augerat",
    "iridia",
    #"christofides"
    ]
EVAL_FILES = "evals_*%s.txt" 
RESULT_FILES = "result_*repts.txt"
OUTLIER_DETECT = 10.0 #smaller is more strict

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


def _get_closest_match(word, possibilities):
    def similarity(seq1, seq2):
        return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()
    
    bestsim = 0.0
    bestmatch = ""
    for p in possibilities:
        sim = similarity(word, p)
        #print sim, word, p
        if sim > bestsim:
            bestsim = sim
            bestmatch = p
    
    return bestmatch

def _list_all_result_files():
    for evals_folder in FOLDERS:
        files = os.path.join(evals_folder, RESULT_FILES)
        for evalFile in glob.glob(files):
            yield evalFile
        
def _list_all_evals_files(postfix=""):
    """ Postfix should start with "_"
    """
    eval_files = EVAL_FILES % postfix
    for evals_folder in FOLDERS:
        files = os.path.join(evals_folder, eval_files)
        for evalFile in glob.glob(files):
            yield evalFile

def _list_alt_file_pairs():  
    alt_files = "alt_*.txt"
    afl = list(glob.glob(alt_files))
    efl = list(_list_all_evals_files())
    rfl = list(_list_all_result_files())
    
    pairs = []
    for af in afl:
        of = _get_closest_match(af.replace("alt_", ""), efl+rfl)
        pairs.append( (af, of) )
    return pairs

def _check_result_similarity(first_results, second_results):
    for key1 in first_results:
        #unpack 
        print key1
        (ar1, mev1, meq1, seq1, tpl1, ql1, evl1 ) = first_results[key1]     
        (ar2, mev2, meq2, seq2, tpl2, ql2, evl2 ) = second_results[key1]     
        
        # Check that these come from the same distribution
        # (statistic, p_value) 
        
        #pprint(ql1)
        #pprint(ql2)
        print( "mean, stdev", stats.mean(ql1), stats.stdev(ql1) )
        print( "mean, stdev", stats.mean(ql2), stats.stdev(ql2) )
        print "kruskalwallish", kruskalwallish(ql1, ql2)
        print "mannwhitneyu", mannwhitneyu(ql1, ql2)
        print

def _get_eval_results(evaluations, do_remove_outliers):
    evalq_results = []

    to_opt_repeats = {}

    ## 1. ITERATE TUNING TASKS
    for task_key, tuning_task_evaluations in evaluations.items():        
        ## 2. ITERATE PARAMETER CONFIGURATIONS OF A TUNING TASK
        for ps_idx, repeats in tuning_task_evaluations.items():
            ## 3. ITERATE EVALUATION REPETITIONS OF A TASK AND OF A PARAMETER SET
            for repetition in repeats:
                benchmark_q = 0.0
                at_opt_c = 0
                for evaluation in repetition:
                    payload = evaluation
                    #unpack (tuned_ps_idx,benchmark_name,instance_quality,ps_actual_evals,ps_hash)
                    (ps_idx,instance_name,q,ps_evals,ps_hash) = payload
                    benchmark_q += q
                    if instance_name in best_known and q-BEST_CMP_TOL<=best_known[instance_name]:
                        at_opt_c += 1
                        
                    if at_opt_c==14:
                        print task_key, ps_idx
                        
                        
                evalq_results.append(benchmark_q)
                if at_opt_c > int(BEST_CMP_RAPORT_THLD*len(repetition)):
                    optkey = task_key+(at_opt_c, len(repetition))
                    if optkey not in to_opt_repeats:
                        to_opt_repeats[optkey]=0
                    to_opt_repeats[optkey]+=1

    for optkey, cnt in to_opt_repeats.items():
        print optkey[:3], "%d/%d to opt (%d times)" % (optkey[3], optkey[4], cnt)
        
    if len(evalq_results)>0 and do_remove_outliers:
        noutliers = list_Z_outliers(evalq_results, OUTLIER_DETECT)
        if len(noutliers)>0:
            print "Removed  %d outliers" % (len(noutliers))
        
        return remove_outliers(evalq_results, OUTLIER_DETECT)
    else:
        return evalq_results
        
def _get_evalq_per_instance(evaluations, do_remove_outliers):
    evalq_per_instance = defaultdict(list)
        
    ## 1. ITERATE TUNING TASKS
    for task_key, tuning_task_evaluations in evaluations.items():        
        ## 2. ITERATE PARAMETER CONFIGURATIONS OF A TUNING TASK
        for ps_idx, repeats in tuning_task_evaluations.items():
            ## 3. ITERATE EVALUATION REPETITIONS OF A TASK AND OF A PARAMETER SET
            for repetition in repeats:
                for evaluation in repetition:
                    payload = evaluation
                    #unpack (tuned_ps_idx,benchmark_name,instance_quality,ps_actual_evals,ps_hash)
                    (ps_idx,instance_name,q,ps_evals,ps_hash) = payload
                    evalq_per_instance[instance_name].append(q)
           
    if do_remove_outliers:
        no_evalq_per_instance = {}
        for instance, ql in evalq_per_instance.items():
            noutliers = list_Z_outliers(ql, OUTLIER_DETECT)
            if len(noutliers)>0:
                print "Removed  %d outliers from %s" % (len(noutliers), instance)
            no_evalq_per_instance[instance] = remove_outliers(ql, OUTLIER_DETECT)
        return no_evalq_per_instance
    else:
        return evalq_per_instance
    
def verify_result_file_similarity(first, second):
    print "Alternative data:"
    print first
    print second
    first_results = parseResultsFromFiles(first, None)
    second_results = parseResultsFromFiles(second, None)
    #pprint( first_results )
    #pprint( second_results.keys() )
    print
    _check_result_similarity(first_results, second_results)
    print 


def verify_evals_file_similarity(first, second):
    print "Alternative data:"
    print first
    print second
    first_results = parseEvalsFromFiles(first, None, False)
    second_results = parseEvalsFromFiles(second, None, False)
    print
    #pprint( first_results )
    #pprint( second_results.keys() )
    _check_result_similarity(first_results, second_results)
    print 

def print_best_worst_q_for_tuningruns(data_folder, do_remove_outliers=False):
    
    print "Verifying results in %s" % (data_folder)
    seekpath = os.path.join(data_folder, RESULT_FILES)
    results = parseResultsFromFiles(seekpath, medianFunc)
    
    mql = []
    for key, payload in results.items():
        (ar, mev, meq, seq, tpl, ql, evl ) = payload
        if do_remove_outliers:
            noutliers = list_Z_outliers(ql, OUTLIER_DETECT)
            if len(noutliers)>0:
                print "Removed  %d outliers from %s" % (len(noutliers), key)
            mql += remove_outliers(ql, OUTLIER_DETECT)
        else:
            mql += ql
    print min(mql), max(mql)
    print
        
def print_best_worst_q_for_evaluations(data_folder, special_eval, do_remove_outliers=False):
    
    print "Verifying evals %s in %s" % (special_eval, data_folder)
    
    eval_files = EVAL_FILES % special_eval                 
    seekpath = os.path.join(data_folder, eval_files)
    print seekpath
    #  evaluations[key][tuned_ps_idx].append([])
    evaluations = parseEvalsFromFiles(seekpath, medianFunc, True)
    
    # Organize evaluations per instancefile
    evalq_per_instance = _get_evalq_per_instance(evaluations, do_remove_outliers)
    evalq_results = _get_eval_results(evaluations, do_remove_outliers)
    
    if len(evalq_per_instance.keys())==0 or len(evalq_results)==0:
        return
    
    totalworst = max(evalq_results)
    totalbest = min(evalq_results)
    
    
    # Make sure right number of instances (and right instances are used)
    print "DEBUG: ", str(evalq_per_instance.keys())
    assert(len(evalq_per_instance)==14)

    
    theoreticalbest = 0.0
    theoreticalworst = 0.0
    for instance_name, ql in evalq_per_instance.items():        
        fql = [q for q in ql if q!=2147480000.0]
        print instance_name, min(fql), max(fql)
        theoreticalbest+=min(ql)    
        theoreticalworst+=max(ql)
     
    print "encountered min: ",  totalbest, "max: ", totalworst
    print "theoretical min: ",  theoreticalbest, "max: ", theoreticalworst
    print
  

def find_evals_outliers(data_folder, special_eval):
    print "Detecting outliers %s in %s" % (special_eval, data_folder)
    eval_files = EVAL_FILES % special_eval                 
    seekpath = os.path.join(data_folder, eval_files)
    print seekpath
    #  evaluations[key][tuned_ps_idx].append([])
    evaluations = parseEvalsFromFiles(seekpath, medianFunc, True)    
    evalq_per_instance, totalbest, totalworst = _get_evalq_per_instance(evaluations, False)
    
    for instancename, ql in evalq_per_instance.items():
        print instancename,
        outliers = list_Z_outliers(ql, OUTLIER_DETECT )        
        if len(outliers)>0:
            print ", outliers (mean=%f):" % stats.mean(ql), set(outliers)
        else:
            print ", outliers: None"
         
    
def find_result_outliers(data_folder):
    print "Detecting outliers in %s" % (data_folder)
    seekpath = os.path.join(data_folder, RESULT_FILES)
    results = parseResultsFromFiles(seekpath, medianFunc)
    
    targets = set()
    for key in results.keys():
        targets.add(key[1])
    
    for target in targets:
        mql = []
        for key, payload in results.items():
            (ar, mev, meq, seq, tpl, ql, evl ) = payload
            mql+=ql
       
        outliers = list_Z_outliers(mql, OUTLIER_DETECT )
        if len(outliers)>0:
            print "outliers (mean=%f) for " % stats.mean(mql), target, set(outliers)
            




def parse_cmd_arguments():
    parser = argparse.ArgumentParser(description='A script containing a collection of tuning result verification routines.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', help='Calculate min/max values for the results and evaluations', dest='minmax', action='store_true')
    parser.add_argument('-mro', help='Calculate min/max values for the results and evaluations BUT remove outliers', dest='minmax_wo_outliers', action='store_true')
    parser.add_argument('-a', help='Compare statistically the .//alt_* result and evals files against the ones in the result folder structure', dest='alt_results', action='store_true')
    parser.add_argument('-oe', help='Find outliers from the evaluations data', dest='evals_outliers', action='store_true')
    parser.add_argument('-or', help='Find outliers from the evaluations data', dest='result_outliers', action='store_true')
    return vars(parser.parse_args())
    
def main():

    ## PARSE CMD LINE ##
    args = parse_cmd_arguments()
        
    ## VERIFICATIONS ##      
    
    if args["alt_results"]:
        for pair in _list_alt_file_pairs():
            if "result_" in pair[1]:
                verify_result_file_similarity(pair[0], pair[1])
            elif "evals_" in pair[1]:
                verify_evals_file_similarity(pair[0], pair[1])
    
    if args["minmax"] or args['minmax_wo_outliers']:
        do_remove_outliers = args['minmax_wo_outliers']
        for data_folder in FOLDERS:
            for special_eval in SPECIAL_EVALS:
                print_best_worst_q_for_evaluations(data_folder, special_eval, do_remove_outliers )
            print_best_worst_q_for_tuningruns(data_folder, do_remove_outliers )
    
    if args["evals_outliers"]:
        for data_folder in FOLDERS:
            for special_eval in SPECIAL_EVALS:
                find_evals_outliers(data_folder, special_eval)
                print
                
    if args["result_outliers"]:
        for data_folder in FOLDERS:
            find_result_outliers(data_folder)
            print
    
if __name__ == "__main__":
    main()
    #cvrp_we_to_testset()
