# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 17:28:01 2011

@author: juherask
"""

import time
from os.path import basename
import operator
from heapq import *
from collections import deque

from ParameterSet import *
from InternalTuner import *
from Algorithms.GFEAlgorithm import *
import logging
import PathManager

# This many first parameter sets get points for scoring to top RANKING_MAX for
#  each problem instance.
RANKING_MAX = 10 

# Retry evaluation this many times until giving up
RETRIES = 3

DBG_PRODUCE_TRACE = False

#TODO: Add support for setting the seed

class RandomTuner(InternalTuner):
    """A tuner that has parameters defined in tunerParameterSetDefinition
    ( a ParameterSetDefinition class instance )"""
    def __init__(self):  
        InternalTuner.__init__(self)
        self._definition.Add("Ranking list size", "-rls", 10, (0,100), False, False)
       

    @staticmethod
    def _getBestParameterSet(objectives, candidateCache):
        totalPoints = {}
        for topAps in objectives:
            logging.debug(str(topAps))
            for points in range(len(topAps)):
                objf, apsId = heappop(topAps)
                if not apsId in totalPoints:
                    totalPoints[apsId] = 0
                totalPoints[apsId] += points
        
        sortedByPoints = [(v, k) for k, v in totalPoints.items()]
        sortedByPoints.sort()
        logging.debug("(total points, aps Id)" + str(sortedByPoints))
        
        idx = sortedByPoints[-1][1]
        return candidateCache[idx]
        

    def Tune(self, tunerParameterSet=None ):
        """ Tunes the given algorithm with random sampling of paramters
        instancelist is assumed to be list of instancefiles
        list of instancefiles
        """

        if not tunerParameterSet:
            tunerParameterSet = self.GetDefinition().NewDefaultParameterSet()
        
        if "-seed" in tunerParameterSet:
            random.seed( int( tunerParameterSet["-seed"] ) )
            
        ranking = RANKING_MAX
        if "-rls" in tunerParameterSet:
            ranking =  tunerParameterSet["-rls"]
        
        stopConditions = self._getStoppingTriplet(tunerParameterSet)
            
        # The main tuning loop
        instanceCount = len(self._training_instances)
        candidateCapacity = instanceCount*ranking+1
        iteration = 0
        evaluations = 0
        
        objectives = [list() for i in range(instanceCount)]
        candidates = [None]*candidateCapacity
        objectivePositions = [0]*candidateCapacity
        freeCandidateIds=deque(range(candidateCapacity))
        bestObjective = MAX_FLOAT
        bestCandidate = None
        
        tuningTimeStart = time.clock()

        if DBG_PRODUCE_TRACE:
            tracefile = open("%s_%s_trace.txt" % (self._algorithm.__class__.__name__, str(time.time())),'w')
	
        while True:

            # 1. Sample new parameter set values

            apsd =  self._algorithm.GetDefinition()
            aps = apsd.NewSampledParameterSet()
            
            if ranking>0:
                apsId = freeCandidateIds.pop()
                apsPositions = 0
                
            logging.debug("New random set #(%d)" % (iteration+1))
            
            # 2. Evaluate for all instances
            totobjf = 0
            for instanceId in range(instanceCount):
                instance = self._training_instances[instanceId]
                
                if apsd.HasParameter( "Instance" ):
                    isw = apsd.GetParameterSwitch("Instance")
                    aps[isw] = instance
                
                objf = self._algorithm.Evaluate(aps)["obj"]
                evaluations+=1
                totobjf+=objf
                
                # If ranking is used, update ranking lists
                if ranking>0:
                    heappush(objectives[instanceId], (-objf, apsId))
                    apsPositions+=1
                        
                    logging.debug("Pushed %s for instance %d with objective %f" % (str(aps), instanceId, objf))
                            
                    # Remove dropout aps                
                    if len(objectives[instanceId])>ranking:
                        (popObjf, popId) = heappop(objectives[instanceId])
                        
                        
                        if popId==apsId:
                            apsPositions-=1
                            
                            logging.debug( "Popped %s for instance %s with objective %f" % (str(aps), instanceId, -popObjf) )
                        else:
                            objectivePositions[popId]-=1
                            logging.debug( "Popped %s for %s with objective %f" % (str(candidates[popId]), instanceId, -popObjf) )
                            # If the popped does no longer hold any positions
                            #  it can be ignored
                            if objectivePositions[popId]==0:
                                candidates[popId]=None
                                freeCandidateIds.append(popId)
                                logging.debug( "Freed %d " % popId ) 
                
            # Keep track of the best so far
            if (totobjf<bestObjective):
                bestObjective=totobjf
                bestCandidate=aps

            #QUICKHACKCODE for getting a trace from random search
            if DBG_PRODUCE_TRACE:
                if apsd.HasParameter( "Instance" ):
                    isw = apsd.GetParameterSwitch("Instance")
                    aps[isw] = ""
                tracefile.write(str(aps)+";"+str(totobjf)+"\n")
            
            # If ranking is used, manage candidate IDs
            if ranking>0:  
                # If candidate managed to get top positions, keep it
                if apsPositions>0:             
                    candidates[apsId] = aps
                    objectivePositions[apsId] = apsPositions
                else:
                    freeCandidateIds.append(apsId)
                
                        
            # 3. Test if we are done 
                
            iteration+=1
            tuningTime = time.clock()-tuningTimeStart
            
            currentStatus = (tuningTime, evaluations, bestObjective)
            expected = (None, instanceCount, None) #TODO: get expected time and improvement
            if self._isStopConditionFilled(stopConditions, expected, currentStatus):
                break
         
        if DBG_PRODUCE_TRACE:
            tracefile.close()

        # 4. return best parameter set 
        
        logging.debug( str( list( zip(range(len(candidates)), candidates) )) )
            
        # If ranking is used, get best of ranked candidates
        if ranking>0:  
            tunedParameters = RandomTuner._getBestParameterSet(objectives, candidates)
        else:
            tunedParameters = bestCandidate
            
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
    #logging.basicConfig(level=logging.DEBUG)
    
    algo = GFEAlgorithm(10, 1)

    # Run random parameter tuner with defaults and with dummy algo
    tuner = RandomTuner()
    dps = tuner.GetDefinition().NewDefaultParameterSet()
    dps["-eb"]=1000
    dps["-rls"]=0
    
    tuner.SetAlgorithm(algo)
    #tuner.SetInstances([PathManager.GetTuningBasePath()+"Benchmarks/gfe/f1_c/f1_c_1.spc"])
    instances = []
    for i in range(14):
        instance = PathManager.GetTuningBasePath()+"Benchmarks/gfe/f1_c/f1_c_%d.txt" % (i+1)
        instances.append(instance)
    tuner.SetInstances(instances)
    
    # Tune
    tuningResult = tuner.Tune(dps)
    print str(tuningResult["obj"])
    #print "Quality: " + str(tuningResult["obj"])
    #print "Evaluations: " + str(tuningResult["ops"])
    #print "Tuned parameters: " + str(tuningResult["special"])
    
if __name__ == '__main__':
    main()         
        
        
        

