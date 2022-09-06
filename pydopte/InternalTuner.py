import sys

from BaseTuner import BaseTuner
from ParameterSet import *


class InternalTuner(BaseTuner):
    """ This class offers functionality that makes implementing internal tuners to the PyDote 
    framework more straightforward. 
    """
    
    def __init__(self):
        """ Internal tuner constuctor 
        """
        BaseTuner.__init__(self)
        
        # Stopping condition parameters
        self._definition.Add("Timeout", "-t", 1.0, (0.0,MAX_FLOAT), False, False)
        self._definition.Add("Evaluation budget", "-eb", 0, (0,MAX_INT), False, False)
        self._definition.Add("Required objective", "-ro", 0.0, (0.0,MAX_FLOAT), False, False)
        
        self._definition.Add("Seed", "-seed", 0, (0,MAX_INT), False, False)
        
        # In derived class, here is the place for the 
        #_definition.Add("Verbosity", "-v", VERBOSE, (0,5), True, False)
        
    def _getStoppingTriplet(self, tunerParameterSet):
        
        budgetTime = None
        if ("-t" in tunerParameterSet):
            budgetTime = tunerParameterSet["-t"]
            
        budgetEvaluations = None
        if ("-eb" in tunerParameterSet):
            budgetEvaluations = tunerParameterSet["-eb"]
            
        requiredObjective = None
        if ("-ro" in tunerParameterSet):
            requiredObjective = tunerParameterSet["-ro"]
            
        if (not budgetTime) and \
           (not budgetEvaluations) and \
           (not requiredObjective):
            raise ValueError("Define stopping condition to tuner with any of these: '-eb <evaluation budget>', '-t <time budget>' or '-ro <required tolerance>'")
        
        return (budgetTime, budgetEvaluations, requiredObjective)

    def _isFullEvaluationNeeded(self, conditionTriplet):
        return conditionTriplet[2]!=None
    
    def _isStopConditionFilled(self, conditionTriplet, expectedTriplet, stateTriplet):
        """ If expected time/evaluations/improvement is given, try to get as close as possible
        note: expectedImprovement can be used to give tolerance.
        """
        
        #Unpack
        (elapsedTuningTime, elapsedEvaluations, bestObjective) = stateTriplet
        (budgetTime, budgetEvaluations, requiredObjective) = conditionTriplet
        (expectedTime, expectedEvaluations, expectedImprovement) = expectedTriplet
        
        # Test
        if budgetEvaluations:
            if expectedEvaluations!=None and \
                ( abs(budgetEvaluations - elapsedEvaluations) <
                abs(budgetEvaluations - (elapsedEvaluations+expectedEvaluations)) ):
                return True
            elif elapsedEvaluations >= budgetEvaluations:
                return True
                
        if budgetTime:
            if expectedTime!=None and \
                ( abs(budgetTime - elapsedTuningTime) <
                abs(budgetTime - (elapsedTuningTime+expectedTime)) ):
                return True
            elif (elapsedTuningTime > budgetTime):
                return True
                
        if requiredObjective:
            if expectedImprovement!=None and \
                ( abs(requiredObjective - bestObjective) <
                abs(requiredObjective - (bestObjective+expectedImprovement)) ):
                return True
            elif (bestObjective <= requiredObjective):            
                return True
        
        return False    
