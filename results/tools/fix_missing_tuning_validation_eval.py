# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 10:45:13 2013

Retries those algorithm evaluations where the quality is given
value and 
and writes a new file into fixed/ folder.

@author: juherask
"""

import random
import ast
from time import sleep
from parse_results import _getAlgoAndTunerFromFilename
from Experiments.algorithmFactory import BuildAlgorithm


FILES_TO_FIX = [
#e.g.
r"augerat/result_GGA_vrph_augerat_ej_10sec_1000eval_13repts.txt",
r"augerat/result_GGA_vrph_augerat_ej_10sec_100eval_13repts.txt",
r"augerat/result_GGA_vrph_augerat_ej_10sec_500eval_13repts.txt",
r"augerat/result_ParamILS_vrph_augerat_ej_10sec_1000eval_13repts.txt",
r"augerat/result_ParamILS_vrph_augerat_ej_10sec_100eval_13repts.txt",
r"augerat/result_ParamILS_vrph_augerat_ej_10sec_500eval_13repts.txt",
]
QUALITY_VALUE_TO_FIX = "e+308"
RETRYCOUNT = 10 

def evaluate(algo, tuned_ps):
    algokey = algo.lower().replace(" ", "_")
    #print algokey
    # Support for old style algo desc
    if algokey in ("vrph_rtr", "vrph_ej", "vrph_sa"):
        algoparts = algokey.split("_")
        algokey = algoparts[0]+"_christofides_"+algoparts[1]
    
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
        
    # All tuned Parameter Sets  
    ctps = dict(fps.items()+tuned_ps.items())
    
    # Create
    total_q = 0.0
    for benchmark in testset:
    
        if (isw):
            ctps[isw]=benchmark   
        if (ssw):
            ctps[ssw]=random.randint(0, 100000000)
        
        # NOTE: Ugly quickhack to try to resolve situations
        #  where the algorithm fails with given seed
        success = False
        retries = RETRYCOUNT 
        while not success and retries>0:
            try:
                print "DEBUG: evaluating %s with parameters %s" % (algokey, ctps)
                retries-=1
                evv = algo.Evaluate(ctps)
                #evv = {"obj":1.0}
                #sleep(1.0)
                print "DEBUG: got result %f" % evv["obj"]
                success = True
            except Exception as e:
                #print e
                if (ssw):
                    ctps[ssw]+=1
                else:
                    raise e
                
        total_q += evv["obj"]
    return total_q
    
for rfn in FILES_TO_FIX:
    rfi = open(rfn, 'r')
    rfo = open(r"fixed/"+rfn, 'w+')

    eval_result_line = ""
    actual_eval_line = ""
    tuned_param_line = ""
    requires_eval = True
    
    tuner, algo, parts = _getAlgoAndTunerFromFilename(rfn)
        
    for line in rfi.readlines():
        if "Quality:" in line:
            if QUALITY_VALUE_TO_FIX in line:
                requires_eval = True
                eval_result_line = "???"
            else:
                requires_eval = False
                eval_result_line = line
        elif "Evaluations:" in line:
            actual_eval_line = line
        elif "Tuned parameters:" in line:
            tuned_param_line = line
            if requires_eval:
                tpstr = tuned_param_line.replace("Tuned parameters: ", "")
                tp = ast.literal_eval(tpstr)
                eval_result_line = "Quality: %f\n" % evaluate(algo, tp)
            
            # Output
            print eval_result_line
            print actual_eval_line
            print tuned_param_line
            rfo.write(eval_result_line)
            rfo.write(actual_eval_line)
            rfo.write(tuned_param_line)
        else:
            print line
            rfo.write(line)
            
    rfi.close()
    rfo.close()
