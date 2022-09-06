from Tuners.GGATuner import GGATuner, reverse_estimate, reverse_estimate_linear

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
    
    tuner = GGATuner(PathManager.GetTuningBasePath()+"Tuners/gga")
    tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    
    ist = min(5, len(instances))
    ien = len(instances)
    if evaluations==100:
        (p,g) = 8,3
    elif evaluations==500:
        (p,g) = 15,7
    elif evaluations==1000:
        (p,g) = 20,10
    else:
        (p,g) = reverse_estimate_linear(evaluations, ist, ien)

    
    tunerParameters["-p"] = p
    tunerParameters["-g"] = g
    tunerParameters["-gf"] = g
    tunerParameters["-me"] = evaluations #Evaluations
    tunerParameters["-out"] = 1
    tunerParameters["-is"]=ist
    tunerParameters["-ie"]=ien
    tunerParameters["-sg"]=1

    # As in ansotegui
    tunerParameters["-t"]=8

    # verbosity 1 enables logging. Anything over it makes it more verbose.
    if verbosity and abs(verbosity)>1:
        vsw = tuner.GetDefinition().GetParameterSwitch("Verbosity")
        tunerParameters[vsw] = max(5, abs(verbosity-1))
    
    
    # 3. Tune
    
    experiment_template.RunExperiment(algo, instances, tuner, tunerParameters, repetitions, verbosity, k_folds, rng_seed_override)


if __name__ == '__main__':
    # usage: python experiment.py <algo_id> <repetitions> <evaluations> [-v[f] <level>]"
    
    experiment_template.ExperimentFromCmdLine(sys.argv, SetupAndRunExperiment)

