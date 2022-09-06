#!/bin/bash

# This is a script to run simple tuning (function minmization) on all supported tuners
#  used as a smoke test

if [ ! $# == 2 -a ! $# == 3 ]; then
  echo "Usage: $0 all|gfe|vrph|vrpsd [repeats] [\"list of tuners\"]"
  exit
fi

repeats=3
if [[ -n "$2" ]] ; then
  repeats=$2
fi
tuners="Default RTnR GGA IRace ParamILS SMAC REVAC CMAES"
if [[ -n "$3" ]] ; then
  tuners=$3
fi


if [ "$1" == "all" -o "$1" == "gfe" ] ; then

  for tuner in $tuners
  do

  python experiment_${tuner}_VRPH.py "gfe" ${repeats} 100 | tee smoke_${tuner}_gfe_100eval_${repeats}repts.txt

  if [ -f break_run_batch ]
  then
  	echo "Breaking execution of batch file"
        exit
  fi

  done 
fi

# This is a script to run simple tuning (function minmization) on all supported tuners
#  used as a smoke test
#  1 targets from both solver families

if [ "$1" == "all" -o "$1" == "vrph" ] ; then

  target="vrph_augerat_rtr"

  for tuner in $tuners
  do

  python experiment_${tuner}_VRPH.py ${target} ${repeats} 10 | tee smoke_${tuner}_${target}_10eval_${repeats}repts.txt

  if [ -f break_run_batch ]
  then
	echo "Breaking execution of batch file"
        exit
  fi

  done
fi


if [ "$1" == "all" -o "$1" == "vrpsd" ] ; then

  target="vrpsd_acs"

  for tuner in $tuners
  do

  python experiment_${tuner}_VRPH.py ${target} ${repeats} 100 -vf 5 | tee smoke_${tuner}_${target}_100eval_${repeats}repts.txt

  if [ -f break_run_batch ]
  then
	echo "Breaking execution of batch file"
        exit
  fi

  done
fi
