from Tuners.RandomTuner import RandomTuner

import algorithmFactory
import experiment_template

import sys


def SetupAndRunExperiment(vrhpAlgoId, repetitions, evaluations, algoCutoff, verbosity, k_folds, rng_seed_override):
    
#    #DEBUG
#    algoCutoff = 2.0
    
    
    # 1. Introduce algorithm
    
    algo, instances = algorithmFactory.BuildAlgorithm(vrhpAlgoId)
    algo.SetTimeLimit(algoCutoff)

    
    # 2. Introduce tuner

    tuner = RandomTuner()
    tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    tunerParameters["-eb"] = evaluations # Evaluations
    tunerParameters["-rls"] = 0 # Disable ranking algorithm
    
    # NOTE: Ugly hack. Change the name so that the runexperiment produces it
    tuner.__class__.__name__="RTnR"    
    
    
    # 3. Tune
    
    experiment_template.RunExperiment(algo, instances, tuner, tunerParameters, repetitions, verbosity, k_folds, rng_seed_override)

if __name__ == '__main__':
    #RunExperiment("vrph_sa", 1, 100)
    #exit()
    
    experiment_template.ExperimentFromCmdLine(sys.argv, SetupAndRunExperiment)

