# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 17:28:01 2011

@author: juherask
"""

from BaseAlgorithm import BaseAlgorithm
from ParameterSet import ParameterSetDefinition, MAX_FLOAT
import sys

class BaseTuner(BaseAlgorithm):
    """ Basetuner is the base class for all the tuners. See how the Tuner itself
    is considered just another algorithm. This makes it possible to stack tuners
    if needed.
    """

    def __init__(self):
        """Initialize the tuner. You should give the algorithm and the instances
        (usually a list of files, or list of tuples where first is seed, second
        is the instance file) to tune the algorithm on.
        
        A tuner that has parameters defined in tunerParameterSetDefinition
        ( a ParameterSetDefinition class instance ). If possible tuners should have
        parameters with descriptions of "Seed", "Timeout", "Evaluation budget" and
        "Required objective" to set the respective parameters (altough this is not
        strictly necessary). 
        """
        BaseAlgorithm.__init__(self)
        
    def SetAlgorithm(self, algorithm):
        self._algorithm = algorithm
    
    def SetInstances(self, training_instances, validation_instances=None):
        """ If validation instances are not given, training instances are
        used as validation instances.
        """
        self._training_instances = training_instances
        self._validation_instances = training_instances
        if (validation_instances!=None):
            self._validation_instances = validation_instances
        
        #DEBUG CODE. PLEASE REMOVE before COMMIT
        print "Tuning set:"
        for i in self._training_instances:
            print i
        print "Validation set:"
        for i in self._validation_instances:
            print i
        print
          
    def Tune(self, tunerParameterSet=None):
        """Tunes algorithms that has method Evaluate(parameterSet). The algorithm is set in ctor.
        The tunerParameterSet is a dictionary matching the Tuners ParameterSetDefinition.
        
        As other algorithms returns a dictionary of result values. These include
         "obj", "time", "ops", where ops=operations=algorithm evaluations.
         
        The tuned parameters (dictionary) are returned in special field "special".
        """
        raise NotImplemented("Implement in derived class")
    
    def Evaluate(self, algoParamSet=None):
        """ Tuners are just another algorithm. Use Tune(...) interface to act as one.
        """
        return self.Tune(self, algoParamSet)
        
    
    ## HELPER FUNCTIONS ##
    
    @staticmethod
    def initFixedParameters(forAlgorithm, inThisParameterSet):
        ad = forAlgorithm.GetDefinition()
        for fp in ad.FixedParameters():
            if not fp in inThisParameterSet:
                inThisParameterSet[fp] = ad.GetParameterDefault(fp)
        
    
    @staticmethod
    def setInstanceParameters(instance, forAlgorithm, inThisParameterSet):
        ad = forAlgorithm.GetDefinition()
        
        aisw = None
        assw = None
        if ad.HasParameter("Instance"):
            aisw = ad.GetParameterSwitch("Instance")
        if ad.HasParameter("Seed"):
            assw = ad.GetParameterSwitch("Seed")
        
        iterable = getattr(instance, '__iter__', False)
        if not iterable or isinstance(instance, str) or isinstance(instance, unicode):
            if (aisw):
                inThisParameterSet[aisw]=instance;
        elif isinstance(instance[0], str) or isinstance(instance[0], unicode):
            if (aisw):
                inThisParameterSet[aisw]=instance[0];
            if (assw):
                inThisParameterSet[assw]=instance[1];
        else:
            if (aisw):
                inThisParameterSet[aisw]=instance[1];
            if (assw):
                inThisParameterSet[assw]=instance[0];
    
    @staticmethod
    def calculateAlgorithmPerformance(forAlgorithm, withThisParameterSet, onInstances):
        """ Calculates the algorithm performance on given paramter set
        """
        
        if onInstances and len(onInstances)>0:
            parameterSet = dict( withThisParameterSet.items() )
        
            sumd = dict()
            for instance in onInstances:
                BaseTuner.setInstanceParameters(instance, forAlgorithm, parameterSet)
                
                try:
                    ev = forAlgorithm.Evaluate(parameterSet) 
                    for k in ev.keys():
                        if not k in sumd.keys():
                            sumd[k] = 0.0
                        sumd[k]+=ev[k]
                except Exception as e:
                    # TODO: Handle this in some other way, In perfect world this should not happen.
                    sys.stderr.write('Warning: Evaluation of candidate parameter set failed. Reason "%s"\n' % str(e))
                    return {"obj":MAX_FLOAT}
            return sumd
        else:
            # No instance file
            return forAlgorithm.Evaluate( withThisParameterSet )

        
class TunerError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
   
    
    