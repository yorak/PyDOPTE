from Tuners.ParamILSTuner import ParamILSTuner

import algorithmFactory
import experiment_template
from ParameterSet import MAX_FLOAT, MAX_INT

import sys
import PathManager




def SetupAndRunExperiment(vrhpAlgoId, repetitions, evaluations, algoCutoff, verbosity, k_folds, rng_seed_override):
    
#    #DEBUG
#    algoCutoff = 2.0
    
    
    # 1. Introduce algorithm
    
    algo, instances = algorithmFactory.BuildAlgorithm(vrhpAlgoId)
    algo.SetTimeLimit(algoCutoff)

    
    # 2. Introduce tuner
    
    #Tuner
    DISCRETIZATION_STEPS = 10        
    deterministic = int( not algo.GetDefinition().HasParameter("Seed") )

    tuner = ParamILSTuner(PathManager.GetTuningBasePath()+"/Tuners/paramils2.3.5/bin")
    tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    tunerParameters["-maxEvals"]=evaluations
    #tunerParameters["-maxEvals"]=1000
    tunerParameters["-numRun"]=0
    tunerParameters["-discretization"]=DISCRETIZATION_STEPS
    tunerParameters["-solf_deterministic"]=deterministic
    tunerParameters["-solf_tunerTimeout"]=MAX_INT

    # Verbosity 1 just enables logging. Anything over it produces more.
    if verbosity and abs(verbosity)>1:
        tunerParameters["-userunlog"]=1
    else:
        tunerParameters["-userunlog"]=0

    # 3. Tune
    
    experiment_template.RunExperiment(algo, instances, tuner, tunerParameters, repetitions, verbosity, k_folds, rng_seed_override)

if __name__ == '__main__':
    #RunExperiment("vrph_sa", 1, 100)
    #exit()
    
    experiment_template.ExperimentFromCmdLine(sys.argv, SetupAndRunExperiment)

