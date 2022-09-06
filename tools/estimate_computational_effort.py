# -*- coding: utf-8 -*-
"""
Created on Wed Mar 06 14:12:32 2013

@author: juherask
"""

EVAL_REPTS = 10
REPTS = 10
EBS = [100, 500, 1000]
EXTRA_EBS = [5000]
TUNERS = 7
INSTANCES = 14
CUTOFF = 10
VRPH_ALGOS = 3
VRPSD_ALGOS = 5

tuned_vrph_c_time = CUTOFF*REPTS*sum(EBS)*TUNERS*VRPH_ALGOS
evals_vrph_c_time = CUTOFF*INSTANCES*EVAL_REPTS*REPTS*TUNERS*VRPH_ALGOS*len(EBS)*1

tuned_vrph_a_time = tuned_vrph_c_time
evals_vrph_a_time = evals_vrph_c_time*2

tuned_vrpsd_time = CUTOFF*REPTS*(sum(EBS)*TUNERS*VRPSD_ALGOS + sum(EXTRA_EBS)*TUNERS*1)
evals_vrpsd_time = CUTOFF*INSTANCES*EVAL_REPTS*REPTS*TUNERS*(VRPSD_ALGOS*len(EBS)+1*len(EXTRA_EBS))*2

print "Total CPU time", (tuned_vrph_c_time+evals_vrph_c_time+
                        tuned_vrph_a_time+evals_vrph_a_time+
                        tuned_vrpsd_time+evals_vrpsd_time)/(3600.0*24)
print

tuned_vrph_c_cnt = REPTS*len(EBS)*TUNERS*VRPH_ALGOS
tuned_vrph_a_cnt = tuned_vrph_c_cnt
tuned_vrpsd_cnt = REPTS*(len(EBS)*TUNERS*VRPSD_ALGOS + len(EXTRA_EBS)*TUNERS*1)

print "Total tuning runs ", tuned_vrph_c_cnt+tuned_vrph_a_cnt+tuned_vrpsd_cnt