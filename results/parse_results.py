#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:40:25 2011

@author: juherask
"""

import ast
import glob
import os
import sys
import os.path
import argparse
import re
import pickle
from helpers import *
from collections import OrderedDict
from math import sqrt
import figgen
import PathManager

if module_exists("pylab"):
    from pylab import rcParams

if module_exists("scipy"):
    import scipy
    from scipy.stats import mannwhitneyu

if module_exists("statlib"):
    from statlib.stats import kruskalwallish
    
    
    
#os.chdir("")

DEFAULT = ["Defaults"]
TUNERS = ["CMAES", "GGA", "IRace", "ParamILS", "REVAC", "SMAC", "URS"] #"URSwR",
VRPH_CHRISTOFIDES_ALGOS = ["VRPH RTR C", "VRPH SA C", "VRPH EJ C"]
VRPH_AUGERAT_ALGOS = ["VRPH RTR A", "VRPH SA A", "VRPH EJ A"]
VRPH_ALGOS = VRPH_CHRISTOFIDES_ALGOS + VRPH_AUGERAT_ALGOS
VRPSD_ALGOS = ["VRPSD ACO", "VRPSD EA",  "VRPSD ILS", "VRPSD TS", "VRPSD SA"]
ALGOS = VRPH_CHRISTOFIDES_ALGOS+VRPH_AUGERAT_ALGOS+VRPSD_ALGOS
EBS = [100, 500, 1000]
EXTRA_EBS = [5000]
EXTRA_EBS_ALGOS = ["VRPSD ACO"] #,"VRPH SA C"]

## ENABLE THESE TO PARSE "FEATURES" data
#ALGOS = VRPH_AUGERAT_ALGOS
#EXTRA_EBS = []
#TUNERS = ["SMAC", "fSMAC", "IS-fSMAC"]
#EXTRA_EBS_ALGOS = []
#ALGO_GROUP = ["VRPH_AUGERAT"] SUPPRESS THE VARIABLE BELOW

TGT_REPTS = 10
TGT_REPTS_CV = 5
CV_FOLDS = 3
VERBOSE = 0
JOURNALSTYLE = True
RG75_STYLE = False


## Which algo groups to load (this can be modified)
#ALGO_GROUP = ["VRPH_C_ALGOS"]
#ALGO_GROUP = ["VRPH_AUGERAT"]
#ALGO_GROUP = ["VRPSD_ALGOS"]
ALGO_GROUP = [ "VRPH_CHRISTOFIDES", "VRPH_AUGERAT", "VRPSD_IRIDIA"] #

ALGO_GROUP_RESULT_SUBFOLDERS = {
     "VRPH_CHRISTOFIDES":"christofides_3cv",
	"VRPH_AUGERAT":"augerat_reruns",
    ## ENABLE THIS TO PARSE "FEATURES"
	#"VRPH_AUGERAT":"features",
    "VRPSD_IRIDIA":"iridia_reruns"} 
     
ALGO_GROUP_ALGOS = {
     "VRPH_CHRISTOFIDES":VRPH_CHRISTOFIDES_ALGOS,
     "VRPH_AUGERAT":VRPH_AUGERAT_ALGOS,
     "VRPSD_IRIDIA":VRPSD_ALGOS} 
     

# Use ranges that do not contain outliers
RANGES_WITHOUT_OUTLIERS = False #True
# Normalize to give % from the best known problem (optimality gap)
RANGES_PERCENTAGE_OPT = True 

PRODUCE_PER_TUNER_PARALLEL_PLOTS = False
PRODUCE_MAD_MEDIANS = False
    
CACHE_FOLDER = "cache"

PLOT_OUTPUT_SUBDIR = "plots"
AUTO_SCALE_GRAPHS = True
SCATTER_FOR_TARGETS = [] #["VRPSD TS"]
SCATTER_FOR_EBS = [1000]
SCATTER_PARAMETERS = ["-pt", "-po", "-ttf"]

WARNING_EVALUATIONS_DIFF = 0.05 #0.15

NAME_TRANSLATIONS = {\
"default":"Defaults",
"rt":"URSwR",
"RT":"URSwR",
"random":"URSwR",
"randomtuner":"URSwR",
"random tuner":"URSwR",
"rtnr":"URS",
"RTnR":"URS",
"urs":"URS",
"paramils":"ParamILS",
"cma-es":"CMAES",
"cmaes":"CMAES",
"gga":"GGA",
"irace":"IRace",
"revac":"REVAC",
"smac":"SMAC",

"vrphrtr":"VRPH RTR",
"vrphsa":"VRPH SA",
"vrphej":"VRPH EJ",

"vrphrtrc":"VRPH RTR C",
"vrphsac":"VRPH SA C",
"vrphejc":"VRPH EJ C",

"vrphchristofidesrtr":"VRPH RTR C",
"vrphchristofidessa":"VRPH SA C",
"vrphchristofidesej":"VRPH EJ C",

"vrphaugeratrtr":"VRPH RTR A",
"vrphaugeratsa":"VRPH SA A",
"vrphaugeratej":"VRPH EJ A",

"vrphrtra":"VRPH RTR A",
"vrphsaa":"VRPH SA A",
"vrpheja":"VRPH EJ A",

"vrphrtrrwF-n45":"VRPH RTR RW F-n45",
"vrphrtrrwF-n72":"VRPH RTR RW F-n72",
"vrphrtrrwF-n135":"VRPH RTR RW F-n135",
"vrphrtrrwRT385":"VRPH RTR RW RT-385",
"vrphsarwF-n45":"VRPH SA RW F-n45",
"vrphsarwF-n72":"VRPH SA RW F-n72",
"vrphsarwF-n135":"VRPH SA RW F-n135",
"vrphsarwRT385":"VRPH SA RW RT-385",
"vrphejrwF-n45":"VRPH EJ RW F-n45",
"vrphejrwF-n72":"VRPH EJ RW F-n72",
"vrphejrwF-n135":"VRPH EJ RW F-n135",
"vrphejrwRT385":"VRPH EJ RW RT-385",

"vrpsdacs":"VRPSD ACO",
"vrpsdaco":"VRPSD ACO",
"vrpsdea":"VRPSD EA",
"vrpsdts":"VRPSD TS",
"vrpsdsa":"VRPSD SA",
"vrpsdils":"VRPSD ILS",

"fsmac":"fSMAC",
"is-smac":"IS-fSMAC",
"is-fsmac":"IS-fSMAC",
}

reTuningTask = re.compile("(.*) tuning (.*)_Algorithm,.*({.*})")
reFoldLine = re.compile(r"([0-9]+)/([0-9]+) fold")
reEvalsInFileName = re.compile(r"_([0-9]+)eval")
reReptsInFileName = re.compile(r"_([0-9]+)rept")

# Tuners and algos in alphabetical order for output
#TUNERS.sort()
VRPH_CHRISTOFIDES_ALGOS.sort()
VRPH_AUGERAT_ALGOS.sort()
VRPSD_ALGOS.sort()
ALGOS.sort()

def _filterResults(results, only_tuners=None, only_algos=None, only_ebs=None):
    """ Get a filtered version of results data. If only_=None, then that
    specific filter is not used
    """
    # Use ordered dict to get nice ordering in graphs
    filtered_results = OrderedDict() 
    for algo in ALGOS:
        for tuner in DEFAULT+TUNERS:        
            for eb in [1]+EBS+EXTRA_EBS:
                key = (tuner, algo, eb)
                
                if ((key in results) and
                    (not only_tuners or tuner in only_tuners) and
                    (not only_algos or algo in only_algos) and
                    (not only_ebs or eb in only_ebs)):
                     filtered_results[key]=results[key]
    
    return filtered_results
        
    
def _getMinMaxResults(results, selector, remove_outliers_per_test=True, remove_outliers_from_all=False):
    """
    Returns the (min,max) of the results values using the selector function to 
     pick the payload we are interested in. 
    
    Optionally outlier detection and removal can be done before minmax:
     remove_outliers_from_all, remove_outliers_per_test
     where 'from_all' combines all results and then removes outliers and
     where 'from_test' does the outlier detection by test basis (more conservative)
    """
    
    allval = []
    testval = []
    for key in results:
        # Unpack
        val = selector( results[key] )
        try:
            testval.extend(val)
        except TypeError:
            testval.append(val)
            
        if remove_outliers_per_test and len(testval)>3:
            allval+=remove_outliers(testval, nsigma=10.0)
        else:
            allval+=testval
                    
    if remove_outliers_from_all and len(allval)>3:
        allval = remove_outliers(allval, nsigma=10.0)
        
    return min(allval),max(allval)

def _exportGraphs(results, algorithms, avgfname, datasetlabel,
                  extension = "png", graph_type="line", journalstyle = False):
    
    # (minQ,maxQ)=(None,None), (minEv,maxEv)=(None,None)
    
    #print "DEBUG: calling _exportGraphs", len(results), \
    #    "results for", str(algorithms), avgfname, extension, graph_type
           
    #graph_type="line" OR
    #graph_type="boxplot"
    #graph_type="parallel" #Parallel coordinate plot. Requires tuned parameters list in tp (souce is results file, not evals file)
    
    (minQ,maxQ)=(None,None)
    (minEv,maxEv)=(None,None)
    
    # Min max quality
    (minQ,maxQ) = (0.0,1.1)
    (minEv,maxEv) = (0,5100)
    if AUTO_SCALE_GRAPHS:
        def selQ(record):
            #(ar, mev, meq, seq, tpl, ql, evl )
            return record[2]
        minQ,maxQ = _getMinMaxResults(results, selQ, True )
        
    # Actual avtive evals?
    evs = []
    for key in results.keys():
        sk = str(key[2])
        if not sk in evs:
            evs.append(sk)
            
    avglabel = avgfname
    if avgfname:
        if avgfname=="median":
            avglabel = 'Median'
        elif avgfname=="mean":
            avglabel = 'Avg.'
        elif avgfname=="best":
            avglabel = 'Best'
        elif avgfname=="worst":
            avglabel = 'Worst'
        
    for algo in algorithms:
        aresults = _filterResults(results, only_algos=[algo])
            
        # Min max quality
        if graph_type=="line":
            # Scaling per algo
            if AUTO_SCALE_GRAPHS:
                def selEv(record):
                    #(ar, mev, meq, seq, tpl, ql, evl )
                    return record[1]
                minEv,maxEv = _getMinMaxResults(aresults, selEv, False )                
                minEv,maxEv = int(60),int(maxEv+(maxEv-minEv)*0.05)
                minQ,maxQ = ( int((min( pl[2] for pl in aresults.values() )-0.05)*100)/100.0,
                                 ((max( pl[2] for pl in aresults.values() )+0.05)*100)/100.0 )
                                 
            fn = "tuning_results_%s%s.%s" % (algo.replace(" ", "-"), datasetlabel, extension)
            fn = os.path.join(PLOT_OUTPUT_SUBDIR, avgfname, fn)
            figgen.exportLineGraph(fn, aresults, algo, avglabel, (minQ,maxQ), (minEv,maxEv), pubstyle = journalstyle )
        elif graph_type=="boxplot":
            # Scaling per algo
            if AUTO_SCALE_GRAPHS:                
                minQ,maxQ = ( -0.05, #int((min( min(pl[-2]) for pl in results.values() )-0.05)*100)/100.0,
                    int((max( max(pl[-2]) for pl in results.values() )+0.05)*100)/100.0 )
                    
            fn = "box_plot_%s_%s%s.%s" % (algo.replace(" ", "-"), "-".join(sorted(evs)), datasetlabel, extension)
            fn = os.path.join(PLOT_OUTPUT_SUBDIR, "box", fn)
            figgen.exportBoxPlot(fn, aresults, algo, (minQ,maxQ), pubstyle = journalstyle )
        elif graph_type=="parallel":
            tunername =  "ALL-"
            for eb in EBS+[1]+EXTRA_EBS:
                fn = "parallel_plot_%s%s_%s.%s" % (algo.replace(" ", "-"), datasetlabel, tunername+str(eb), extension)
                fn = os.path.join(PLOT_OUTPUT_SUBDIR, "parallel", fn)
                figgen.exportParallelCoordinatePlot(fn, aresults, algo, TUNERS, [eb], pubstyle = journalstyle )
            fn = "parallel_plot_%s%s_%s.%s" % (algo.replace(" ", "-"), datasetlabel, tunername+"AEBS", extension)
            fn = os.path.join(PLOT_OUTPUT_SUBDIR, fn)            
            figgen.exportParallelCoordinatePlot(fn, aresults, algo, TUNERS, EBS+[1]+EXTRA_EBS, pubstyle = journalstyle )

            if PRODUCE_PER_TUNER_PARALLEL_PLOTS:                
                for tuner in TUNERS: 
                    for eb in EBS+[1]+EXTRA_EBS:
                        tunername =  (str(tuner)+"-") if tuner else "ALL-"
                        fn = "parallel_plot_%s%s_%s.%s" % (algo.replace(" ", "-"), datasetlabel, tunername+str(eb), extension)
                        fn = os.path.join(PLOT_OUTPUT_SUBDIR, fn)
                        figgen.exportParallelCoordinatePlot(fn, aresults, algo, [tuner], [eb] )
                    tunername =  (str(tuner)+"-") if tuner else "ALL-"
                    fn = "parallel_plot_%s%s_%s.%s" % (algo.replace(" ", "-"), datasetlabel, tunername+"AEBS", extension)
                    fn = os.path.join(PLOT_OUTPUT_SUBDIR, fn)
                    figgen.exportParallelCoordinatePlot(fn, aresults, algo, [tuner], EBS+[1]+EXTRA_EBS, pubstyle = journalstyle)
                    
        elif graph_type=="scatter":
            if algo in SCATTER_FOR_TARGETS:
                sp_results = _filterResults(aresults, only_ebs=SCATTER_FOR_EBS)
                fn = "scatter_plot_%s%s%s.%s" % (algo.replace(" ", "-"), datasetlabel, "".join(SCATTER_PARAMETERS), extension)
                fn = os.path.join(PLOT_OUTPUT_SUBDIR, fn)
                figgen.exportScatterPlot(fn, sp_results, algo, TUNERS, ebs=SCATTER_FOR_EBS, parameters=SCATTER_PARAMETERS, pubstyle = journalstyle)
        
                    
def _getAlgoAndTunerFromFilename(fn):
    stripped = fn.replace(".txt", "").replace("alt_", "")
    parts = stripped.split("_")
    
    tuner = parts[1].lower()
    algo = parts[2].lower()
    
    try:    
        if not tuner in TUNERS:
            tuner=NAME_TRANSLATIONS[tuner]
        
        # Use the most specific name you can find        
        if algo in NAME_TRANSLATIONS:
            algo = NAME_TRANSLATIONS[algo]
        for maxalgoidx in range(3, len(parts)):
            name_candidate = ("".join(parts[2:maxalgoidx])).lower()
            if name_candidate in NAME_TRANSLATIONS:
                algo = NAME_TRANSLATIONS[name_candidate]
    except:
        raise IOError("Unrecognized result file "+str((fn, tuner, algo)))
        
    return tuner, algo, parts

def _storeParameterSetResult(evaluations, repts, avgFunc, toResults, results_with_parameter_configurations=None, isCV=False):
    # evaluations[task_key][tuned_ps_idx][repeat_idx].append( payload )
    
    #expected_repeats = (TGT_REPTS_CV*CV_FOLDS if isCV else TGT_REPTS)    
    expected_repeats = (TGT_REPTS_CV if isCV else TGT_REPTS)
    
    ## 1. ITERATE TUNING TASKS
    for task_key, tuning_task_evaluations in evaluations.items():
        
        ## 1.1 VALIDATE TUNING TASK
        #print task_key, len(tuning_task_evaluations)
        if len(tuning_task_evaluations)!=expected_repeats:
            print "Error ",task_key,"Wrong number of tuned parameter sets. (was %d, expected %d)"%(len(tuning_task_evaluations),expected_repeats)
        
        ql = []      
        evl = []
        tpl = [] # Store idx!
        ar = 0
        
        ## 2. ITERATE PARAMETER CONFIGURATIONS OF A TUNING TASK
        for ps_idx, repeats in tuning_task_evaluations.items():
            
            ar+=1

            ## 2.1 VALIDATE PARAMETER CONFIGURATION EVALUATION REPEATS
            #print ps_idx, len (repeats)        
            if len(repeats)!=repts:
                print "Error: Wrong number of repetitions. (was %d, expected %d)"%(len(repeats),repts)                
        
            
            ## 3. ITERATE EVALUATION REPETITIONS OF A TASK AND OF A PARAMETER SET
            #print repeats
            for repetition in repeats:
                #print repetition
                
                ## 3.1 VALIDATE EVALUATION REPEATS
                # payload = (tuned_ps_idx,benchmark_name,instance_quality,ps_actual_evals,ps_hash)
                if not isCV and len(repetition)!=14:
                    print "Error: Wrong number of evaluated instances. (was %d, expected %d)"%(len(repetition),14)
                if isCV and (len(repetition)!=14 and len(repetition)!=28):
                    print "Error: Wrong number of evaluated instances. (was %d, expected %d)"%(len(repetition),14)
                    
                if len( set((payload[0] for payload in repetition)) )!=1:
                    print "Error: repetition should only contain results of single parameter configuration"
                if not isCV and len( set((payload[1] for payload in repetition)) )!=len(repetition):
                    print "Error: duplicate evaluation of a problem instance in repetition"
                    
                # TODO: This check does not work as expected. The HASH should be used, but
                #  then it should not contain the seed/instance. :( Unsolved for now 
                if not isCV and len( set((payload[3] for payload in repetition)) )!=1:
                    print "Error: repetition should only contain results of single parameter configuration that was produced with %d actual evaluations" % repetition[0][3]
                if isCV and not 1<=len( set((payload[3] for payload in repetition)) )<=CV_FOLDS:
                    print "Error: repetition should only contain results of single parameter configuration that was produced with %d actual evaluations: %s" % (repetition[0][3], str(set((payload[3] for payload in repetition))))

                if not isCV and len( set((payload[4] for payload in repetition)) )!=len(repetition):
                    print "Error: duplicate evaluation with key %s repetition (hash encoutered twice)" % str(task_key)
                
                # unpack payload =
                #(tuned_ps_idx,benchmark_name,instance_quality,actual_evaluations,ps_hash) = repetition
                
                ql.append( sum( (payload[2] for payload in repetition) ) )
                
                # TODO: How to get this. Use ps_idx? Perhaps tp_hash?
                # WARNING: THIS IS NEEDED
                #evl.append( repetition[0][3]  )
                
                # Cross validation might have different number of evals for
                #  each fold. Use average.
                evl.append( scipy.mean( [payload[3] for payload in repetition] ) )
            
            # 4. Get parameter configuration used to do this evaluation            
            if results_with_parameter_configurations:
                #unpack
                if not isCV:
                    #(ar, mev, meq, seq, tpl, ql, evl ) = results_with_parameter_configurations[task_key]
                    (_, _, _, _, rtpl, _, _) = results_with_parameter_configurations[task_key]
                else:
                    #(ar_per_fold, rl, fl, mev, meq, seq, tpl, ql, evl, ctsl, cvsl ) = results_with_parameter_configurations[task_key]
                    (ar_per_fold, _, _, _, _, _, rtpl, _, _, _, _ ) = results_with_parameter_configurations[task_key]
                tpl.append(rtpl[int(ps_idx)])
            else:
                tpl.append(ps_idx)
            
            
            #if  ('ParamILS', 'VRPH SA A', 100) 
            #{'-c': 0.99,  '-cutoff': 10.0,  '-f': '',  '-h_1pm': 0,  '-h_2pm': 0,  '-h_3pm': 1,  '-h_oro': 0,  '-h_tho': 1,  '-h_two': 1,  '-i': 10,  '-n': 222,  '-nn': 23,  '-r': 1,  '-t': 3.33333333333} in tpl:
            
        if not avgFunc:
            mev = -1.0
            meq = -1.0
            seq = -1.0            
        else:
            mev, meq, seq = avgFunc(evl, ql)
            
        result = (ar, mev, meq, seq, tpl, ql, evl )
    
        toResults[task_key] = result
                
def parseEvalsFromFiles(files = "evals_*_we.txt", avgFunc=None, returnEvaluationsData=False, results_with_pcs=None):
    """
    from eval file with lines like
    <tuning task key>;<tuned parameter set Idx>;<repeat idx>;<benchmark_name>;<seed>;<evaluated quality>;<hash_of_the_parameter_set_seed_and_benchmark>
    
    if returnEvaluationsData==True, the routine produces a dict of
         evaluations[key][tuned_ps_idx][repeat_idx].append( payload ), where payload is
         (tuned_ps_idx,benchmark_name,instance_quality,ps_actual_evals,ps_hash)
     otherwise it produces the normal result dict with
         key=(tuner, algo, eb) -> payload=(actual_rpts, mev, meq, seq, tpl, ql, evl )
     where tpl is a list of parameter configuraitons of results_with_pcs is given (otherwise list of idxs)
    
    """
    results = {}
    evaluations = {}
    
    isCV = False
    
    for evalsFile in glob.glob(files):
        if VERBOSE > 0:
            print "Reading evaluations from file ", evalsFile
        
        if not returnEvaluationsData:
            evaluations = {}        
        
        counter = 0
        repts = 0
        
        tuner, algo, parts = _getAlgoAndTunerFromFilename(os.path.basename(evalsFile))        
        
        if "3cv" in evalsFile:
            isCV = True
            
        for pt in parts:
            if "repts" in pt:
                repts = int( pt.replace("repts", "").replace(".txt", "") )
        
        rf = open(evalsFile)
        rflines = rf.readlines()
        rf.close()
        key = None
        
        keys_read_from_this_file = set()
        firstkey = None
        for line in rflines:
            line = line.strip()
            if line=="" or line[0]=="=":
                continue
            
            lparts = line.split(";")
            
            try:
                ast_key = ast.literal_eval(lparts[0])
            except:
                print "ERROR: Failed to parse line %s (len %d) in file %s" % (line, len(line), evalsFile)
                continue
            
            
            if not firstkey:
                firstkey = ast_key
                        
            # Dirty dirty quickfix
            #  we use this because algorithm names have changed
            #  the file name determines Christofides or Augerat target
            tuner, algo_evalskey, eb = ast_key
            key = (tuner, algo, eb)
            
            if key not in keys_read_from_this_file:
                keys_read_from_this_file.add(key)
                
                if evaluations.has_key(key):
                    print "Warning: Same key %s from multiple files, not good" % key
            
            #   0          1       2      3       4    5    6       7
            # task_key; ps_id; rep_id; instance; seed; q; a.evals; ps_hash
            tuned_ps_idx = int(lparts[1])
            repeat_idx = int(lparts[2])
            benchmark_name = lparts[3]
            #seed = int(lparts[4])
            instance_quality = float(lparts[5])
            ps_actual_evals = int(lparts[6])
            ps_hash = ast.literal_eval(lparts[7])
                
            
            if not key in evaluations:
                evaluations[key]={}
            if not tuned_ps_idx in evaluations[key]:
                evaluations[key][tuned_ps_idx]=[]
                for i in range(repts):
                    evaluations[key][tuned_ps_idx].append([])
                        
            #print key, psId, repId
            payload = (tuned_ps_idx,benchmark_name,instance_quality,ps_actual_evals,ps_hash)
            #print payload
            #if len(evaluations[key][tuned_ps_idx])<repeat_idx:
            #    print evalsFile
            #    print line
            try:
                if not isCV:
                    if payload in evaluations[key][tuned_ps_idx][repeat_idx]:
                        print "Error: Duplicate data", payload, evaluations[key][tuned_ps_idx][repeat_idx]
                        raise IOError("Duplicate data")
                    evaluations[key][tuned_ps_idx][repeat_idx].append( payload )
                else:
                    #QUICKFIX. For training set evals in 3cv there may be duplications
                    evaluations[key][tuned_ps_idx][repeat_idx].append( payload )
                    
                counter+=1
            except:
                print key, tuned_ps_idx, repeat_idx
                print evalsFile
                print line
                raise IOError("Malformed data, repeats, parameter count and the data do not match.")
        
        if algo!=algo_evalskey and VERBOSE>1:
            print "Warn   Evaluation file key %s and file name key %s differ" % (firstkey, key)

        if not returnEvaluationsData:
            _storeParameterSetResult(evaluations, repts, avgFunc, results, results_with_pcs, isCV)
            
    #print results
    if returnEvaluationsData:
        return evaluations
    else:
        return results
    
    
def parseResultsFromFiles(files = "result*.txt", avgFunc=None, crossValidation=False):
    """ Parse files that have the format:
        result_<Tuner>_<Algo>_<timeout>sec_<eval_budget>eval[s]_<repetitions>repts.txt
        e.g. result_ParamILS_VRPHEJ_10sec_500eval_10repts.txt
    """
    global VERBOSE
    #VERBOSE = 3
    
    required_repeats = TGT_REPTS
    #print files
    if crossValidation:
        required_repeats = TGT_REPTS_CV*CV_FOLDS
        
    
    results = {}
    tunerParameters = {}
    
    for resultFilePath in glob.glob(files):
        resultFile = os.path.basename(resultFilePath)
        if VERBOSE > 0:
            print "Reading evaluations from file ", resultFile
        
        tuner, algo, parts = _getAlgoAndTunerFromFilename(resultFile)

        if VERBOSE > 2:
            print tuner, algo, parts
        #raise IOError("Unrecognized file name format %s"%resultFile)
       
       
        # QUCKHACK Skip temp files
        if "first" in parts[5] or "last" in parts[5]:
            continue

        #print parts
        #evals = int( parts[-2].replace("evals", "").replace("eval", "") )
        #repts = int( parts[-1].replace("repts", "") )
        try:
            evals = int( reEvalsInFileName.search(resultFile).group(1) )
            repts = int( reReptsInFileName.search(resultFile).group(1) )
        except:
            raise IOError("Could not recognize number of evals and repetitions from the filename %s" % resultFile )
        
        # Skip extra EBS results 
        #if evals in EXTRA_EBS and skipExtra:
        #    continue
            
        # Actual repts
        ar = 0
        rf = open(resultFilePath)
        rflines = rf.readlines()
        rf.close()
        mev = 0.0
        tp = None
    
        ql = []
        evl = []
        tpl = []
        
        fold = 0
        current_training_set = []
        reading_cts = False
        current_validation_set = []
        reading_cvs = False
        
        ctsl = []
        cvsl = []
        fl = []
        rl = []
               
        fold = CV_FOLDS
        prev_fold = CV_FOLDS
        
        for line in rflines:
            if "Quality" in line:
                ar+=1
                ql.append(float(line.replace("Quality: ", "")))
                if crossValidation:
                    ctsl.append(current_training_set)
                    cvsl.append(current_validation_set)            
            if "Evaluations: " in line:
                try:
                    evl.append(int(line.replace("Evaluations: ", "")))
                except:
                    raise IOError("Could not parse number of evaluations from line %s in file %s" % (line,resultFile) )
                    
            if "Tuned parameters: " in line:
                dictstr = line.replace("Tuned parameters: ", "")
                tp = ast.literal_eval(dictstr)
                tpl.append( tp )
                
            if crossValidation:
                # Absolute to relative
                if reading_cts or reading_cvs:
                    local_fs_line_start = line.find(r"Benchmarks/")
                    local_fs_line = os.path.join(
                        PathManager.GetTuningBasePath(),
                        line[local_fs_line_start:].strip() )
                
                if reading_cts:
                    if line=="" or not os.path.isfile(local_fs_line):
                        # instances must be in concecutive lines
                        reading_cts = False
                    else:
                        current_training_set.append(local_fs_line)
                if reading_cvs:
                    if line=="" or not os.path.isfile(local_fs_line):
                        # instances must be in concecutive lines
                        reading_cvs = False
                    else:
                        current_validation_set.append(local_fs_line)
                        
                if "Tuning set:" in line:
                    reading_cts = True
                    current_training_set=[]
                if "Validation set:" in line:
                    reading_cvs = True
                    current_validation_set=[]

                # fold recognition
                rflm = reFoldLine.match(line)
                if rflm:
                    prev_fold = fold
                    fold = int(rflm.group(1))
                    of_folds = int(rflm.group(2))
                    if of_folds!=CV_FOLDS:
                        raise IOError("Different number of folds (%d) in cross validation than expected (%d)"%(fold, of_folds))
                    if (fold == 1 and prev_fold!=CV_FOLDS):
                        raise IOError("Not enough folds for the repetition %d in file %s"%(ar/CV_FOLDS, resultFile))
                    if (prev_fold == fold):
                        raise IOError("Too many folds (%d) for the repetition %d in file %s"%(fold, ar/CV_FOLDS, resultFile))
                    fl.append(fold-1)
                    rl.append(ar/CV_FOLDS)
                    
                
            # UGLY QUICKFIX FOR REVAC
            reline = line.replace("'-I': 1000", "").replace("'-m': 100", "")
            
            # Get the tuning task
            ttm = reTuningTask.match(reline)
            if ttm:
                ttmTuner = ttm.group(1).replace("_", "").replace("Tuner", "").lower()
                ttmAlgo = ttm.group(2).replace("_", "").lower()
                tttp = ast.literal_eval( ttm.group(3).replace(", ,", ",") )
                
                #print tttp.values()
                allebs = EBS+EXTRA_EBS
                valset = False
                ttmEvals = max(allebs)
                for val in tttp.values():
                    if val in allebs and val <= ttmEvals:
                        ttmEvals = val;
                        valset = True
                if not valset:
                    # Defaults may not have budget specified
                    ttmEvals =1
                
                try:    
                    if not ttmTuner in TUNERS:
                        ttmTuner=NAME_TRANSLATIONS[ttmTuner]
                    if not ttmAlgo in ALGOS:            
                        ttmAlgo=NAME_TRANSLATIONS[ttmAlgo]
                except:
                    raise IOError("Unrecognized tuning task (%s tunes %s) in file %s"%\
                      (ttmTuner, ttmAlgo, resultFile) )
                
                # Modified to allow the algo name to be substring of the full target name
                if ttmTuner!=tuner or (not ttmAlgo in algo) or (evals!=1 and int(ttmEvals)!=int(evals)):
                    raise IOError("Wrong tuning task (%s tunes %s for %s evals) in file %s (should be %s tuning %s for %s evals)"%\
                      (ttmTuner, ttmAlgo, ttmEvals, resultFilePath,
                      tuner, algo, evals))
        
        key = (tuner, algo, evals)
        
        if (ar==0 or (ar<required_repeats and ar<repts)):
            raise IOError("Not enough results for (%s) in file %s (%d vs. %d)"%\
                (str(key), resultFile, ar, repts) )
        
        #print "DEBUG: ", key, resultFile, len(ql), len(evl), len(tpl)
        
        if not avgFunc:
            mev = -1.0
            meq = -1.0
            seq = -1.0            
        else:
            mev, meq, seq = avgFunc(evl, ql)

        # Check for budget
        if VERBOSE>0 and tuner!="Defaults":
            wrong_nbr_of_evaluations_used = len( [e for e in evl if abs(e-evals)>25] )
            if wrong_nbr_of_evaluations_used > 0:
                print key, "%d outside evaluation budget" % wrong_nbr_of_evaluations_used
            
        
        if key in results:
            raise IOError("Duplicate results for (%s) in file %s"%\
                (str(key), resultFile) )

        if len(ql)!=len(tpl) or len(ql)!=len(evl):
            raise IOError("Unbalanced/incomplete results for (%s) in file %s"%\
                (str(key), resultFile) )
            
            
        if crossValidation:
            if len(ql)!=len(rl) or len(ql)!=len(fl) or len(ql)!=len(fl) or len(ql)!=len(fl):
                raise IOError("Unbalanced/incomplete results for (%s) in file %s"%\
                    (str(key), resultFile) )
            results[key] = (ar/CV_FOLDS, rl, fl, mev, meq, seq, tpl, ql, evl, ctsl, cvsl )
        else:
            results[key] = (ar, mev, meq, seq, tpl, ql, evl )
        #print key, evl
        
        # Check for paramter conflicts
        if (VERBOSE>0):
            tkey = (tuner, evals)
            if tkey in tunerParameters and tttp!=tunerParameters[tkey]:
                differences = []
                for pkey in tttp.keys():
                    if pkey!="-seed" and pkey!="--seed" and pkey!="-s" and pkey!="-numRun" and pkey!="--numRun":
                        if pkey in tttp and pkey in tunerParameters[tkey]:
                            if tttp[pkey]!=tunerParameters[tkey][pkey]:
                                differences.append( (pkey, tttp[pkey],tunerParameters[tkey][pkey]) )
                        else:
                            pval = 0
                            if pkey in tttp:
                                pval = tttp[pkey]
                            elif pkey in tunerParameters[tkey]:
                                pval = tunerParameters[tkey][pkey]                   
                            differences.append( (pkey, pval, pval) )
                            
                if len(differences)>0:
                    print "Warning: in file %s, task %s results have different tuner parameter sets (%s)"%\
                      (resultFile, str(tkey), str(differences))
            else:
                tunerParameters[tkey]=tttp

                
        
        
        #if len(tpl)==0:
        #    print resultFile
        #print key, results[key] 
    return results
        

    
def significanceBestResults(significances, best_values, algorithms, p_level=0.10, neighbours=0, use_family_correction=True):
    global VERBOSE
    different = set()

    # Bonferroni correction
    if use_family_correction:
        corrected_p_level = p_level/(len(TUNERS))
    else:
        corrected_p_level = p_level
    
    #for tuner in TUNERS:
    for algo in algorithms:
        default_key = (DEFAULT[0], algo, 1)
        
        for evals in EBS+EXTRA_EBS:
            #key = (tuner, algo, evals)
            best_key = (algo, evals)
            
            if not best_key in best_values: 
                if VERBOSE > 1:
                    print "Warning: No best tuner for task %s" % str(best_key)
                continue
                #raise ValueError("No best tuner for task %s" % str(best_key))
            for best in best_values[best_key]:
                bkey = (best, algo, evals)
                
                #print significances[bkey]
                #(H_statistic, p_value) = significances[bkey][default_key]                            
                #if p_value>corrected_p_level:
                #    if VERBOSE > 0:
                #        print "Rejected %s because not significantly better than defaults" % str(bkey)
                #    continue
                    
                        
                sigc = 0
                testc = 0
                similars = []
                
                for other_tuner in TUNERS:
                    okey = (other_tuner, algo, evals)
                        
                    if okey!=bkey:                        
                        
                        #print okey, bkey
                        if okey in significances[bkey]:
                            testc+=1
                            (H_statistic, p_value) = significances[bkey][okey]                            
                            
                            if p_value<corrected_p_level:
                                sigc+=1
                                if VERBOSE>1:
                                    print "%"+str(bkey) + " and " + str(okey) + " are statistically different with confidence " + str(corrected_p_level)
                                    print "%","H_statistic, p_value = ",(H_statistic, p_value)
                                    print
                            else:
                                if VERBOSE>1:
                                    print okey, "found to be similar to the best", bkey
                                similars.append(okey)
                 
                if (abs(sigc-testc)==neighbours) or (bkey in similars): #and (tuner==best)): #
                    if VERBOSE>1:
                        print "All tests signficant for " + str(bkey) + " at level " + str(corrected_p_level) + " together with %d others (%s)" % (abs(sigc-testc), str(similars))
                    different.add(bkey)
                    for sim in similars:
                        different.add(sim)
    return list(different)
    
def calculateSignificances(results, algorithms, includeDefaults=False):
    
    tested_tuners = TUNERS
    if includeDefaults:
        tested_tuners = TUNERS+DEFAULT
        
    sfms = {}
    for tuner in tested_tuners:
        for algo in algorithms:
            for evals in [1]+EBS+EXTRA_EBS:
                key = (tuner, algo, evals)
                for other_tuner in tested_tuners:
                    if other_tuner==DEFAULT[0]:
                        okey = (other_tuner, algo, 1)
                    else:
                        okey = (other_tuner, algo, evals)
                    #print key, okey
                    if key in results and okey!=key and okey in results:                        
                        ql = results[key][-2]
                        oql = results[okey][-2]                        
                        try:
                            #(statistic, p_value) = kruskalwallish(ql, oql)
                            (statistic, p_value) = mannwhitneyu(ql, oql)
                            #print statistic, p_value
                        except:
                            print ql, oql
                            
                        #if (p_value<p_level):
                        if not key in sfms:
                            sfms[key]={}
                        if not okey in sfms[key]:
                            sfms[key][okey]=None
                        else:
                            if sfms[key][okey]!=(statistic, p_value):
                                print "Warning reverse test gave different result", (statistic, p_value), "vs.", sfms[key][okey]
                        
                        sfms[key][okey]=(statistic, p_value)
        
    return sfms

def printSignificantResults(algorithms, significances, statistically_significant_best, p_level=0.10):
    for ksg, sg in sorted(significances.items()):
        print ksg
        for ok, up in sorted(sg.items()):
            if up[1] < p_level:
                print "->", ok , "by:", up[1]
            else:
                print "--", ok , "by:", up[1]
        #print
        
    return
    
    for algo in sorted(algorithms):   
        for eb in [1]+EBS+EXTRA_EBS: 
            for sn in sorted(statistically_significant_best):
                if sn[1]==algo and sn[2]==eb:
                    print sn
            print
        
def getBestTunersForTasks(results, algorithms, number_of_best=1):
    best = {}
    for algo in algorithms:
        for evals in EBS+EXTRA_EBS:
            best_key = (algo, evals)
            #print best_key
            
            best_tuners = []
            #best_q = sys.maxint 
            for tuner in TUNERS:
                key = (tuner, algo, evals)
                if key in results:
                    #print key
                    q = results[key][2]
            
                    #print "start", best_tuners
                    if len(best_tuners)<number_of_best:
                        best_tuners.append( (q, tuner) )
                    elif q<best_tuners[-1][0]:
                        best_tuners.pop()
                        best_tuners.append( (q, tuner) )
                    best_tuners.sort()
                    #print "end", best_tuners
                 
            if len(best_tuners)>0:
                #print best_tuners, best_key 
                best[best_key] = zip(*best_tuners)[1]
            else:
                #print best_tuners, best_key 
                best[best_key] = ()
                
            #print
    return best
            
                    
def approximateBudgetQualities(results, algorithms):
    """ Some tuning tasks used more or less evaluations than specified 
    in the budget. This code does linear approximation (interpolation/
    extrapolation depending on datapoint positions) for the evaluation
    budgets in the list. 
    """
    approx_results = {}
    
    for tuner in DEFAULT:
        for algo in algorithms:
            key = (tuner, algo, 1)
            if key in results:
                approx_results[key] = results[key]
            
    for tuner in TUNERS:
        for algo in algorithms:
            for evals in EBS+EXTRA_EBS:
                key = (tuner, algo, evals)
                if key in results:
                    #unpack
                    (ar, mev, meq, seq, tpl, ql, evl ) = results[key]                     
                    
                    if (int(mev)==evals):
                        ameq = meq
                        aseq = seq 
                    else:
                        # Get 2 closest data pts
                        dist = []
                        for devals in EBS+EXTRA_EBS:
                            dkey = (tuner, algo, devals)
                            if dkey in results:
                                (dar, dmev, dmeq, dseq, dtpl ) = results[dkey]    
                                dist.append( (abs(dmev-evals), dmev, dmeq, dseq) )
                        if len(dist)<2:
                            raise AttributeError("Not enough data poits to approximate the budget value")
                        dist.sort()
                        #print dist                        
                        
                        ameq = line_y((dist[0][1],dist[0][2]), (dist[1][1],dist[1][2]), evals)
                        aseq = line_y((dist[0][1],dist[0][2]+dist[0][3]), (dist[1][1],dist[1][2]+dist[0][3]), evals)-ameq
                     
                    if VERBOSE>0:
                        print("result %s"%str(key))
                        print("   original was %f,%f,%f" % (mev,meq,seq))
                        print("approximated is %f,%f,%f" % (float(evals),ameq,aseq ))
                        print
                    # pack 
                    approx_results[key] = (ar, float(evals), ameq, aseq, tpl, ql, evl )
    return approx_results
    
def checkForMissing(results, algorithms, isCV):
    #print results.keys()
    
    target = []
    
    expected_repeats = (TGT_REPTS_CV if isCV else TGT_REPTS)
    for algo in algorithms:
        for evals in EBS+EXTRA_EBS:
            for tuner in TUNERS:
                if not tuner in TUNERS:
                    tuner=NAME_TRANSLATIONS[tuner]
                if not algo in ALGOS:  
                    algo=NAME_TRANSLATIONS[algo]
                if tuner == "Defaults":
                    if evals!=100:
                        continue
                    evals = 1
                #Skip those that should not have 5000e results
                if evals in EXTRA_EBS and algo not in EXTRA_EBS_ALGOS:
                    continue
                
                key = (tuner, algo, evals)
                target.append(key)
            
    # Verify that the results exist   
    for key in target:    
        if key in results:
            #unpack
            (ar, mev, meq, seq, tpl, ql, evl ) = results[key]  
            #if ar<target[key]:
            #    print "Error ",key, (" has only %d repts" % results[key][0])
            if abs(key[2]-mev)>(WARNING_EVALUATIONS_DIFF*key[2]):
                print "Warn  ", key,  " with %.2f evals (|Q|=%.2f) over %d%% eb violation" %\
                    (mev, meq, int(WARNING_EVALUATIONS_DIFF*100))
            else:
                print "OK    ", key, " with %.2f evals (|Q|=%.2f)" % (mev, meq)
            
            tprc = len(results[key][4])
            if tprc<expected_repeats:
                print key, " has not enough repetitions (%d, when should be at least %d)" % (tprc, expected_repeats)
        else:
            print "Error ",key, " results are missing"
                    
    
def medianFunc(evl, ql, giveDesc=False):
    if giveDesc:
        return ("median number of evaluations", "median quality", "median absolute deviation")
    
    # mev, meq, seq = avgFunc(evl, ql)
    midxs = median_idxs(evl)    
    mev = sum((evl[i] for i in midxs))/len(midxs)
    midxs = median_idxs(ql)
    meq = sum((ql[i] for i in midxs))/len(midxs)
        
    # Calculate MAD        
    madl = [abs(q-meq) for q in ql]
    seq = median(madl)
    
    return (mev, meq, seq)

def meanFunc(evl, ql, giveDesc=False):
    if giveDesc:
        return ("mean of number of evaluations", "mean quality", "standard deviation")
    
    # mev, meq, seq = avgFunc(evl, ql)
    if module_exists("scipy"):                
        meq = scipy.mean(ql)
        mev = scipy.mean(evl)
        seq = scipy.std(ql)
    else:
        meq = -1.0        
        mev = -1.0     
        seq = -1.0     
    return (mev, meq, seq)  
    
def bestFunc(evl, ql, giveDesc=False):
    if giveDesc:
        return ("evaluations used to get the best quality", "best quality", "range")
    
    import operator
    min_idx, tql = min(enumerate(ql), key=operator.itemgetter(1))
    tev = evl[min_idx]
    qrange = max(ql)-tql
    return (tev, tql, qrange)
    
def worstFunc(evl, ql, giveDesc=False):
    if giveDesc:
        return ("evaluations used to get the worst quality", "worst quality", "range")
    
    import operator
    max_idx, tql = max(enumerate(ql), key=operator.itemgetter(1))
    tev = evl[max_idx]
    qrange = tql-min(ql)
    return (tev, tql, qrange)
    
def label_to_avgFunc(avgf_label):
    if avgf_label=="median":
        uavgFunc = medianFunc
    elif avgf_label=="mean":
        uavgFunc = meanFunc
    elif avgf_label=="best":
        uavgFunc = bestFunc
    elif avgf_label=="worst":
        uavgFunc = worstFunc
    else:
        raise Exception("Unknown method %s" % str(avgf_label))
    return uavgFunc 
    
def get_special_eval(from_data_source):
    # Results evaluated on training data, so it is the default
    special_evals = "_results"
    special_evals_label = "tuning instances"
    special_evals_short_label = "on training set"
    if ("testset" in from_data_source):
        special_evals= "_testset"
        special_evals_label = "test instances"
        special_evals_short_label = "on validation set"
    if ("we" in from_data_source or "trainset" in from_data_source):
        special_evals= "_trainset"# training set       
        special_evals_label = "tuning instances"
        special_evals_short_label = "on training set"
    return special_evals, special_evals_label, special_evals_short_label 
    
    
def get_scaling_range(special_evals, target, no_outliers=False, scale_optimality_gap=True):
    """
    Get range for scaling. Returns triplet (min, max, multiplier)
    """
    
    if no_outliers and scale_optimality_gap:
        print "Error, cannot scale both without outiliers and with optimality gap"
    
    plaintarget = target.lower().replace("_rtr_", "_").replace("_ej_", "_").replace("_sa_", "_")
    if "christofides" in plaintarget or "vrph_c" in plaintarget:
        algo_group = "VRPH_CHRISTOFIDES"
    elif "augerat" in plaintarget  or "vrph_a" in plaintarget:
        algo_group = "VRPH_AUGERAT"
    elif "iridia" in target.lower() or "vrpsd" in plaintarget:
        algo_group = "VRPSD_IRIDIA"
    else:
        algo_group = target
    
    #print algo_group
    #print special_evals
    
    # 45113.08 is sum of all best known
    if special_evals=="_results" or special_evals=="_we" or special_evals=="_tuneset" or special_evals=="_trainset":
        if no_outliers:
            Qranges = {
                "VRPH_CHRISTOFIDES":(13664.35, 14659.754),
                "VRPH_AUGERAT":(13750.0, 14165.0),
                "VRPSD_IRIDIA":(45342.66215, 46210.27753),
            }
            normalization_multiplier = 1.0
        elif scale_optimality_gap:
            Qranges = {
                "VRPH_CHRISTOFIDES":(13664.35, 13664.35*2),
                "VRPH_AUGERAT":(13750.0, 13750.0*2),
                "VRPSD_IRIDIA":(45342.66215, 45342.66215*2),
            }
            normalization_multiplier = 100.0
        else:
            Qranges = {
                "VRPH_CHRISTOFIDES":(13664.35, 14987.807),
                "VRPH_AUGERAT":(13750.0, 14165.0),
                "VRPSD_IRIDIA":(45342.66215, 46210.27753),
            }
            normalization_multiplier = 1.0
            
    if special_evals=="_testset":
        if no_outliers:
            Qranges = {            
                "VRPH_CHRISTOFIDES":(13664.35, 14659.754),
                "VRPH_AUGERAT":(12494.0, 12804.0),
                "VRPSD_IRIDIA":(36757.070509, 37529.104434),
            }
            normalization_multiplier = 1.0
        elif scale_optimality_gap:
            Qranges = {
                "VRPH_CHRISTOFIDES":(13664.35, 13664.35*2),
                "VRPH_AUGERAT":(12494.0, 12494.0*2),
                "VRPSD_IRIDIA":(36757.070509, 36757.070509*2),
            }
            normalization_multiplier = 100.0
        else:
            Qranges = {   
                "VRPH_CHRISTOFIDES":(13664.35, 14987.807),
                "VRPH_AUGERAT":(12494.0, 12804.0),
                "VRPSD_IRIDIA":(36757.070509, 37529.104434),
            }
            normalization_multiplier = 1.0


    if (special_evals=="_we" or special_evals=="_tuneset") and "3cv" in target:
        # The training set is twice the normal 
        Qranges[algo_group] = (Qranges[algo_group][0]*2, Qranges[algo_group][1]*2)
        
        
    # Return triplet (min, max, multiplier)
    return Qranges[algo_group][0], Qranges[algo_group][1], normalization_multiplier

def normalizeQualities(results, minQ=None, maxQ=None, multiplier=1.0):
    # Use ordered dict to get nice ordering in graphs
    normalized_results = OrderedDict() 
    
    if len(results)==0:
        return normalized_results

    # Determine source range    
    #(ar, mev, meq, seq, tpl, ql, evl )
    def selQList(record):
        return record[5]
    
    # Use actual range (without outliers) as default
    #  (usually overwritten with  minQ, maxQ)
    rangeMinQ,rangeMaxQ = _getMinMaxResults(results, selQList, True )
    if (minQ):
        rangeMinQ = minQ
    if (maxQ):
        rangeMaxQ = maxQ
    dQ = rangeMaxQ-rangeMinQ
        
    # Normalize
    for key in results:
        #unpack
        (ar, mev, meq, seq, tpl, ql, evl ) = results[key]
        
        nmeq = (meq-rangeMinQ)/dQ*multiplier
        nseq = (seq)/dQ*multiplier
        
        nql = [(q-rangeMinQ)/dQ*multiplier for q in ql]
        
        #if max(nql)>1.01:
        #    print len(nql), rangeMaxQ, rangeMinQ, dQ, key, nql
        
        # pack 
        normalized_results[key] = (ar, mev, nmeq, nseq, tpl, nql, evl )
        
    return normalized_results 
    
def load_all_results(data_source="Evals_testset", avgf="median", check_missing=False, use_cache=False, produce_cache=False, extra_ebs=False, normalize=True):
    # Init some helper variables and shorthands   
    special_evals, special_evals_label, special_evals_short_label = get_special_eval(data_source)
    
    # Get results for every ALGO_GROUP
    all_results = OrderedDict() 
    for ag in ALGO_GROUP:
        results = load_results(ag, data_source, avgf, None, check_missing, use_cache, produce_cache, extra_ebs)
        if normalize:
            minQ, maxQ, nmult = get_scaling_range(special_evals, ag, RANGES_WITHOUT_OUTLIERS, RANGES_PERCENTAGE_OPT)
            nresults = normalizeQualities(results, minQ, maxQ, nmult)
            all_results = dict( all_results.items() + nresults.items() ) 
        else:
            all_results = dict( all_results.items() + results.items() )                      
    
    return all_results

def load_results(algorithm_group, data_source="Evals_testset", avgf="median", only_algos=None, check_missing=False, use_cache=False, produce_cache=False, extra_ebs=False):

    uavgFunc = label_to_avgFunc(avgf)
    
    # Init some helper variables and shorthands    
    ag = algorithm_group
    special_evals, special_evals_label, special_evals_short_label = get_special_eval(data_source)
    
    # == Load data from files ==
    data_folder = ALGO_GROUP_RESULT_SUBFOLDERS[ag]
    
    
    algos = ALGO_GROUP_ALGOS[ag]     
        
    cachefilen = "nresults_cache_%s_%s_%s.pickle" % (data_source, avgf, ag)
    cachefilepath = os.path.join(CACHE_FOLDER, cachefilen)
    if use_cache:
        pfile = open( cachefilepath, 'rb' )
        results = pickle.load( pfile )
        pfile.close()
        
    isCV = False
    # TODO: This is QUCIKFIX. Find a better way to find out it is cross 
    #  validation file
    if "_3cv" in data_folder:
        isCV = True
        
    if not use_cache or produce_cache:
        if "Results" in data_source:
            seekpath = os.path.join(data_folder, "result_*repts*.txt")
            print seekpath
            results = parseResultsFromFiles(files=seekpath, avgFunc=uavgFunc)
        elif "Evals" in data_source:
            #Ugly quickfix. Christofides does not have test set.
            if not isCV and ag=="VRPH_CHRISTOFIDES" and special_evals=="_testset":
                seekpath = os.path.join(data_folder, "evals_*.txt")
                results = parseEvalsFromFiles(files=seekpath, avgFunc=uavgFunc)
            else:
                seekpath = os.path.join(data_folder, "evals_*"+special_evals+".txt")
                results = parseEvalsFromFiles(files=seekpath, avgFunc=uavgFunc)
         
        if check_missing:
            checkForMissing(results, algos, isCV)   
            
        if produce_cache:
            pfile = open( cachefilepath, 'wb' )
            pickle.dump( results, pfile )
            pfile.close()

    #aresults = ApproximateBudgetQualities(results, only_algos)
    
    if only_algos!=None:
        return _filterResults(results, only_algos=only_algos)
    else:
        return results #_filterResults(results, only_algos=algos)
    
    
    
def main(data_source="Evals_testset", fig_exts=["png"], avgf="median", produce_table=None, only_algos=None, graph_types=[], check_missing=False, use_cache=False, produce_cache=False, extra_ebs=False):
    global VERBOSE
    global JOURNALSTYLE

    # === DEFAULTS ====
        
    special_evals, special_evals_label, special_evals_short_label = get_special_eval(data_source)
    
    
    # === Parsing and output ===
    
    uavgFunc = label_to_avgFunc(avgf)
            
    all_algos = []
    all_statistically_significant_best = []
    all_nresults = OrderedDict() 
    
    
    for ag in ALGO_GROUP:
        # == Load data from files ==
        
        results = load_results(ag, data_source, avgf, only_algos, check_missing, use_cache, produce_cache, extra_ebs)
        
        minQ, maxQ, nmult = get_scaling_range(special_evals, ag, RANGES_WITHOUT_OUTLIERS, RANGES_PERCENTAGE_OPT)
        nresults = normalizeQualities(results, minQ, maxQ, nmult)
        
        # == Table generation ==
        algos = ALGO_GROUP_ALGOS[ag]     
        if only_algos:
            algos = only_algos
            
        if len(nresults)>0:
            if produce_table or PRODUCE_MAD_MEDIANS:
                all_algos=list(set(algos+all_algos))
                    
                new_all_nresults = OrderedDict( all_nresults.items() + nresults.items() )        
                all_nresults = new_all_nresults
                
                best = getBestTunersForTasks(results, algos, 1)
                snf = calculateSignificances(results, algos)
                statistically_significant_best = \
                    significanceBestResults(snf, best, algos, 0.05, neighbours=0) + \
                    significanceBestResults(snf, best, algos, 0.05, neighbours=1) #+ \
                    #SignificanceBestResults(snf, best, algos, 0.05, neighbours=2)
                if VERBOSE>1:
                    printSignificantResults(algos, snf, statistically_significant_best, 0.05)
                all_statistically_significant_best+=statistically_significant_best
    
            
            for graph_type in graph_types:
                if len(nresults)==0:
                    continue
                for ext in fig_exts:
                    _exportGraphs(nresults, algos, avgf, special_evals, ext, graph_type, JOURNALSTYLE)
    
            
        if not RG75_STYLE and produce_table:
            (eblabel, qlabel, sddevlabel) = uavgFunc([],[], True)
            
            if len(algos)!=len(ALGO_GROUP_ALGOS[ag]):
                target = ", ".join(algos)
                table_sbs = 1
                table_ebs = EBS+EXTRA_EBS
                tableLabel="results_tuning_"+"_".join(algos)+"_on"+special_evals+"_"+avgf
            else:
                target = ag.split("_")[0]+" "+ag.split("_")[1].lower().capitalize()
                table_sbs = 1
                if extra_ebs:
                    table_ebs = EBS+EXTRA_EBS
                else:
                    table_ebs = EBS
                tableLabel="results_tuning_"+ag+"_on"+special_evals+"_"+avgf
                
            #tableTitle=r"""Tuning results for %s targets with %s. %s aggregated solution quality is normalized between best known and worst encountered result, where smaller value is better. %ss are listed in parentheses. Statistically better results are bolded. Evaluation budget (EB) violations of more than 5\%% are italicized.""" % (target, special_evals_label, avgf.capitalize(), sddevlabel.capitalize())
            tableTitle=r"""%s tuning results for %s targets on %s.""" % (avgf.capitalize(), target, special_evals_label)
            tableNotes=r"""Results are given as percentage from the aggerated best known solution (relative optimality gap). Statistically better results are bolded. Evaluation budget (EB) violations of more than 5\% are italicized.""" 
            figgen.produceLatexTable(nresults,tableTitle, tableNotes, tableLabel, table_ebs, algos, TUNERS,
                                     sbs=table_sbs, warn_ebd=WARNING_EVALUATIONS_DIFF,
                                     significantlyDifferent=statistically_significant_best, vert=True)#, set_label=special_evals_short_label)
 

    if RG75_STYLE and produce_table:
        (eblabel, qlabel, sddevlabel) = uavgFunc([],[], True)
        
        target = ", ".join(all_algos)
        table_sbs = 3
        table_ebs = EBS
        tableLabel="all_results_tuning_"+"_".join(all_algos)+"_on"+special_evals+"_"+avgf
            
        #tableTitle=r"""Tuning results for %s targets with %s. %s aggregated solution quality is normalized between best known and worst encountered result, where smaller value is better. %ss are listed in parentheses. Statistically better results are bolded. Evaluation budget (EB) violations of more than 5\%% are italicized.""" % (target, special_evals_label, avgf.capitalize(), sddevlabel.capitalize())
        tableTitle=r"""%s tuning results for %s targets on %s.""" % (avgf.capitalize(), target, special_evals_label)
        tableNotes=r"""Results are given as percentage from the aggerated best known solution (relative optimality gap). Statistically better results are bolded. Evaluation budget (EB) violations of more than 5\% are italicized.""" 
        figgen.produceLatexTable(all_nresults,tableTitle, tableNotes, tableLabel, table_ebs, all_algos, TUNERS,
                                 sbs=table_sbs, warn_ebd=WARNING_EVALUATIONS_DIFF,
                                 significantlyDifferent=all_statistically_significant_best, vert=False)#, set_label=special_evals_short_label)
    
       
    #fi ag in ALGO_GROUP:
                
    if PRODUCE_MAD_MEDIANS:
        mads = []
        for tuner in TUNERS:
            madl = [rp[3] for key, rp in all_nresults.items() if key[0]==tuner]
            mads.append( (mean(madl), tuner) )
            
        mads.sort()
        for medm, t in mads:
            print "%s, %f" % (t, medm)
        
    
def parse_cmd_arguments():
    parser = argparse.ArgumentParser(description='A script containing a collection of result parsing and table and figure producing routines.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', help='Verbosity (0 = off, 1 = info, 2 = debug)', default=0, dest='verbosity', type=int)
    parser.add_argument('-mt', help='Produce main result tables', dest='result_tables', action='store_true')
    parser.add_argument('-at', help='Produce full set of tables', dest='all_tables', action='store_true')
    parser.add_argument('-pp', help='Produce parallel plot files', dest='parallel_plots', action='store_true')
    parser.add_argument('-lp', help='Produce line plot files', dest='line_plots', action='store_true')
    parser.add_argument('-bp', help='Produce box plot files', dest='box_plots', action='store_true')
    parser.add_argument('-sp', help='Produce scatter plot files', dest='scatter_plots', action='store_true')
    parser.add_argument('-ee', help='Include extra evaluation budget', dest='extra_evals', action='store_true')
    
    parser.add_argument('-ap', help='Produce ALL plot files', dest='all_plots', action='store_true')
    
    parser.add_argument('-vg', help='Produce vector graphics (eps)', dest='vector_graphics', action='store_true')
    parser.add_argument('-cm', help='Check and print if there is incomplete results', dest='check_missing', action='store_true')
    
    parser.add_argument('-ucache', help='Use cached results (for faster load)', dest='use_cache', action='store_true')
    parser.add_argument('-pcache', help='Produce cached results (to make it possible to use -ucache)', dest='produce_cache', action='store_true')
    
    parser.add_argument('-jf', help='Produce journal style figures (give the width of column in points)', default=0.0, dest='journal_figures', type=float)
    parser.add_argument('-pf', help='Produce poster style figures (give the width of column in points)', default=0.0, dest='poster_figures', type=float)
    
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    return vars(parser.parse_args())
        

if __name__ == "__main__":
    
    args = parse_cmd_arguments()
    VERBOSE = args['verbosity']
    JOURNALSTYLE = 'poster'
    ee = args['extra_evals']
    
    avgfs = ["median", "mean", "best", "worst"]
    
    if args['journal_figures']>0.1 or args['poster_figures']>0.1:
        if args['journal_figures']>0.1:
            fig_width_pt = args['journal_figures']  # Get this from LaTeX using \showthe\columnwidth    
            JOURNALSTYLE = 'journal'
            linewt = 1.0
            axeswt = 1.5
            # 469.75499    
        if args['poster_figures']>0.1:
            fig_width_pt = args['poster_figures']  # Get this from LaTeX using \showthe\columnwidth
            linewt = 2.5
            axeswt = 1.5
        
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
        
    if args['produce_cache'] or args['check_missing']:
        if args['check_missing'] and not args['produce_cache']:
            avgfs_loop = [avgfs[0]]
        else:
            avgfs_loop = avgfs
            
        pc = args['produce_cache']
        cm = args['check_missing']
        print        
        print "Parse tuning run results:"
        print "========================="
        for avgf in avgfs_loop:
            main("Results", fig_exts = [], produce_table=False, avgf=avgf, check_missing=cm, produce_cache=pc)
        print 
        print "Parse testset evaluations:"
        print "=================================="
        for avgf in avgfs_loop:
            main("Evals_testset", fig_exts = [], produce_table=False, avgf=avgf, check_missing=cm, produce_cache=pc)
        print        
        print "Parse trainset evaluations:"
        print "==================================="
        for avgf in avgfs_loop:
            main("Evals_we", fig_exts = [], produce_table=False, avgf=avgf, check_missing=cm, produce_cache=pc)

    if args["result_tables"]:
        main("Evals_testset", produce_table=True, avgf="median", use_cache=args['use_cache'], extra_ebs=ee)
        
    elif args["all_tables"]:
        # Recreates tables
        for a in avgfs:
            main("Evals_testset", produce_table=True, avgf=a, use_cache=args['use_cache'], extra_ebs=ee)
            print 
            print "\\clearpage"
            print 
            main("Evals_we", produce_table=True, avgf=a, use_cache=args['use_cache'], extra_ebs=ee)
            print 
            print "\\clearpage"
            print         
    # Recreates plots
    exts = ["png"]#, "eps"]  
    if args["vector_graphics"]:
        exts = ["eps"]  
    
    if args["parallel_plots"] or args["all_plots"]:
        main("Results", fig_exts=exts, graph_types=["parallel"], produce_table=False, use_cache=args['use_cache'])
    if args["line_plots"] or args["all_plots"]:
        for a in avgfs:
            main("Evals_testset", fig_exts=exts, avgf=a, graph_types=["line"], produce_table=False, use_cache=args['use_cache'])
            main("Evals_we", fig_exts=exts, avgf=a, graph_types=["line"], produce_table=False, use_cache=args['use_cache'])
    if args["box_plots"] or args["all_plots"]:
        main("Evals_testset", fig_exts=exts, avgf="median", graph_types=["boxplot"], produce_table=False, use_cache=args['use_cache'])
        main("Evals_we", fig_exts=exts, avgf="median", graph_types=["boxplot"], produce_table=False, use_cache=args['use_cache'])
    if args["scatter_plots"] or args["all_plots"]:
        main("Results", fig_exts=exts, graph_types=["scatter"], produce_table=False, use_cache=args['use_cache'])
        
    
