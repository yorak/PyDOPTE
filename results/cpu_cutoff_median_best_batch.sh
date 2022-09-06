#!/bin/bash

(python test_cpu_cutoff.py 10 best_vrph_tuned_parameters_per_tgt.csv F | tee cutoff_tuned_best_vrph_10r.csv)&
sleep 1
(python test_cpu_cutoff.py 10 median_vrph_tuned_parameters_per_tgt.csv F | tee cutoff_tuned_median_vrph_10r.csv)&
sleep 1

(python test_cpu_cutoff.py 10 best_vrpsd_tuned_parameters_per_tgt.csv F | tee cutoff_tuned_best_vrpsd_10r.csv)&
sleep 1
(python test_cpu_cutoff.py 10 median_vrpsd_tuned_parameters_per_tgt.csv F | tee cutoff_tuned_median_vrpsd_10r.csv)&
sleep 1

wait
