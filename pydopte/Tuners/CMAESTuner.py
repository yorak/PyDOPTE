# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 17:28:01 2011

@author: juherask
"""

import cma
import sys
import numpy as np
import time

import PathManager
from ParameterSet import *
from InternalTuner import *


# This many first parameter sets get points for scoring to top RANKING_MAX for
#  each problem instance.
RANKING_MAX = 10 


class CMAESTuner(InternalTuner):
    """A tuner that has parameters defined in tunerParameterSetDefinition
    ( a ParameterSetDefinition class instance )"""
    def __init__(self):
        InternalTuner.__init__(self)
        self._definition.Add("Positive bias for default category values", "-dcb", 0, (0,1), False, True)
        
        

    """ Tunes the given algorithm with random sampling of paramters
    instancelist is assumed to be list of instancefiles
    list of instancefiles
    """
    
    @staticmethod
    def parameterSetToParameterVector(parameterSet, parameterSetDefinition, biasDefault=True):
        # Convert only tunable
        dpsi = []
        for k in parameterSetDefinition.TunableParameters():
            prange = parameterSetDefinition.GetParameterRange(k)
            
            borderCnt = len(prange)
            defaultVal = parameterSet[k]
            
            
            # Continous or boolean
            if borderCnt==2:
                borderDom = prange[1]-prange[0]
                defaultVal = (defaultVal-prange[0])/float(borderDom)
                dpsi.append( ((k, -1), defaultVal) )
            
            # Categorical
            elif borderCnt>2:
                # Add one variable for each category value
                for category in range(len(prange)):
                    if biasDefault:
                        # Default firing strength is stronger (0.75)
                        fs = 0.75 if prange[category]==defaultVal else 0.25
                    else:
                        fs = 0.5
                        
                    dpsi.append( ((k, category), fs ) )
        
        dpsi.sort()
        dpsiKeys, dpsiValues = zip(*dpsi)
        
        dpsiBounds = [[],[]]
        for pkey in dpsiKeys:
            prange = parameterSetDefinition.GetParameterRange(pkey[0])
            dpsiBounds[0].append(float(prange[0])) # lower bound
            dpsiBounds[1].append(float(prange[-1])) # upper bound
            
        return (dpsiValues, dpsiKeys, dpsiBounds)
            
    @staticmethod
    def parameterVectorToParameterSet(parameterVector, vectorKeys, vectorBounds, parameterSetDefinition):
        ps = parameterSetDefinition.NewDefaultParameterSet()
       
        i = 0
        while i < len(parameterVector):
            pkey = vectorKeys[i][0]
            
            # Continous or boolean
            if vectorKeys[i][1]==-1:
                if pkey in ps:
                    dataType = type(ps[pkey])
                    pvalue = parameterVector[i]*(vectorBounds[1][i]-vectorBounds[0][i])+vectorBounds[0][i]
                    if dataType is bool:
                        ps[pkey] = pvalue>=0.5
                    if dataType is int:
                        ps[pkey] = int(pvalue+0.5)
                    else:
                        ps[pkey] = dataType(pvalue)
                i+=1
            # Categorical
            else:
                # Find the category value with highest fire strenght...
                fireStrs = []
                while (vectorKeys[i][0]==pkey):
                    fireStrs.append( (parameterVector[i], vectorKeys[i][1]) )
                    i+=1
                fireStrs.sort()
                fireIdx = fireStrs[-1][1] 
                
                # And set is as 
                prange = parameterSetDefinition.GetParameterRange(pkey)
                ps[pkey] = prange[fireIdx]
        
        return ps
    
    def Tune(self, tunerParameterSet=None ):
        if not tunerParameterSet:
            tunerParameterSet = self.GetDefinition().NewDefaultParameterSet()
        
        # This overlaps with internal conditions of cma, but do not care.
        #  better to check twice than once. :)
        stopConditions = self._getStoppingTriplet(tunerParameterSet)
        
        
        
        # Translate InternalTuner parameters into cma format
        defaultBias = False
        cmaOpts =  {'bounds': [0.0, 1.0]}
        evaluationBudget = None
        
        for (k,v) in tunerParameterSet.items():
            # evaluation budget
            if (k=="-eb"):
                cmaOpts["maxfevals"]=v/len(self._training_instances)
                evaluationBudget = v
                
            # Required objective
            if (k=="-ro"):
                cmaOpts["ftarget"]=v
            
            # Seed of cma
            if (k=="-seed"):
                cmaOpts["seed"]=v
                
            # Default category bias
            if (k=="-dcb"):
                defaultBias=v
            
        # measure wall time
        tuningTimeStart = time.time()
        
        # Calculate # of algo evaluations
        evaluations = 0
        
        # Keep track of the best objective if needed
        bestObjective = MAX_FLOAT
            
        # The main tuning loop
        apsd = self._algorithm.GetDefinition()
        aps = apsd.NewDefaultParameterSet()
        
        dpsiValues, dpsiKeys, dpsiBounds = CMAESTuner.parameterSetToParameterVector(aps, apsd, defaultBias) 
        
        print dpsiValues, cmaOpts
        es = cma.CMAEvolutionStrategy(dpsiValues, 0.5, cmaOpts)

        # Quickfix / modify popsize to allow eval for 100e
        if (es.popsize*len(self._training_instances))>evaluationBudget:
            # Force at least 1 iteration
            cmaOpts["popsize"]=int(float(evaluationBudget)/len(self._training_instances))
            sys.stderr.write("Warning: force popsize to %d\n" % cmaOpts["popsize"])
            # Re-init
            es = cma.CMAEvolutionStrategy(dpsiValues, 0.5, cmaOpts)
            
            
        #logger = cma.CMADataLogger().register(es)
        # TODO: Convert to fmin()!!!
        while not es.stop():
            
            # 1. Sample iteration instances from all available instances

            sampledInstances = self._training_instances
            
            # TODO: Implement advanced sampling
            #if self._isFullEvaluationNeeded(stopConditions):
            #    
            #else:
            #    #  for example like it is done in GGA
            #    sampledInstances = [self._training_instances[random.randint(0, len(self._instances)-1)]]
            
            # 2. Evaluate ES sampled individuals for this instance
            
            X = es.ask()
            
            #for individual in X:
            #    logging.debug( str(individual)+"\n" )
            
            fit = [BaseTuner.calculateAlgorithmPerformance(
                self._algorithm,
                CMAESTuner.parameterVectorToParameterSet(individual, dpsiKeys, dpsiBounds, apsd), 
                sampledInstances)["obj"]\
                for individual in X]
            evaluations+=len(X)*len(sampledInstances)
        
            es.tell(X, fit)
            
            logging.debug( "Mean fit: " + str( sum(fit)/len(fit) ) )
            #logger.add()
            #es.disp()
            
            ## 3. Test if we are done 
            
            # In case the stop condition is objective limit, we keep track of the best objective 
            #  (we can take this from the fit-vector as we are doing full evaluation (all instances)
            #  each iteration.
            if self._isFullEvaluationNeeded(stopConditions):
                bestObjective = min(bestObjective, min(fit))
                                
            tuningTime = time.clock()-tuningTimeStart
            
            currentStatus = (tuningTime, evaluations, bestObjective)
            expected = (None, es.popsize*len(sampledInstances), None) #TODO: get expected time and improvement
            if self._isStopConditionFilled(stopConditions, expected, currentStatus):
                break
            
        
        tunedParameters = CMAESTuner.parameterVectorToParameterSet(es.result()[0], dpsiKeys, dpsiBounds, apsd)
        
        # Not needed if run over all instances, then objf in es.result()[1]
        BaseTuner.initFixedParameters(self._algorithm, tunedParameters)
        tunedObjective = BaseTuner.calculateAlgorithmPerformance(\
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
        

""" Code that test the basic operation of the CMAES Tuner """    
def main():
    
    from Algorithms.GFEAlgorithm import GFEAlgorithm
    algo = GFEAlgorithm(10, 1)
    
    # Convert 1 of the vars to be categorical
    x1ind = algo.GetDefinition()._switches["-x1"]
    algo.GetDefinition()._ranges[x1ind] = [0, 5, 10, 15]
    
    tuner = CMAESTuner()
    dps = tuner.GetDefinition().NewDefaultParameterSet()
    dps["-eb"]=1000.0
    
    tuner.SetAlgorithm(algo)
    tuner.SetInstances([PathManager.GetTuningBasePath()+"Benchmarks/gfe/f1_c/f1_c_1.spc",\
                        PathManager.GetTuningBasePath()+"Benchmarks/gfe/f1_c/f1_c_1.spc"])
    
    # Tune
    tuningResult = tuner.Tune(dps)
    print "Quality: " + str(tuningResult["obj"])
    print "Evaluations: " + str(tuningResult["ops"])
    print "Tuned parameters: " + str(tuningResult["special"])
    
if __name__ == '__main__':
    main()       
        
        
        

