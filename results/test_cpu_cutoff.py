# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 22:46:25 2011

@author: juherask
"""

import os
import sys
import random
import time
from math import floor
from os import path

from helpers import str2bool, dictHash, MAX_INT
from Experiments.algorithmFactory import BuildAlgorithm, GetSupported


def call_algoritms(repts, use_testset, simulate, algos=None):
    total_time = 0.0
    
    if not algos:
        algos = GetSupported()

    for algoname in algos:
        algoname = algoname.replace("[_testset]", "")    
        # Not included in the tests
        if algoname=="gfe" or algoname=="vrpsd_fr":
            continue
    
        cutoffs = [floor(1 + (x+3)**2.5/10) for x in range(15)];
        # [2.0, 4.0, 6.0, 9.0, 13.0, 19.0, 25.0, 32.0, 41.0, 50.0,
        #   61.0, 74.0, 88.0, 103.0, 120.0]
        for cutoff in cutoffs:
            seeds = []
            for i in range(repts):
                seeds.append(random.randint(0,MAX_INT))
            
            algokey = algoname.lower().replace(" ", "_")
            #print algokey
            
            if use_testset:
                algokey+="_testset"
                    
            #print algokey
            algo, testset = BuildAlgorithm(algokey)
            apsd = algo.GetDefinition()
            algo.SetTimeLimit(cutoff)
        
            isw = None
            ssw = None  
            tmo = None
            if apsd.HasParameter( "Instance" ):
                isw = apsd.GetParameterSwitch("Instance")      
            if apsd.HasParameter( "Seed" ):
                ssw = apsd.GetParameterSwitch("Seed")
            if apsd.HasParameter( "Timeout" ):
                tmo = apsd.GetParameterSwitch("Timeout")
            else:
                print "error, no timeout parameter for %s. The task makes no sense."%algoname
            
            # Evaluate with default paramters        
            ctps = apsd.NewDefaultParameterSet()
            # Or use one read from file
            if type(algos) is dict:
                ctps.update(algos[algoname])
                ctps[tmo]=cutoff # the tuned ps might have this set, override
            
            # Create 
            for benchmark in testset:
                for i in range(repts):
                    
                    while path.isfile("pause_test_cpu_cutoff.txt"):
                        time.sleep(3.33)
                    
                    if (isw):
                        ctps[isw]=benchmark   
                    if (ssw):
                        ctps[ssw]=seeds[i]
                    
                    ps_hash = dictHash(ctps)
                    
                    if simulate:
                        evv = {"obj":-1.0, "time":-1.0}
                        ps_hash = str(ctps)
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
                                    
                    
                    total_time+=cutoff
                    
                    #<key>;<cutoff>;<wall_time>;<repeat idx>;<benchmark_name>; (continues...)
                    # (continues...) <seed>;<evaulation result>;<hash_of_the_parameter_set_seed_and_benchmark>
                    line = "%s;%.2f;%.4f;%d;%s;%d;%f;%s" % \
                        (str(algokey), cutoff, evv["time"], i, path.basename(benchmark),\
                         seeds[i], evv["obj"],  str(ps_hash))
                    yield line
                    
                
    #print total_time/3600.0
  
def main(args):
    

    if len(args)<2:
        print "Usage: test_cpu_cutoff <repetitions> [\"testset\"] [parameterfile] [simulate] [algo1] [algo2] ..."
        print " Test solvers with default parameters and with 15 different timeouts."
        print " Optional simulate boolean argument can be used to skip the evaluations."
        print " If no list of algorithms or a parameter file (csv/txt) with a line format of:"
        print " <algorithm name>;<quality>;<parameter set as python dict>"
        print " are given, the test is done for all algos."
        
        exit()

    supported_algos = [ an.replace("[_testset]", "") for an in GetSupported() ]
    supported_algos = list(set(supported_algos)) # get uniq
    selected_algos = []

    # Read cmdline args    
    repts = int(args[0])
    simulate = False
    use_testset = False
    parameters_fn = None
    if len(args)>1:
        for arg in args[1:]:
            tmpsim = str2bool(arg)
            pf_ext = path.splitext(arg)[1]
            if arg=="testset":
                use_testset = True
            elif (pf_ext=='.csv' or pf_ext=='.txt') and path.isfile(arg):
                parameters_fn = arg
            elif arg in supported_algos:
                selected_algos.append(arg)
            elif tmpsim:
                simulate = tmpsim

    #print files, repts, use_testset, simulate
    #return

    if parameters_fn:
        algos_in_file = {}
        pf = open(parameters_fn, "r")
        for l in pf.readlines():
            parts = l.split(";")
            algo = parts[0].lower().replace(' ', '_')
            params = eval(parts[2])
            # If selected algos are set, only take those that are selected!
            if selected_algos:
                if algo in selected_algos:
                    algos_in_file[algo] = params                    
            else:
                algos_in_file[algo] = params
                
        # Replace with dict       
        selected_algos = algos_in_file
    elif not selected_algos:
        selected_algos = None
    
    #print selected_algos

    # Do the actual evaluations
    for line in call_algoritms(repts, use_testset, simulate, selected_algos):
        print line
    
    
if __name__ == "__main__":
    #main(["result_REVAC_vrpsd_acs_5000eval_10repts.txt", 1, "T"])
    main(sys.argv[1:])
    
    
