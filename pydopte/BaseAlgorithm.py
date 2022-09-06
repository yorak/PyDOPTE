# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 11:57:18 2011

@author: juherask
"""

from ParameterSet import ParameterSetDefinition
import sys
import os
import re

# NOTE: Has to be regexp friendly
OPENING_FORMAT_VARIABLE_CHAR = "{"
CLOSING_FORMAT_VARIABLE_CHAR = "}"
reFmtVar = re.compile(".*?"+OPENING_FORMAT_VARIABLE_CHAR+"(.*?)"+CLOSING_FORMAT_VARIABLE_CHAR)
def toFmtVar(var):
    return OPENING_FORMAT_VARIABLE_CHAR+str(var)+CLOSING_FORMAT_VARIABLE_CHAR
    

class BaseAlgorithm():
    
    """
    Algorithms can provide following outputs:
     
    obj  = objective function value
    seed = the seed that was used in evaluation
             (can be 0, if deterministic algorithm)
    ops  = operations made (iterations, steps etc.)
    time = runtime of the algorithm,
    [wtime = wall time elapsed while running the algorithm]
    """
    EVALUATE_OUTPUT_VALUES = ["obj", "seed", "ops", "time", "special"]
    EVALUATE_DEFAULT_VALUES = {"obj":0.0, "seed":-1, "ops":0, "time":0.0, "special":"N/A"}

    
    def __init__(self):
        """
        NOTE: Add the algorithm specific parameters tn derived classes
        
        All algorithms should have parameters with definition:
        "Instance" = the instance file or instance definition to run the algo on
        "Timeout" = to define algorithm cutoff
        """
        self._definition = ParameterSetDefinition()
    
    def SetTimeLimit(self, timeout):
        """
        Used to set how long the algorithm is allowed to run on each 
        evaluation.
        """
        self._definition.SetParameterFixed("Timeout")
        self._definition.SetParameterDefault("Timeout", float(timeout))

    def GetDefinition(self):
        """
        Get the parameter set definition for the variables the algorithm 
        needs to do the evaluation. A set of parameter sets complying to
        this expected by the Evaluate.
        """
        return self._definition
        
    def Evaluate(self, algoParamSet=None):
        """
        Given the set of parameter set to evaluate the algorithm on.
        A dictionary containining result is returned. (that is at least  
        some of values EVALUATE_OUTPUT_VALUES). 
        """
        raise NotImplementedError("Override in derived class.")
    
    def GetScriptPath(self):
        """
        Call os.path.abspath( __file__ ) in the script file that will
        be executed when using the command line interface of the 
        Algorithm.
        """ 
        raise NotImplementedError("Override in derived class.")
        return os.path.abspath( __file__ )
    
    @staticmethod
    def PrintOutput(result, outputFormat):
        """
        Used to convert result dictionary ( some of EVALUATE_OUTPUT_VALUES as keys )
        to a output string of given format. Example:
        result = {"obj":123.4, "seed":42}, outputFormat = "OF={obj}, SD={seed}"
        results to string "OF=123.4, SD=42" being returned.
        
        Useful when for example external tuner requires specific output from 
        a algorithm.
        """
        
        
        
        if not outputFormat:
            outputFormat = "{obj}"
        
        outputString = outputFormat
        if len(outputString)>0:
            
            fmtvars = reFmtVar.findall(outputFormat)
            
            for fmt in fmtvars:
                varval = "0"
                
                if fmt=="":
                    pass
                elif fmt in result.keys():
                    varval = result[fmt]
                elif fmt in BaseAlgorithm.EVALUATE_OUTPUT_VALUES:
                    varval = BaseAlgorithm.EVALUATE_DEFAULT_VALUES[fmt]
                else:
                    raise LookupError("Unrecognized output format key %s" % fmt)
                
                outputString = outputString.replace( toFmtVar(fmt), str(varval) )
        print outputString
    
    @staticmethod 
    def ParseWrapperParameters(argv, wrapperParameters=[]):
        """ Gets the input and output formatting from the command line switches """
        i = 0
        wp = {}
        while i < len(argv):
            k = argv[i].strip()
            if k=="-ofmt" or k=="-ifmt" or  k in wrapperParameters:
                wp[k] = argv[i+1].strip(' "')
            i+=1
                
        if not "-ofmt" in wp:
            wp["-ofmt"] = None
        if not "-ifmt" in wp:
            wp["-ifmt"] = None
             
        return wp
        
    @staticmethod 
    def ParseAlgorithmParameters(argv, algorithmParameterDescription, inputFormat):
        """
        Used to convert argument list (not including the executable/script name)
        into parameter list format. Note that this method does not check if the 
        command line arguments are right. This is usually done in Evaluate()-method
        where the right amount of right typed parameters is crucial.
        
        The flag parameters are converted to parameters with value "1".
        Example:
        argv=["-give", "-it", "2", "-me"] -> {"-give":"1", "-it":"2", "-me":"1"}
        
        If inputSwitchList is given it will specify the flags used for the 
        values that do not have a switch. If the slot in inputSwitchList is None,
        the value is skipped.
        Example:
        argv=["4" "-mee" "too" 2] inputFormat="{Give Description} {}"-> {"-give":"4", "-mee":"too"}
        """
        
        inputSwitchList = []
        if inputFormat:
            fmtvars = reFmtVar.findall(inputFormat)
            for fmt in fmtvars:
                sw = None
                if fmt!="":
                    sw = algorithmParameterDescription.GetParameterSwitch(fmt)
                inputSwitchList.append(sw)
            
        i = 0
        islp = 0
        argc = len(argv)
        islc = len(inputSwitchList)
        cmdargs = {}
        
        while i < argc:
            k = argv[i].strip()
            
            # Normal parameter
            if len(k)>1 and k[0]=="-":
                v = None
                if i+1<argc:
                    v = argv[i+1].strip('" ')
                
                # Check if flag
                if not v or v[0]=="-":
                    if k in algorithmParameterDescription.keys():
                        cmdargs[k]=1
                # Parameter with value
                else:
                    if k in algorithmParameterDescription.keys():
                        paramType = algorithmParameterDescription.GetParameterType(k)
                        cmdargs[k] = paramType(v)  
                    i+=1
            # Inputformat defined parameter
            elif (islp<islc) :
                if inputSwitchList[islp]:
                    sw = inputSwitchList[islp]
                    paramType = algorithmParameterDescription.GetParameterType(sw)
                    cmdargs[sw] = paramType(k.strip('" '))
                islp+=1 
            i+=1
        
        return cmdargs
                
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        """ You should also implement a command line interface to the algorithm.
        External tuners use this to interface with the tuner instead of calling
        Evaluate.
        
        With the optional output -parameter the output of the command line
        can be defined. EVALUATE_OUTPUT_VALUESLUES for the keywords that are supported
        (remember to surround with "{}"). Output keywords can be combined as
        needed.
        
        Example: 
        output="{time}\t{obj}\t{ops}" prints out a tab delimeted list of 
         of runtime, objective and number of iterations.
        
        With the optional input -parameter a predefined set of command line
        switches for command line parameters without switches can be defined.
        This is useful for example when the calling format of external tuner
        cannot be changed.
        
        Example:
        input="{Instance} {} {} {} {Seed}" defines that first command line parameter without
        switch is set to be the value of the switch that has description "Instance" 
        (usually "-i"), the second value of the switch that has description "Seed"
         and two next ones are ignored.  
        """
        cmd = "python "+self.GetScriptPath()
        if inputFormat:
            cmd +=' -ifmt "%s"'%inputFormat 
        if outputFormat:
            cmd +=' -ofmt "%s"'%outputFormat
        
        return cmd
               
    def PrintUsage(self):
        cmd = "usage: python algo.py "
        for param in self._definition.FixedParameters():
            cmd+=param+" "+str(self._definition.GetParameterRange(param))+" "
        cmd + "[options]"
        print >> sys.stderr, cmd
        print >> sys.stderr, "Required:"
        for param in self._definition.FixedParameters():
            self.PrintParameterLine(param)
        print >> sys.stderr, "Optional:"
        for param in self._definition.AllParameterSwitches():
            if not param in self._definition.FixedParameters():
                self.PrintParameterLine(param)
                
    def PrintParameterLine(self, param):
        valdefault = self._definition.GetParameterDefault(param)
        valtype = str(type(valdefault)).replace("type '", "").replace("'", "")
        description = self._definition.GetParameterDescription(param)
        print >> sys.stderr, param+" " +valtype+" "+description+" (default value "+str(valdefault)+")"
        
        
class AlgorithmError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

         
