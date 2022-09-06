""" Just simple test script to test the tuning out """

import Tuners.RandomTuner
import Tuners.GGATuner
import Tuners.ParamILSTuner
import PathManager

from Algorithms.VRPSDAlgorithms import *
from Algorithms.VRPHAlgorithms import *
from Algorithms.GFEAlgorithm import *
import os
import random

def TrackVRPHCrash():
    pl = ['-cutoff', 10.0, '-f', PathManager.GetTuningBasePath()+'Benchmarks/Christofides/Christofides_07.vrp', '-s', '1',
           '-h_oro', '1', '-h_1pm', '0', '-h_3pm', '0', '-t', '5729', '-m', '1', '-j', '10', '-h_tho', '1', '-h_two', '1', '-h_2pm', '1']
    
    algo = VRPH_EJ_Algorithm(PathManager.GetTuningBasePath()+"Solvers/VRPH/bin")
    
    ps = {}
    for i in range(len(pl)/2):
        ps[pl[2*i]]=pl[2*i+1]
    
    print ps
    
    algo.Evaluate(ps)
    
def RunSimpleVRPSDTest():
    
    SAMPLES = 14
        
    # Tune VRPSD_ACS_Algorithm.
    #algo = VRPSDAlgorithms.VRPSD_ACS_Algorithm(\
    #    "PathManager.GetTuningBasePath()+"Solvers/VRPSD/bin")
    #algo.SetTimeLimit(5.0)
    #INSTANCE_FOLDER = 'PathManager.GetTuningBasePath()+'Benchmarks/VRPSD/'
    #INSTANCE_REQUIRED_EXT = ".vrpsd"

    # Tune VRPH_EJ_Algorithm.
    algo = VRPH_RTR_Algorithm(PathManager.GetTuningBasePath()+"Solvers/VRPH/bin")
    algo.SetTimeLimit(5.0)
    
    INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/Christofides/'
    INSTANCE_REQUIRED_EXT = ".vrp"
    
    # Tune GFE (type 1).
    #algo = GFEAlgorithm(10, 1)
    #algo.SetTimeLimit(3.0)
    #INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/gfe/f1_c'
    #INSTANCE_REQUIRED_EXT = ".spc" #take the hand picked one

    ## Tune algorithm with random tuner.
    #EVALUATIONS = 1000
    #tuner = RandomTuner.RandomTuner()
    #tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    #tunerParameters["-eb"] = EVALUATIONS

    ## Tune with GGA
    POPULATION = 20
    GENERATIONS = 20
    tuner = GGATuner.GGATuner(PathManager.GetTuningBasePath()+"Tuners/gga")
    tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    tunerParameters["-p"] = POPULATION
    tunerParameters["-g"] = GENERATIONS
    tunerParameters["-out"] = 1
    tunerParameters["-v"] = 5
    
    ## Tune with ParamILS
    #tuner = ParamILSTuner.ParamILSTuner(PathManager.GetTuningBasePath()+"Tuners/paramils2.3.5/bin")
    #tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
    #tunerParameters["-userrunlog"]=1
    
    # Sample instances from instance folder
    instancefiles = []
    for fn in os.listdir(INSTANCE_FOLDER):
        extension = os.path.splitext(fn)[1]
        if extension==INSTANCE_REQUIRED_EXT:
            instancefiles.append(os.path.join(INSTANCE_FOLDER, fn))
    random.shuffle(instancefiles)
    sample = instancefiles[0:SAMPLES]

    # Define tuning task
    tuner.SetAlgorithm(algo)
    tuner.SetInstances(sample)
    
    
    # Run tuning
    tuningResult = tuner.Tune(tunerParameters)
    print "Quality: " + str(tuningResult["obj"])
    print "Evaluations: " + str(tuningResult["ops"])
    print "Tuned parameters: " + str(tuningResult["special"])
    
    tunedParameters = tuningResult["special"]
    defaultParameters = algo.GetDefinition().NewDefaultParameterSet()
    

    # Compare aganist default parameters.
    print
    
    isw = algo.GetDefinition().GetParameterSwitch("Instance")

    print "Test with tuned: " + str(tunedParameters)
    tunedSum = 0.0
    for instance in sample:
        tunedParameters[isw] = instance
        tunedSum += algo.Evaluate(tunedParameters)["obj"]
    print "Tuned parameters average quality: " + str(tunedSum/len(sample))
    print

    print "Test with defaults: " + str(defaultParameters)
    defaultSum = 0.0
    for instance in sample:
        defaultParameters[isw] = instance
        defaultSum += algo.Evaluate(defaultParameters)["obj"]
    print "Tuned parameters average quality: " + str(defaultSum/len(sample))
    print

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    TrackVRPHCrash()

