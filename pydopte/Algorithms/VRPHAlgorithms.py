#! /usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 11:04:52 2011

@author: juherask
"""
from ExternalAlgorithm import ExternalAlgorithm, WrapperError
from BaseAlgorithm import BaseAlgorithm
from ParameterSet import MAX_FLOAT, MAX_INT
import util
import os
import sys


class VRPHAlgorithm(ExternalAlgorithm):
    """ The parent class for all VRPH algorithms, as they share numerous
    parameters.
    """

    def __init__(self, cmd):
        self.VRPH_MAX_NUM_LAMBDAS = 100
        
        ExternalAlgorithm.__init__(self, cmd)
        
        # Special parameters that are expected to be in every Solver
        self._definition.Add("Instance", "-f", "", (), True, False) # Input File
        self._definition.Add("Timeout", "-cutoff", 5.0, (0.0,MAX_FLOAT), True, False) # Timebudget for the algo
        self._definition.Add("Seed", "-s", 0, (0.0,MAX_INT), False, False) # Seed 
        self._definition.Add("Randomize", "-r", 1, (0,1), True, False) # Randomization enabled 
        
        # Local set heuristics. Slightly modified flags for the wrapper.
        self._definition.Add("Enable ONE_POINT_MOVE", "-h_1pm", 1, (0,1), False, True)
        self._definition.Add("Enable TWO_POINT_MOVE", "-h_2pm", 1, (0,1), False, True)
        self._definition.Add("Enable TWO_OPT", "-h_two", 1, (0,1), False, True)
        self._definition.Add("Enable OR_OPT", "-h_oro", 0, (0,1), False, True)
        self._definition.Add("Enable THREE_OPT", "-h_tho", 0, (0,1), False, True)
        # NOTE: WARNING: Disabled CROSS because it caused "Error in route hash" error
        #self._definition.Add("Enable CROSS_EXCHANGE", "-h_cre", 0, (0,1), False, True)
        self._definition.Add("Enable THREE_POINT_MOVE", "-h_3pm", 0, (0,1), False, True)

		# If not set, use the default of 3 predefined lambdas. If is set to 3,
		#  use 3 random lambdas (We do not usually want to tune the CW+RTR).
        self._definition.Add("# of initial solutions", "-l", 3, (1,self.VRPH_MAX_NUM_LAMBDAS), False, False) 
        
        # Omitted parameters
        # -help prints this help message
        # -sol <solfile> begins with an existing solution contained in solfile.
        # -v prints verbose output to stdout
        # -o/-out <out_file> writes the solution to the provided file
        # -plot <plot_file> plots the best solution to the provided file
      
    def SetTimeLimit(self, timeout):
        self._definition.SetParameterDefault("-cutoff", float(timeout))

    def WrapperParameterTranslator(self, param, value):
        if param=="-mh" or param=="-cmd":
            return ()
            
        # -r for randomize is handeled as switch ("1" is omitted)
        elif "-r" in param:
            if (util.str2bool(str(value))):
                return ("-r", "1")
            else:
                return()
                
        elif "-h_" in param:
            if (util.str2bool(str(value))):
                if param=="-h_1pm":
                    return ("-h", "ONE_POINT_MOVE")
                elif param=="-h_2pm":
                    return ("-h", "TWO_POINT_MOVE") 
                elif param=="-h_two":
                    return ("-h", "TWO_OPT") 
                elif param=="-h_oro":
                    return ("-h", "OR_OPT") 
                elif param=="-h_tho":
                    return ("-h", "THREE_OPT") 
                elif param=="-h_cre":
                    return ("-h", "CROSS_EXCHANGE") 
                elif param=="-h_3pm":
                    return ("-h", "THREE_POINT_MOVE")
            else: 
                return ()
        else:
            return (param,value)
    
    def ParseExternalOutput(self, row, rowresult):
        """ Parse row with the form:
        '5', '524.611', '2.53', ['1.000']
        Where the 2nd field is the objective function value.
        """
        
        parts = row.split()
        if len(parts)==3 or len(parts)==4:
            try:
                stats = [float(p) for p in parts]
                return {"obj": stats[1], "time": stats[2]}
                    
            except:
                pass
        #Not a output line
        return rowresult
    
    def GetScriptPath(self):
        return os.path.abspath( __file__ )
        
    
class VRPH_SA_Algorithm(VRPHAlgorithm):
    
    def __init__(self, path):
        MAX_ITERATIONS = 10
        MAX_STEPS = 1000
        MAX_TEMP = 10.0
        MAX_NEIGHBOURHOOD_SIZE = 100
    
        path = os.path.normpath(path) + os.sep
        
        VRPHAlgorithm.__init__(self, path+"vrp_sa")
        
        self._definition.Add("Starting temp.", "-t", 2.0, (0.0,MAX_TEMP), False, True)
        self._definition.Add("Cooling steps", "-n", 200, (0,MAX_STEPS), False, True)
        self._definition.Add("Iterations/temp.", "-i", 2, (0,MAX_ITERATIONS), False, True)
        # range p.114 "Local Search in Combinatorial Optimization" eds. Aarts abnd Lenstra
        self._definition.Add("Cooling rate", "-c", 0.99, (0.8,1.0), False, True) 
        self._definition.Add("Neighbour list size", "-nn", 10, (1,MAX_NEIGHBOURHOOD_SIZE), False, True)
        
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return VRPHAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -mh sa"
        

class VRPH_RTR_Algorithm(VRPHAlgorithm):
    
    def __init__(self, path):
        MAX_IMPROVEMENT_TRIES = 100
        MAX_NEIGHBOURHOOD_SIZE = 75 # From source
        MAX_VRPH_TABU_LIST_SIZE = 50
        MAX_PERTUBATIONS = 10
        
        path = os.path.normpath(path) + os.sep
        
        VRPHAlgorithm.__init__(self, path+"vrp_rtr")
         
        self._definition.Add("Accept type (0=first, 1=best)", "-a", 1, (0,1), False, True)
        self._definition.Add("Search deviation", "-d", 0.01, (0.0,0.1), False, True)
        self._definition.Add("Search intensity", "-k", 30, (1,100), False, True)
        self._definition.Add("Tries to beat local minima", "-m", 5, (1,MAX_IMPROVEMENT_TRIES), False, True)
        self._definition.Add("Neighbour list size (0=disabled)", "-N", 4, (0,MAX_NEIGHBOURHOOD_SIZE), False, True)
        self._definition.Add("Perturbations per solution", "-P", 1, (1,MAX_PERTUBATIONS), False, True)
        self._definition.Add("Perturbation type (0=Li, 1=Osman)", "-p", 1, (0,1), False, True)
        self._definition.Add("Tabu Search list size (0=disabled)", "-t", 0, (0,MAX_VRPH_TABU_LIST_SIZE), False, True)
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return VRPHAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -mh rtr"
    
class VRPH_EJ_Algorithm(VRPHAlgorithm):
    
    def __init__(self, path):
        MAX_NUM_EJECTED = 45 # Limited by hard coded value (50) in the vrp_ej
        MAX_NUM_TRIALS = 10000
        
        path = os.path.normpath(path) + os.sep
        
        VRPHAlgorithm.__init__(self, path+"vrp_ej")
         
        self._definition.Add("Ejection count", "-j", 10, (1,MAX_NUM_EJECTED), True, True)
        self._definition.Add("Iterations", "-t", 1000, (0,MAX_NUM_TRIALS), True, True)
        self._definition.Add("Search method (0=rnd, 1=regret)", "-m", 0, (0,1), True, True)

    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return VRPHAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -mh ej"
    
def main(argv):
    wrapperParameters = BaseAlgorithm.ParseWrapperParameters(argv, ["-mh", "-cmd"])
    mh = wrapperParameters["-mh"]
    path = os.path.dirname(wrapperParameters["-cmd"])
    
    if (mh=='ej'):
        algo = VRPH_EJ_Algorithm(path)
    if (mh=='rtr'):
        algo = VRPH_RTR_Algorithm(path)
    if (mh=='sa'):
        algo = VRPH_SA_Algorithm(path)
        
    cmdargs = BaseAlgorithm.ParseAlgorithmParameters(argv, algo.GetDefinition(), wrapperParameters["-ifmt"])
    #print cmdargs
    try:
        result = algo.Evaluate(cmdargs)
        BaseAlgorithm.PrintOutput(result, wrapperParameters["-ofmt"])
    except WrapperError as we:
        print >> sys.stderr, str(we)
        sys.exit(1)

if __name__ == "__main__":   
    if len(sys.argv)==1 or (sys.argv[1] in ["-h", "-help", "--h", "--help"]):
        bare = VRPHAlgorithm("")
        bare.PrintUsage()
    else:
        main(sys.argv[1:])
           
