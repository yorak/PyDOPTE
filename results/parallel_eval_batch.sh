function run_eval_on_algo {
# Parameters are 1=algo
	#(python evaluate_results.py result_CMAES_$1_\*.txt 10 | tee evals_CMAES_$1_10repts_new.txt)&
	#sleep 5
	#(python evaluate_results.py result_GGA_$1_\*.txt 10 | tee evals_GGA_$1_10repts_new.txt)&
	#sleep 5
	#(python evaluate_results.py result_IRace_$1_\*.txt 10 | tee evals_IRace_$1_10repts_new.txt)&
	#sleep 5
	#(python evaluate_results.py result_ParamILS_$1_\*.txt 10 | tee evals_ParamILS_$1_10repts_new.txt)&
	#sleep 5
	#(python evaluate_results.py result_RT_$1_\*.txt 10 | tee evals_RT_$1_10repts_new.txt)&
	#sleep 5
	#(python evaluate_results.py result_RTnR_$1_\*.txt 10 | tee evals_RT_$1_10repts_new.txt)&
	#sleep 5
	(python evaluate_results.py result_SMAC_$1_10sec_100eval_10repts.txt 10 | tee evals_SMAC_$1_100e_10repts_testdata.txt)&
	sleep 5
	(python evaluate_results.py result_SMAC_$1_10sec_500eval_10repts.txt 10 | tee evals_SMAC_$1_500e_10repts_testdata.txt)&
	sleep 5
	(python evaluate_results.py result_SMAC_$1_10sec_1000eval_10repts.txt 10 | tee evals_SMAC_$1_500e_10repts_testdata.txt)&
	sleep 5
}

run_eval_on_algo vrpsd_acs
run_eval_on_algo vrpsd_ea
run_eval_on_algo vrpsd_ils
run_eval_on_algo vrpsd_ts
run_eval_on_algo vrpsd_sa

date
echo "Waiting for 10eval vrpsd batch..."
wait
date
echo "...10 eval vrpsd batch done"
