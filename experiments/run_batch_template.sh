#!/bin/bash

# This is a template script to start batch runs of several experiments

for budget in 100 500
#1000
do
for tuner in RTnR GGA IRace ParamILS REVAC CMAES
do
for target in "vrph_augerat_ej" "vrph_augerat_rtr" "vrph_augerat_sa"
do

python experiment_${tuner}_VRPH.py ${target} 12 ${budget} | tee result_${tuner}_${target}_Augerat_10sec_${budget}eval_12repts.txt

if [ -f break_run_batch ]
then
    	echo "Breaking execution of batch file"
        exit
fi

done
done
done
