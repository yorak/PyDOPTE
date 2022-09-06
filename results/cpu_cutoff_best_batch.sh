#!/bin/bash

(python test_cpu_cutoff.py 10 new_best_vrph_tuned_parameters_per_tgt.csv F | tee cutoff_tuned_best_vrph_10r.csv)&
sleep 1

(python test_cpu_cutoff.py 10 new_best_vrpsd1_tuned_parameters_per_tgt.csv F | tee cutoff_tuned_best_vrpsd1_10r.csv)&
sleep 1

(python test_cpu_cutoff.py 10 new_best_vrpsd2_tuned_parameters_per_tgt.csv F | tee cutoff_tuned_best_vrpsd2_10r.csv)&
sleep 1

wait
