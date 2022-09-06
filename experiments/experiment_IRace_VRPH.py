from Tuners.IRaceTuner import IRaceTuner

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
    
    tuner = IRaceTuner(PathManager.GetTuningBasePath()+"Tuners/irace-0.9/")
    tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    tunerParameters["--max-experiments"]=evaluations
    if evaluations<500:
        epi = 60 # Seems to work for 100 eval, 14 instances
        tunerParameters["--experiments-per-iteration"]=epi
        # For irace 1.07, the 100e case needs more tricks
        tunerParameters["--min-survival"]=1 # we want to find the 1
        tunerParameters["--iterations"]=3
        
    #if evaluations<800:
    #    epi = max(28, evaluations/10)
    #    tunerParameters["--experiments-per-iteration"]=epi
    
    # verbosity 1 enables logging. Anything over it makes it more verbose.
    if verbosity and abs(verbosity)>1:
        vsw = tuner.GetDefinition().GetParameterSwitch("Verbosity")
        tunerParameters[vsw] = abs(verbosity-1)
    
    # 3. Tune
    experiment_template.RunExperiment(algo, instances, tuner, tunerParameters, repetitions, verbosity, k_folds, rng_seed_override)


if __name__ == '__main__':
    #RunExperiment("vrph_sa", 1, 100)
    #exit()
    
    experiment_template.ExperimentFromCmdLine(sys.argv, SetupAndRunExperiment)
    

