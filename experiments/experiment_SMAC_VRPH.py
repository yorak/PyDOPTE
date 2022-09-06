from Tuners.SMACTuner import SMACTuner

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
    
    tuner = SMACTuner(PathManager.GetTuningBasePath()+"Tuners/smac-v2.02.00-master-375")
    tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    tunerParameters["--totalNumRunsLimit"]=evaluations

    deterministic = int( not algo.GetDefinition().HasParameter("Seed") )
    tunerParameters["-solf_deterministic"]=deterministic
    #tunerParameters["-solf_tunerTimeout"]=MAX_INT
    
    # verbosity 1 enables logging, anything over it makes it more verbose
    if verbosity and abs(verbosity)>1:
        vlevels = tuner.GetDefinition().GetParameterRange("Verbosity")
        vsw = tuner.GetDefinition().GetParameterSwitch("Verbosity")
        # Offers 6 verbosity levels (0 is off)
        tunerParameters[vsw] = vlevels[ min( len(vlevels)-1, abs(verbosity-1) ) ]
        
    
    # 3. Tune
    
    experiment_template.RunExperiment(algo, instances, tuner, tunerParameters, repetitions, verbosity, k_folds, rng_seed_override)

if __name__ == '__main__':
    #RunExperiment("vrph_sa", 1, 100)
    #exit()
    
    experiment_template.ExperimentFromCmdLine(sys.argv, SetupAndRunExperiment)

