#!/bin/bash

# This is a template script to start batch runs of several experiments

for budget in 1000
do
for tuner in RTnR IRace ParamILS SMAC REVAC CMAES #GGA
do
for target in "vrph_augerat_ej" "vrph_augerat_rtr" "vrph_augerat_sa"
do

(python experiment_${tuner}_VRPH.py ${target} 13 ${budget} | tee result_${tuner}_${target}_Augerat14_10sec_${budget}eval_13repts.txt)&
sleep 5

if [ -f break_run_batch ]
then
    	echo "Breaking execution of batch file"
        exit
fi

done # end tuning target loop

date
echo "Waiting for the tuning of vrph targets with ${tuner}..."
wait
echo "...done"

done # end tuner loop



# GGA is multithreaded so run it by itself
tuner=GGA
for target in "vrph_augerat_ej" "vrph_augerat_rtr" "vrph_augerat_sa"
do

python experiment_${tuner}_VRPH.py ${target} 13 ${budget} | tee result_${tuner}_${target}_Augerat14_10sec_${budget}eval_13repts.txt

if [ -f break_run_batch ]
then
    	echo "Breaking execution of batch file"
        exit
fi

done # end gga target loop

done # end budget loop


