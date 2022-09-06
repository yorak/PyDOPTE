function start_tuneset_evals_for_algo {
  folder=$1
  algo=$2
  tuner=$3
  evals=$4
  (unbuffer python evaluate_results.py ${folder}/result_${tuner}_${algo}_\*.txt 90 0 | tee evals_${tuner}_${algo}_${evals}e_12repts_tuneset.txt)&
  sleep 1
  #(unbuffer python evaluate_results.py ${folder}/result_${tuner}_${algo}_\*.txt 10 testset 0 | tee evals_${tuner}_${algo}_${evals}e_12repts_testset.txt)&
  #sleep 1
}
function start_testset_evals_for_algo {
  folder=$1
  algo=$2
  tuner=$3
  evals=$4
  #(unbuffer python evaluate_results.py ${folder}/result_${tuner}_${algo}_\*.txt 10 0 | tee evals_${tuner}_${algo}_${evals}e_12repts_tuneset.txt)&
  #sleep 1
  (unbuffer python evaluate_results.py ${folder}/result_${tuner}_${algo}_\*.txt 90 testset 0 | tee evals_${tuner}_${algo}_${evals}e_12repts_testset.txt)&
  sleep 1
}

for evals in 500
do

for tuner in Default
do

for algo in "vrph_rtr_rw_F-n45" "vrph_rtr_rw_F-n72" "vrph_rtr_rw_F-n135" "vrph_rtr_rw_RT_385" "vrph_sa_rw_F-n45" "vrph_sa_rw_F-n72" "vrph_sa_rw_F-n135" "vrph_sa_rw_RT_385" "vrph_ej_rw_F-n45" "vrph_ej_rw_F-n72" "vrph_ej_rw_F-n135" "vrph_ej_rw_RT_385"
do
  start_testset_evals_for_algo realworld ${algo} ${tuner} ${evals}
done

date
echo "Waiting for testset evaluation 10 repts ${tuner} with ${evals}e batch..."
wait
date
echo "...10 repts testset evaluations on ${tuner} with ${evals}e done"

for algo in "vrph_rtr_rw_F-n45" "vrph_rtr_rw_F-n72" "vrph_rtr_rw_F-n135" "vrph_rtr_rw_RT_385" "vrph_sa_rw_F-n45" "vrph_sa_rw_F-n72" "vrph_sa_rw_F-n135" "vrph_sa_rw_RT_385" "vrph_ej_rw_F-n45" "vrph_ej_rw_F-n72" "vrph_ej_rw_F-n135" "vrph_ej_rw_RT_385"
do
  start_tuneset_evals_for_algo realworld ${algo} ${tuner} ${evals}
done

date
echo "Waiting for tuneset evaluation 10 repts ${tuner} with ${evals}e batch..."
wait
date
echo "...10 repts testset evaluations on ${tuner} with ${evals}e done"



done

done
