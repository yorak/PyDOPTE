from Tuners.CMAESTuner import CMAESTuner

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
    
    tuner = CMAESTuner()
    tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    tunerParameters["-eb"]=evaluations
    
    # 3. Tune
    
    experiment_template.RunExperiment(algo, instances, tuner, tunerParameters, repetitions, verbosity, k_folds, rng_seed_override)


if __name__ == '__main__':
    #RunExperiment("vrph_sa", 1, 100)
    #exit()
    
    experiment_template.ExperimentFromCmdLine(sys.argv, SetupAndRunExperiment)
    

