#! /usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 11:04:52 2011

@author: juherask
"""
from ExternalAlgorithm import ExternalAlgorithm, WrapperError
from BaseAlgorithm import BaseAlgorithm
from ParameterSet import MAX_FLOAT, MAX_INT
import os
import sys


class VRPSDAlgorithm(ExternalAlgorithm):
    """ The parent class for all VRPSD algorithms, as they share numerous
    parameters.
    """

    def __init__(self, cmd):
        ExternalAlgorithm.__init__(self, cmd)

        # Special parameters that are expected to be in every Solver
        self._definition.Add("Instance", "-i", "", (), True, False) # Input File
        self._definition.Add("Seed", "-s", 0, (0,MAX_INT), False, False) # Random seed for a stochastic algo
        self._definition.Add("Timeout", "-t", 5.0, (0.0,MAX_FLOAT), True, False) # Timebudget for the algo
        
        # Parameters that define the solver behaviour, but are not typically tuned
        self._definition.Add("Number of tries", "-n", 1, (0,MAX_INT), True, False)
        #self._definition.Add("VehicleCapacity", "-q", 0, (0,MAX_INT), False, False) # Not used
        
        # Objective function evaluation parameters
        self._definition.Add("Use proxy evaluation", "-p", 0, (0, 1), False, True )
        self._definition.Add("Use TSP evaluation", "-u", 0, (0, 1), False, True )
        
        # Special paramter for selecting the VRPSD variant to use (used by the cmdline interface)
        #self._definition.Add("VRPSD metaheuristic", "-mh", None, ("acs", "ea", "fr", "ils", "sa", "ts"), True, False )
    
    def SetTimeLimit(self, timeout):
        """ Used to set how long the algorithm is allowed to run on each 
        evaluation. """
        self._definition.SetParameterDefault("-t", float(timeout))
        
    def ParseExternalOutput(self, row, rowresult):
        if "final" in row:
            parts = row.split()
            try:
                return {"obj": float( parts[1] ), "time": float( parts[3] )}
            except:
                pass
        #Not a output line
        return rowresult
    
    def GetScriptPath(self):
        return os.path.abspath( __file__ )
    
        
class VRPSD_ACS_Algorithm(VRPSDAlgorithm):
    
    def __init__(self, path):
        path = os.path.normpath(path) + os.sep
        
        VRPSDAlgorithm.__init__(self, path+"vrpsd.acs")
        
        self._definition.Add("Colony size", "-colonysize", 7, (1,100), False, True);
        self._definition.Add("tau0", "-tau0", 0.5, (0.0,1.0), False, True);
        self._definition.Add("rho", "-rho", 0.1, (0.0,1.0), False, True);
        self._definition.Add("psi", "-psi", 0.3, (0.0,1.0), False, True);
        self._definition.Add("Q", "-Q", 10000000.0, (10.0,10000000.0), False, True);
        self._definition.Add("alpha", "-alpha", 1.0, (0.0,5.0), False, True);
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return VRPSDAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -mh acs"
    
    
class VRPSD_EA_Algorithm(VRPSDAlgorithm):
    
    def __init__(self, path):
        path = os.path.normpath(path) + os.sep
        
        VRPSDAlgorithm.__init__(self, path+"vrpsd.ea")

        self._definition.Add("Population size", "-popSize", 10, (1,1000), False, True);
        self._definition.Add("Mutation rate", "-mr", 0.2, (0.0,1.0), False, True);
        self._definition.Add("Adaptive mutation rate", "-isadaptive", 0, (0,1), False, True);
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return ExternalAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -mh ea"

class VRPSD_FR_Algorithm(VRPSDAlgorithm):
    
    def __init__(self, path):
        path = os.path.normpath(path) + os.sep
        VRPSDAlgorithm.__init__(self, path+"vrpsd.fr")
    
        #self._definition.Add("Number of iterations", "-I", 1, (0,MAX_INT), False, True);
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return VRPSDAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -mh fr"

class VRPSD_ILS_Algorithm(VRPSDAlgorithm):
    
    def __init__(self, path):
        path = os.path.normpath(path) + os.sep
        
        VRPSDAlgorithm.__init__(self, path+"vrpsd.ils")
 
        self._definition.Add("Terminate try -factor x", "-I", 10.0, (0.0,1000.0), False, True);
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return VRPSDAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -mh ils"
        
class VRPSD_SA_Algorithm(VRPSDAlgorithm):
    
    def __init__(self, path):
        path = os.path.normpath(path) + os.sep
        
        VRPSDAlgorithm.__init__(self, path+"vrpsd.sa")
 
        self._definition.Add("Initial temperature multiplier factor", "-itf", 0.01, (0.0,0.1), False, True);
        self._definition.Add("Cooling rate factor alpha", "-alpha", 0.98, (0.0,1.0), False, True);
        self._definition.Add("Annealing interval", "-rtl", 1, (1,100), False, True);
        self._definition.Add("Reheating interval", "-ilr", 20, (1,100), False, True);
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return VRPSDAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -mh sa"
        
class VRPSD_TS_Algorithm(VRPSDAlgorithm):
    
    def __init__(self, path):
        path = os.path.normpath(path) + os.sep
        
        VRPSDAlgorithm.__init__(self, path+"vrpsd.ts")
 
        self._definition.Add("Tabu tenure factor", "-ttf", 0.8, (0.0,1.0), False, True);
        self._definition.Add("Evaluation probability for tabulisted moves", "-pt", 0.8, (0.0,1.0), False, True);
        self._definition.Add("Evaluation probability for other moves", "-po", 0.3, (0.0,1.0), False, True);
    
    def GetCmd(self, outputFormat=None, inputFormat=None):
        return VRPSDAlgorithm.GetCmd(self, outputFormat, inputFormat)+" -mh ts"

def main(argv):
    wrapperParameters = BaseAlgorithm.ParseWrapperParameters(argv, ["-mh", "-cmd"])
    mh = wrapperParameters["-mh"]
    path = os.path.dirname(wrapperParameters["-cmd"])
    
    if (mh=='acs'):
        algo = VRPSD_ACS_Algorithm(path)
    if (mh=='ea'):
        algo = VRPSD_EA_Algorithm(path)
    if (mh=='fr'):
        algo = VRPSD_FR_Algorithm(path)
    if (mh=='ils'):
        algo = VRPSD_ILS_Algorithm(path)
    if (mh=='sa'):
        algo = VRPSD_SA_Algorithm(path)
    if (mh=='ts'):
        algo = VRPSD_TS_Algorithm(path)
        
    cmdargs = BaseAlgorithm.ParseAlgorithmParameters(argv, algo.GetDefinition(), wrapperParameters["-ifmt"])
        
    try:
        result = algo.Evaluate(cmdargs)
        BaseAlgorithm.PrintOutput(result, wrapperParameters["-ofmt"])
    except WrapperError as we:
        print >> sys.stderr, str(we)
        sys.exit(1)
    
if __name__ == "__main__":
    if len(sys.argv)==1 or (sys.argv[1] in ["-h", "-help", "--h", "--help"]):
        bare = VRPSDAlgorithm("")
        bare.PrintUsage()
    else:
        main(sys.argv[1:])
           
