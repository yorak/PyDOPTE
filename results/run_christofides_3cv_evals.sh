function start_evals_for_algo {
  folder=$1
  algo=$2
  tuner=$3
  evals=$4
  (unbuffer python evaluate_results.py ${folder}/result_${tuner}_${algo}_\*${evals}eval_3cv_5repts\*.txt 10 0 | tee evals_${tuner}_${algo}_${evals}e_10repts_3cv_we.txt)&
  sleep 1
}

for evals in 500
do

for algo in vrph_christofides_sa
do

for tuner in RTnR IRace SMAC REVAC CMAES ParamILS GGA
do
  start_evals_for_algo christofides_3cv ${algo} ${tuner} ${evals}
done

date
echo "Waiting for evaluation 10 repts ${algo} for all tuners with ${evals}e batch..."
wait
date
echo "...10 repts evaluations on ${algo} for all tuners with ${evals}e done"

done

done
