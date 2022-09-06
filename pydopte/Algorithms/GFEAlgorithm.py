# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 15:43:40 2011

@author: juherask
"""
import util
from ParameterSet import *
from BaseAlgorithm import *
import sys
import os

class GFEAlgorithm(BaseAlgorithm):
    @staticmethod
    def _eval(f, xl, pl):
        
        pc = len(pl)
        
        sum = 0.0
        if (f==1):
            for i in range(pc):
                sum += (xl[i*2]*xl[i*2+1]-pl[i])**2
        if (f==2):
            for i in range(pc):
                sum += (xl[i*3]*xl[i*3+1]*xl[i*3+2]-pl[i])**2
        if (f==3):
            for i in range(pc/2):
                sum += (xl[i*3]*xl[i*3+1]-pl[i])**2 + (xl[i*3]*xl[i*3+2]-pl[i])**2
        return sum       
    
    def __init__(self, constantCount, f):
        """ Set the dictionary containing the constants and the function type.
        Also generates the input parameter (variable) definition based 
        on given method parameters.
        """
        
        BaseAlgorithm.__init__(self)
        
        if ( f==3 and constantCount%2!=0 ): 
            raise ValueError("Function 3 needs even number of constants.")
        
        
        self._f = f
        self._cc = constantCount

        # Generate input parameter (variable) definition that
        #  matches to the one of the selected function        

        n = 0
        if f==1:
            n = constantCount*2
        elif f==2:
            n = constantCount*3
        elif f==3:
            n = constantCount/2*3
            
        # Need to give the instance
        self._definition.Add("Instance", "-i", "", (), True, False)
        
        # Add n tunable variables x1..xn with range (0,15)        
        for i in range(n):
            self._definition.Add("Variable_x"+str(i), "-x"+str(i), 7, (0,15), True, True)
    
    def SetTimeLimit(self, timeout):
        """ Used to set how long the algorithm is allowed to run on each 
        evaluation. """
        pass # Evaluation is so fast that this makes no sense
            
    
    def Evaluate(self, algoParamSet):
        # TODO: fill the algoParamSetSet with non tuned params (if necessary)
        #  Fill the non tuned variables it may
        
        if self._definition.__neq__(algoParamSet):
            logging.debug("Expected: " + str( [self._definition.AllParameterSwitches()] ) + " got: " +str(algoParamSet))
            raise ValueError("Parameter set does not have the right parameters.")
        
        constantFile = algoParamSet["-i"]
        
        cfile = open(constantFile, "r")
        clines = cfile.readlines()
        cfile.close()
        
        cs = dict()
        for line in clines:
            parts = util.split_ex(line, ["=", ";", ",", " "], skipEmpty=True)
            if parts[0][0] != "-":
                constantName = "-"+parts[0]
            else:
                constantName = parts[0]
            constantValue = float(parts[1])
            cs[constantName] = constantValue
        
        # Store the constant values in natural key order
        ck = cs.keys()
        util.natsort(ck) 
        self._pl = [cs[k] for k in ck]
        
        # Get the variables in natural key order
        ps = dict(algoParamSet)
        ps.pop("-i")
        dk = ps.keys()
        util.natsort(dk) 
        xl = [int(ps[k]) for k in dk]
        
        value = self._eval(self._f, xl, self._pl)
        return {"obj":value}
    
    def GetScriptPath(self):
        return os.path.abspath( __file__ )
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return BaseAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -f "+str(self._f)+" -cc "+str(self._cc)
        
def main(argv):
    """ The main function if used as executable.
    """

    wrapperParameters = BaseAlgorithm.ParseWrapperParameters(argv, ["-f", "-cc"])
    function = int(wrapperParameters["-f"])
    constantCount = int(wrapperParameters["-cc"])
    
    # Pretend to know the
    algo = GFEAlgorithm(constantCount, function) 
    cmdargs = BaseAlgorithm.ParseAlgorithmParameters(argv, algo.GetDefinition(), wrapperParameters["-ifmt"])
    
    try:
        result = algo.Evaluate(cmdargs)
        BaseAlgorithm.PrintOutput(result, wrapperParameters["-ofmt"])
    except AlgorithmError as we:
        print >> sys.stderr, str(we)
        sys.exit(1)

if __name__ == "__main__":
    #import logging
    #logging.basicConfig(level=logging.DEBUG)
        
    if len(sys.argv)==1 or (sys.argv[1] in ["-h", "-help", "--h", "--help"]):
        bare = GFEAlgorithm(0,0)
        bare.PrintUsage()
    else:
        main(sys.argv[1:])
