# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 22:46:25 2011

@author: juherask
"""

import os
import sys
import random

from parse_results import parseResultsFromFiles, DEFAULT, TGT_REPTS_CV, CV_FOLDS, TGT_REPTS
from helpers import str2bool, dictHash, MAX_INT
from Experiments.algorithmFactory import BuildAlgorithm

# This can be used to do normal tuneset / testset evaluations on cross validated 
#  results instead of using fold-by-fold based instance sets.
FORCE_NORMAL_EVALS_ON_CV = False

def evaluate_results(repts, files, use_testset, simulate=False):
    
    seeds = []
    for i in range(repts):
        seeds.append(random.randint(0,MAX_INT))
    
    isCV = False
    if "3cv" in files:
        isCV = True
            
            
    # Get results from file. This includes parameter sets to evaluate
    results = parseResultsFromFiles(files, crossValidation=isCV)


    
    if simulate:
        print files, "found", len(results), "results"
    
    for key, values in results.items():
        # unpack key
        if (isCV):
            (tuner, algoname, evals) = key 
            (ar, rl, fl, mev, meq, seq, tpl, ql, evl, cv_training_set_list, cv_validation_set_list ) = values
            number_of_folds = max(fl)+1 # fl is fold indices
        else:
            (tuner, algoname, evals) = key 
            (ar, mev, meq, seq, tpl, ql, evl ) = values
        
        algokey = algoname.lower().replace(" ", "_")
        #print algokey
        # Support for old style algo desc
        if algokey in ("vrph_rtr", "vrph_ej", "vrph_sa"):
            algoparts = algokey.split("_")
            algokey = algoparts[0]+"_christofides_"+algoparts[1]
        
        if use_testset:
            algokey+="_testset"
            
        #print algokey
        algo, testset = BuildAlgorithm(algokey)
        apsd = algo.GetDefinition()
        algo.SetTimeLimit(10.0)

        isw = None
        ssw = None  
        if apsd.HasParameter( "Instance" ):
            isw = apsd.GetParameterSwitch("Instance")      
        if apsd.HasParameter( "Seed" ):
            ssw = apsd.GetParameterSwitch("Seed")
    
        fps = {}        
        for fp in apsd.FixedParameters():        
            fps[fp] = apsd.GetParameterDefault(fp)

        # Some sanity checking for cross validation
                
        
        # All tuned Parameter Sets
        for tpIdx in range(len(tpl)):
            # Only do as many as needed
            if isCV:
                if tpIdx>=TGT_REPTS_CV*CV_FOLDS:
                    continue
            elif tpIdx>=TGT_REPTS:
                continue
            
            tps = tpl[tpIdx]
            tpev = evl[tpIdx]

            ctps = dict(fps.items()+tps.items())
            
            # For cross validation, use only the validation set for evaluating
            if isCV and not FORCE_NORMAL_EVALS_ON_CV:
                if (use_testset):
                    testset = cv_validation_set_list[tpIdx]
                else:
                    testset = cv_training_set_list[tpIdx]
                fold_idx = fl[tpIdx]
                
            # Create 
            for benchmark in testset:
                for i in range(repts):
                    if (isw):
                        ctps[isw]='"'+benchmark+'"'
                    if (ssw):
                        ctps[ssw]=seeds[i]
                    
                    if simulate:
                        #print "Use algorithm %s to solve instance %s with parameters %s, repeat %d of %d" % (algokey, benchmark, str(tps), i+1, repts)
                        print str(tps)
                        evv = {"obj":-1.0}
                    else:
                        # NOTE: Ugly quickhack to try to resolve situations
                        #  where the algorithm fails with given seed
                        success = False
                        while not success:
                            try:
                                evv = algo.Evaluate(ctps)
                                success = True
                            except Exception as e:
                                if (ssw):
                                    ctps[ssw]+=1
                                else:
                                    raise e
                                    
                                
                            
                    ps_hash = dictHash(ctps)
                    
                    #<key>;<tuning_repetition_id>;<repeat idx>;<benchmark_name>; (continues...)
                    # (continues...) <seed>;<evaulation result>;<actual tuning evaluations>;<hash_of_the_parameter_set_seed_and_benchmark>
                    if not isCV or FORCE_NORMAL_EVALS_ON_CV:
                        line = "%s;%d;%d;%s;%d;%f;%d;%d" % (str(key), tpIdx, i, os.path.basename(benchmark), seeds[i], evv["obj"], tpev, ps_hash)
                    else:
                        if tpIdx/number_of_folds!=rl[tpIdx]:
                            raise IOError("Tuned parameter set %d for result %s, belongs to wrong repetition."%\
                                (tpIdx, str(key)) )
                        # k (as in k-fold cross validtion) concecutive parameter confs are of the same repeat. 
                        #  also add ;<tuned parameter set Id>;<k>; to the end of the line
                        line = "%s;%d;%d;%s;%d;%f;%d;%d;%d;%d" % (str(key), tpIdx/number_of_folds, i, os.path.basename(benchmark), seeds[i], evv["obj"], tpev, ps_hash, tpIdx, fold_idx )
                        
                    yield line
                    
            # Default tuner has only 1 parameter set (the default!)
            if tuner==DEFAULT:
                break
  
def main(args):
    

    if len(args)<2:
        print "Usage: evaluate_results <file> <repetitions>  [\"testset\"] [simulate]"
        print " Evaluates tuned parameters from the tuning experiment output files."
        print " You can use wildcards in <file>, for example result_*.txt"
        print " Evaluates everything in those files."
        print " Optional \"testset\" option can be used to compute evaluations on"
        print " testset."
        print " Optional simulate boolean argument can be used to skip the actual"
        print " evaluations and only simulate the run."
        
        exit()
        
    # Read cmdline args    
    files = args[0]
    repts = int(args[1])
    simulate = False
    use_testset = False
    if len(args)>2:
        tmpsim = str2bool(args[2])
        if tmpsim:
            simulate = tmpsim
        else:
            if args[2]=="testset":
                use_testset = True
            if len(args)>3:
                simulate = str2bool(args[3])
        
    #print files, repts, use_testset, simulate
    #return
    
    # Do the actual evaluations
    for line in evaluate_results(repts, files, use_testset, simulate):
        print line
    
    
if __name__ == "__main__":
    #main(["result_REVAC_vrpsd_acs_5000eval_10repts.txt", 1, "T"])
    main(sys.argv[1:])
    
    
