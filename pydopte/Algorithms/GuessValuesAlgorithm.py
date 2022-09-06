# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 17:14:29 2011

@author: jussi
"""
import sys, os
from BaseAlgorithm import BaseAlgorithm, AlgorithmError

KNOWN_TYPES = {
    'int': int,
    'i': int,
    'float': float,
    'f': float,
    'bool': bool,
    'b': bool
}

class GuessValuesAlgorithm(BaseAlgorithm):
    def __init__(self, num_variables=1, variable_type=float):
        BaseAlgorithm.__init__(self)
        
        self._definition.Add("Instance", "-i", "", (), True, False)
        for i in range(num_variables):
            if variable_type == bool:
                var_range = (0,1)
                variable_default = 1
            else:
                var_range = (variable_type(0.0),variable_type(10.0))
                variable_default = (var_range[0]+var_range[1])/2
            self._definition.Add("Variable%02d"%i, "-x%02d"%i, variable_default, var_range, True, True)

        self._definition.Add("Number of variables", "-N", num_variables, (1,100), True, False)        
        self._definition.Add("variable type", "-T", variable_type.__name__, (), True, False)        
        
    def Evaluate(self, algoParamSet):
        num_variables = algoParamSet["-N"]
        variable_type = KNOWN_TYPES[algoParamSet["-T"]]
        
        # read the target from a file
        target = []
        with open(algoParamSet["-i"]) as targetfile:
            for line in targetfile.readlines():
                for e in line.split():
                    if variable_type == bool:
                        target.append( int(e) )
                    else:
                        target.append( variable_type(e) )
                    if len(target)==num_variables:
                        break
                if len(target)==num_variables:
                        break              

        # calcluate how close the guess hit
        f = 0        
        for i in range(num_variables):
            f+=abs(algoParamSet["-x%02d"%i]-target[i])
        return {"obj":f}
    
    def SetTimeLimit(self, timeout):
        pass # Evaluation is so fast that this makes no sense
    
    def GetScriptPath(self):
        return os.path.abspath( __file__ )
    
def main(argv):
    """ The main function if used as executable.
    """

    wrapperParameters = BaseAlgorithm.ParseWrapperParameters(argv)
    
    # Get -T and -N
    algo = GuessValuesAlgorithm() 
    cmdargs = BaseAlgorithm.ParseAlgorithmParameters(argv, algo.GetDefinition(), wrapperParameters["-ifmt"])
    
    # Parse again this time like you mean it
    algo = GuessValuesAlgorithm(num_variables=cmdargs["-N"], variable_type=KNOWN_TYPES[ cmdargs["-T"] ])
    cmdargs = BaseAlgorithm.ParseAlgorithmParameters(argv, algo.GetDefinition(), wrapperParameters["-ifmt"])
    
    try:
        result = algo.Evaluate(cmdargs)
        BaseAlgorithm.PrintOutput(result, wrapperParameters["-ofmt"])
    except AlgorithmError as we:
        print >> sys.stderr, str(we)
        sys.exit(1)

if __name__ == "__main__":
    #main(['-ofmt', '"obj:{obj} ; seed:{seed} ; operations={ops} ; elapsed time={time};"', '-v', '5.0', '-i', '6'])
    if len(sys.argv)==1 or (sys.argv[1] in ["-h", "-help", "--h", "--help"]):
        bare = GuessValuesAlgorithm()
        bare.PrintUsage()
    else:
        main(sys.argv[1:])
        
