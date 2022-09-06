function run_eval_on_algo {
  folder=$1
  algo=$2
  tuner=$3
  (python evaluate_results.py ${folder}/result_${tuner}_${algo}_\*repts.txt 10 testset 0 | tee evals_${tuner}_${algo}_10repts_testset.txt)&
  sleep 1
  (python evaluate_results.py ${folder}/result_${tuner}_${algo}_\*repts.txt 10 trainset 0 | tee evals_${tuner}_${algo}_10repts_new.txt)&
  sleep 1
}

for tuner in Default RTnR IRace SMAC REVAC CMAES ParamILS GGA
do
  run_eval_on_algo augerat_rerun vrph_augerat_rtr ${tuner}
done

date
echo "Waiting for 10eval vrph_rtr_a batch..."
wait
date
echo "...10 eval vrpsd batch done"

for tuner in Default RTnR IRace SMAC REVAC CMAES ParamILS GGA
do
  run_eval_on_algo augerat vrph_augerat_sa ${tuner}
done

date
echo "Waiting for 10eval vrph_sa_a batch..."
wait
date
echo "...10 eval vrpsd batch done"

for tuner in Default RTnR IRace SMAC REVAC CMAES #ParamILS GGA
do
  run_eval_on_algo augerat vrph_augerat_ej ${tuner}
done

date
echo "Waiting for 10eval vrph_ej_a batch..."
wait
date
echo "...10 eval vrpsd batch done"
