from Tuners.REVACTuner import REVACTuner

import algorithmFactory
import experiment_template

import sys
import PathManager

def SetupAndRunExperiment(vrhpAlgoId, repetitions, evaluations, algoCutoff, verbosity, k_folds, rng_seed_override):
    
#    #DEBUG
#    algoCutoff = 2.0
    
    
    # 1. Introduce algorithm
    
    algo, instances = algorithmFactory.BuildAlgorithm(vrhpAlgoId)
    algo.SetTimeLimit(algoCutoff)

    
    # 2. Introduce tuner
    
    tuner = REVACTuner(PathManager.GetTuningBasePath()+"Tuners/codREVAC/bin")
    tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    
    I = len(instances)
    # Cannot use the H*10=N, N*2=M formula
    
    # eval | M | N | H 
    # 100    5   2   2 
    # 500   10   5   2
    # 1000  20  10   2
    
    #M = max(10, int(evaluations/(I*11)+0.5))
    if evaluations<=100:
        M = max(5, 70/I)
    elif evaluations<=500:
        M = min(100, 140/I)
    elif evaluations<=1000:
        M = min(100, 280/I)
    else:
        M = 100
        
    N = max(3, M/2) 
    H = max(3, int(N/10+0.5))
    
    tunerParameters["-m"] = M
    tunerParameters["-n"] = N
    tunerParameters["-h"] = H
    tunerParameters["-eb"] = evaluations #Evaluations
    
    # verbosity 1 enables logging. Anything over it makes it more verbose.
    if verbosity and abs(verbosity)>1:
        vsw = tuner.GetDefinition().GetParameterSwitch("Verbosity")
        tunerParameters[vsw] = abs(verbosity-1)

    #tunerParameters["-v"] = 5    
    
    
    # 3. Tune
    
    experiment_template.RunExperiment(algo, instances, tuner, tunerParameters, repetitions, verbosity, k_folds, rng_seed_override)


if __name__ == '__main__':
    #experiment_template.ExperimentFromCmdLine(["experiment_REVAC_VRHP.py", "vrph_christofides_rtr", "1", "10", "-v", "2"], SetupAndRunExperiment)
    #exit()
    
    experiment_template.ExperimentFromCmdLine(sys.argv, SetupAndRunExperiment)

