#!/bin/bash

(python test_cpu_cutoff.py 10 F vrph_ej_a | tee cutoff_vrph_rtr_c_10r.csv)&
sleep 1
(python test_cpu_cutoff.py 10 F vrph_sa_a | tee cutoff_vrph_sa_c_10r.csv)&
sleep 1

wait

#(unbuffer python test_cpu_cutoff.py 3 False 2>errors_cutoff_test2_1of4_r3.log | tee result_cutoff_test2_1of4_r3.csv)&
#sleep 1
#(unbuffer python test_cpu_cutoff.py 3 False 2>errors_cutoff_test2_2of4_r3.log | tee result_cutoff_test2_2of4_r3.csv)&
#sleep 1
#(unbuffer python test_cpu_cutoff.py 3 False 2>errors_cutoff_test2_3of4_r3.log | tee result_cutoff_test2_3of4_r3.csv)&
#sleep 1
#(unbuffer python test_cpu_cutoff.py 3 False 2>errors_cutoff_test2_4of4_r3.log | tee result_cutoff_test2_4of4_r3.csv)&
#sleep 1
