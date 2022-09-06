#!/bin/bash

# This is a template script to start batch runs of several experiments

for budget in 100 500
do
for tuner in RTnR SMAC REVAC CMAES #GGA ParamILS IRace
do
for target in "vrph_christofides_ej" "vrph_christofides_rtr" "vrph_christofides_sa"
do

(unbuffer python experiment_${tuner}_VRPH.py ${target} 5 ${budget} -k 3 | tee result_${tuner}_${target}_10sec_${budget}eval_3cv_5repts.txt)&
sleep 5

if [ -f break_run_batch ]
then
    	echo "Breaking execution of batch file"
        exit
fi

done # end tuning target loop

done # end tuner loop

date
echo "Waiting for the 3 fold cross validation tuning of vrph targets with ${tuner} and budget of ${budget}..."
wait
echo "...done"


# GGA is multithreaded so run it by itself
tuner=GGA
for target in "vrph_christofides_ej" "vrph_christofides_rtr" "vrph_christofides_sa"
do

unbuffer python experiment_${tuner}_VRPH.py ${target} 5 ${budget} -k 3 | tee result_${tuner}_${target}_10sec_${budget}eval_3cv_5repts.txt

if [ -f break_run_batch ]
then
    	echo "Breaking execution of batch file"
        exit
fi

done # end gga target loop

done # end budget loop


