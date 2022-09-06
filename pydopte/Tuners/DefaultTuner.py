# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 17:28:01 2011

@author: juherask
"""

from ParameterSet import *
from InternalTuner import *
from Algorithms.GFEAlgorithm import *
import PathManager


class DefaultTuner(InternalTuner):
    """A tuner that has parameters defined in tunerParameterSetDefinition
    ( a ParameterSetDefinition class instance )"""
    def __init__(self):  
        InternalTuner.__init__(self)

    def Tune(self, tunerParameterSet=None ):
        """ Tunes the given algorithm with random sampling of paramters
        instancelist is assumed to be list of instancefiles
        list of instancefiles
        """

        if not tunerParameterSet:
            tunerParameterSet = self.GetDefinition().NewDefaultParameterSet()
        
        ## Ignored
        #stopConditions = self._getStoppingTriplet(tunerParameterSet)
        
        tuningTime = 0.0
        evaluations = 0
        
        tunedParameters = self._algorithm.GetDefinition().NewDefaultParameterSet()
        tunedObjective = self.calculateAlgorithmPerformance(\
            self._algorithm,\
            tunedParameters,\
            self._validation_instances )["obj"]
        
        # Build result
        tuningResult = {}
        tuningResult["time"] = tuningTime
        tuningResult["obj"] = tunedObjective
        tuningResult["ops"] = evaluations
        tuningResult["special"] = tunedParameters
        #TODO: Implement setting of the seed -> tuningResult["seed"] = seed
        return tuningResult 
        

""" Code that test the basic operation of the RandomTuner """    
def main():
    
    algo = GFEAlgorithm(10, 1)

    # Run random parameter tuner with defaults and with dummy algo
    tuner = DefaultTuner()
    dps = tuner.GetDefinition().NewDefaultParameterSet()
    dps["-eb"]=1 # Dummy set does not affact
    
    tuner.SetAlgorithm(algo)
    tuner.SetInstances([PathManager.GetTuningBasePath()+"Benchmarks/gfe/f1_c/f1_c_1.spc"])
    
    # Tune
    tuningResult = tuner.Tune(dps)
    print "Quality: " + str(tuningResult["obj"])
    print "Evaluations: " + str(tuningResult["ops"])
    print "Tuned parameters: " + str(tuningResult["special"])
    
if __name__ == '__main__':
    main()         
        
        
        

