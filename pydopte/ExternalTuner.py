# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 15:07:41 2011

@author: jussi
"""

import shutil
import util
import os
import logging
from time import time, sleep

from ExternalAlgorithm import ExternalAlgorithm
from BaseTuner import BaseTuner
from ParameterSet import MAX_INT

CLEAN_UP_TEMP_FILES = True # True JUST TEST. SET TO TRUE.
TEMP_INSTANCES_FILE = "tuner_instances.txt"
TEMP_PARAMETERS_FILE = "algo_parameters.txt"

class ExternalTuner(ExternalAlgorithm, BaseTuner):
    """ This class offers functionality that makes wrapping external tuners to the PyDote 
    framework more straightforward. Just fill out the missing pieces in: 
    
    In constructor,
     * Introduce the (free) parameters of the tuner
     * Set the path to the executable via ExternalTuner ctor
    
    In createAlgorithmParametersFile override 
     * Write algorithm parameter definition into a format understood by the external tuner.
     
    In ParseExternalOutput override 
     * Handle external tuner output in a way that we can report the number of evaluations {"ops":N}
        and tuner parameters {"special":ParameterSetDict}. The "ops" is incremented.
     
    InCreateAlgorithmCommand
     * If the default implementation defined in ExternalAlgoirthm is not enough, override with
        specialized method.
        
    TEMP_INSTANCES_FILE
    TEMP_PARAMETERS_FILE
    
    """
    def __init__(self, cmd):
        """ External 
        """
        BaseTuner.__init__(self)
        ExternalAlgorithm.__init__(self, cmd)
        
        self._tid = "TT_%s_%s" % (self.__class__.__name__, str(time()) )
       
        # In derived class, here is the place for the 
        #_definition.Add("Verbosity", "-v", VERBOSE, (0,5), True, False)
    
        
    ### OVERRIDEABLE METHODS ###
        
    def createAlgorithmParametersFile(self, configurationFilename,
	                                  tunerParameters, algorithmParameterDefinition ):
        """ Writes algorithm parameter definition into a file that is
        understood by the external tuner.
        """
        raise NotImplementedError
    
    def getOutputLineRecognizer(self, key):
        """Definition of dictonary of regular expressions in derived class (or other
        objects implementig a obj.match(str) -iterface.
         
        They are used to recognize the rows where the final tuned parameters are 
        found ("special") and where a parameter set evaluation with tuned algorithm 
        was announced ("ops").
        """
        raise NotImplementedError
    
    
    ### DEFAULT IMPLEMENTATION METHODS ###
    
    def ParseExternalOutput(self, row, rowresult):
        """ Inherited from ExternalAlgorithm. Should fill the parameters
        to a "special" field, you might want to use convertStringToParameters(...).
        Count number of evaluations to "ops" field.
        
        This default implementation relies on definition of dictonary
         of regular expressions in derived class. They are used to 
         recognize the rows where the final tuned parameters are found ("special")
         and where a parameter set evaluation with tuned algorithm was announced
         ("ops").
         
         To convert the tuned parameter line to parameter set the static method 
         _convertToParameters is used. It should do the trick 99% of the time.
        """
        
        if self.getOutputLineRecognizer("special").match(row):
            apsd = self._algorithm.GetDefinition()
            tuned = ExternalTuner.convertStringToParameters(apsd, row)
            rowresult["special"] = tuned
        elif self.getOutputLineRecognizer("ops").match(row):
            if "ops" in rowresult:
                rowresult["ops"] += 1
            else:
                rowresult["ops"] = 1
            
        return rowresult
    
    @staticmethod
    def createAlgorithmInstancesFile(instancesFilename, instances, writeSeed=True ):
        """ The default implementation writes instance file in
        <seed> <instance>
        format (for each line) where the <seed> is seed (integer) and
        <instance> is the instance listed in instanceList.
        """
        instancesFile = open(instancesFilename,"w")
        for instance in instances:
            if isinstance(instance, str) or isinstance(instance, unicode):
                if writeSeed:
                    raise ValueError("Cannot write seed, because no seed is given!")
                else:
                    instancesFile.write(instance+"\n")
                    
            elif isinstance(instance[0], str) or isinstance(instance[0], unicode):
                if writeSeed:
                    instancesFile.write(str(instance[1])+" "+instance[0]+"\n")
                else:
                    instancesFile.write(instance[0]+"\n")
            else:
                if writeSeed:
                    instancesFile.write(str(instance[0])+" "+instance[1]+"\n")
                else:
                    instancesFile.write(instance[1]+"\n")
        instancesFile.close()
        
    
    
    def Tune(self, tunerParameterSet=None):
        """ Assumes that the instances is set into a (tuner) parameter
        that has the description "Instance" if the tuned algorithm 
        requires instances for the tuning.
        """
        
        if not self._algorithm:
            raise ValueError("No algorithm to tune")
        
        # Setup temp files and folder
        self.createAndSetTuningFolder()
        self.createAlgorithmParametersFile( TEMP_PARAMETERS_FILE, tunerParameterSet, self._algorithm.GetDefinition() )
        
        if isinstance(self._training_instances[0], str) or isinstance(self._training_instances[0], unicode):
            # Only instances are specified
            ExternalTuner.createAlgorithmInstancesFile( TEMP_INSTANCES_FILE, self._training_instances, False )
        else:
            # Seed and instance are specified
            ExternalTuner.createAlgorithmInstancesFile( TEMP_INSTANCES_FILE, self._training_instances, True )       
        
        tuningResult = self.Evaluate(tunerParameterSet)
        
        BaseTuner.initFixedParameters(self._algorithm, tuningResult["special"])
        tuningResult["obj"] = self.calculateAlgorithmPerformance(\
            self._algorithm,\
            tuningResult["special"],\
            self._validation_instances )["obj"]
        
        # Delete temp files and folder
        if CLEAN_UP_TEMP_FILES:
            self.cleanUpTuningFolder()
            
        return tuningResult
        
    ### HELPER FUNCTIONS ###
    
    def createAndSetTuningFolder(self):
        """Almost all external tuners litter the current folder with all kind of
        temp files. Changing the working folder makes it sure parallel tuning tasks do 
        not mess each other."""
    
        cwdpath = os.path.abspath(os.getcwd())
        cwddir = os.path.basename(cwdpath)
                
        if cwddir!=self._tid:
            newd = os.path.join(cwdpath, self._tid)
            
            if not os.path.exists(newd):
                classlogger = logging.getLogger(self.__class__.__name__)
                classlogger.debug( "Creating tuning folder:" + newd )

                os.makedirs(newd)
            os.chdir( newd )
        
    def cleanUpTuningFolder(self):
        cwdpath = os.path.abspath(os.getcwd())
        cwddir = os.path.basename(cwdpath)
        if cwddir==self._tid:
            os.chdir( os.path.dirname(cwdpath) )
            shutil.rmtree(cwdpath)
        
    @staticmethod
    def convertStringToParameters(parameterDefinition, rawParameterString):
        """ Finds those paramters, or "-switch value" pairs 
        (example: "-r 0.1") and if the switch is matched to the
        algorithm definition, adds it into the resulting parameter
        set. The fixed parameters are added if missing from the raw string.
        """
        parameterSet = dict()
        apsd = parameterDefinition
        rawParameters = util.split_ex(rawParameterString, ["=", ";", ":", ",", " ", "\t"], skipEmpty=True)
        
        for fsw in apsd.FixedParameters():
            parameterSet[fsw] = apsd.GetParameterDefault(fsw) 
        
        for i in range(len(rawParameters)):
            
            if i<(len(rawParameters)-1):
                sw = (rawParameters[i]).strip()
                val = (rawParameters[i+1]).strip()
                
                if apsd.HasParameter( "-"+sw ):
                    sw = "-"+sw
                
                if apsd.HasParameter(sw):
                    valtype = apsd.GetParameterType(sw)
                    if valtype in (int, float, long):
                        val = val.strip("'\"")
                    parameterSet[sw] = valtype( val )
                    
        return parameterSet  
        
    
        