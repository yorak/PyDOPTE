'''
Created on Aug 17, 2011

@author: jussi
'''

from BaseAlgorithm import BaseAlgorithm
from datetime import datetime
from ParameterSet import MAX_FLOAT, MAX_INT
import subprocess
import os
import sys
import logging
import time

class ExternalAlgorithm(BaseAlgorithm):
    '''
    Abstract base class for all algorithms that rely on external executable.
     See Evaluate and WrapperParameters and IsFinalParameterRow to see how 
     it saves you some coding.
    '''

    def __init__(self, cmd):
        BaseAlgorithm.__init__(self)
        self._cmd = cmd
    
    def WrapperParameterTranslator(self, param, value):
        """ Translates parameters as needed. If empty pair
        ,that is a (), is returned the parameter is skipped.
        """
        return (param,value)
    
    def ParseExternalOutput(self, row, rowresult):
        """ Returns a dictionary containing values (for a list of possible values, 
        see BaseAlgorithm.EVALUATE_OUTPUT_VALUES). 
        Current dictionary of values is given as output. More than
        one value can also be returned/modified.
        """ 
        raise NotImplementedError("Override in derived class.")
        # Example:
        # if "final parameters" in row:
        #   return {"objf":123.45}
        # else
        #   return rowresult
    

    def CreateAlgorithmCommand(self, algoParamSet):
        # Treat instance switch separately to guarantee that it is first (if defined)
        isw = None
        isv = None
        
        if self.GetDefinition().HasParameter("Instance"):  
            isw = self.GetDefinition().GetParameterSwitch("Instance")
        
        cmdargs = list()
        for k, v in algoParamSet.items():
            pkpv = self.WrapperParameterTranslator(k.strip(), v)
            if len(pkpv) == 2:
                if pkpv[0] == isw:
                    isv = str(pkpv[1])
                else:
                    cmdargs.append(pkpv[0])
                    cmdargs.append(str(pkpv[1]))
        
        if isv:
            fullcmd = "%s %s %s %s" % (self._cmd, isw, isv, " ".join(cmdargs))
        else:
            fullcmd = "%s %s" % (self._cmd, " ".join(cmdargs))
        return fullcmd

    def Evaluate(self, algoParamSet=None):
        
        if not algoParamSet:
            algoParamSet = self.GetDefinition().NewDefaultParameterSet()

        logging.info( "Evaluating: " + self.__class__.__name__ + \
                       " with parameters " + str(algoParamSet) )
        
        if self.GetDefinition().__neq__(algoParamSet):
            raise ValueError("Parameter set does not have the right parameters.")
        
        fullcmd = self.CreateAlgorithmCommand(algoParamSet)
        
        classlogger = logging.getLogger(self.__class__.__name__)
        #classlogger.debug( "Working directory is:" + os.getcwd() )
        #classlogger.debug( "Contains is:" + os.getcwd() )
        #for tempfile in os.listdir(os.getcwd()):
        #    classlogger.debug( "    " + tempfile )
        classlogger.debug( "Running command:" + fullcmd )
        
        # measure wall time
        start_wall = time.clock()
        # measure child process time
        start_times = os.times()
        
        proc = subprocess.Popen(fullcmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
     
                
        # Read line by line to discard the excessive logging
        result = {}
        while True:
            next_line = proc.stdout.readline()
            if next_line == "" and proc.poll() != None:
                break

            classlogger.debug( "Command stdout/stderr output: "+next_line )
            
            # This will hopefully fill in "obj" and possibly others to
            #  the result
            result = self.ParseExternalOutput(next_line, result) 
        
        wall_elapsed = time.clock()-start_wall
        end_times = os.times()
        cpu_elapsed = (end_times[2]+end_times[3])-(start_times[2]+start_times[3])
        
        if (proc.returncode!=0):
            raise WrapperError("Command: " + fullcmd + " Failed (enable logging to see the problem)")
        
        # Set the processing time (if not set by the ParseExternalOutput)
        if not "time" in result.keys():
            result["time"] = cpu_elapsed
        result["wtime"] = wall_elapsed
            
        # Set the seed used (if not set by the ParseExternalOutput)
        if self.GetDefinition().HasParameter("Seed"):
            seedsw = self.GetDefinition().GetParameterSwitch("Seed")
            if not "seed" in result.keys() and seedsw in algoParamSet.keys():
                result["seed"] = algoParamSet[seedsw]
        
        return result
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return BaseAlgorithm.GetCmd(self, outputFormat, inputFormat)+' -cmd "'+self._cmd+'" '

class WrapperError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
  
        