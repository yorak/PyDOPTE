# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 18:55:18 2015

@author: juherask

Combine 3cv evaluations into one megaevals file that corresponds to 
 non _cv3 evals (all tuned parameter sets evaluated on the entire problem set)
"""

import glob
import ast
from collections import defaultdict

files = "christofides_3cv/evals_*.txt"
outlines_by_target = defaultdict(list)

for evalsFile in glob.glob(files):
    
    if "Default" in evalsFile or "fullset" in evalsFile:
        continue
    
    print "Reading evaluations from file ", evalsFile
        
    counter = 0
    repts = 0
    
    rf = open(evalsFile)
    rflines = rf.readlines()
    rf.close()
    key = None
    
    
    
    for line in rflines:
        line = line.strip()
        if line=="" or line[0]=="=":
            continue
        
        lparts = line.split(";")
                
        #   0          1       2      3         4    5    6       7            8      9
        # task_key; run_id ; rep_id; instance; seed; q; a.evals; ps_hash ; tps id>;<k>;
        key = ast.literal_eval( lparts[0] )
        run_id = int(lparts[1])
        repeat_idx = int(lparts[2])
        benchmark_name = lparts[3]
        seed = int(lparts[4])
        instance_quality = float(lparts[5])
        ps_actual_evals = int(lparts[6])
        ps_hash = ast.literal_eval(lparts[7])
        ps_id = int(lparts[8])
        fold_id = int(lparts[9])
        
        # Print in non-cv format
        outlines_by_target[key[:2]].append( ";".join(
            [
            str(key), # 0
            "%02d"%ps_id, # 1 (format for sorting)
            "%02d"%repeat_idx, # 2 (format for sorting)
            str(benchmark_name), # 3
            str(seed),# 4
            str(instance_quality), # 5
            str(ps_actual_evals), # 6
            str(ps_hash), # 7
            ])+"\n"
        )

# problem: there should be 15 pss

for key, lines in outlines_by_target.items():
    lines.sort()
    fn = "evals_{tuner}_{target}_10repts_fullset.txt".format(
        tuner=key[0],
        target=key[1].replace(" ","_"))
    of = file(fn, "w")
    of.writelines(lines)
    of.close()
