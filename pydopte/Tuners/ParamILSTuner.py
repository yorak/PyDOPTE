# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 15:07:41 2011

@author: jussi
"""

import os
import re
from time import sleep

from ParameterSet import MAX_INT, MAX_FLOAT
from ExternalTuner import *
from BaseTuner import TunerError
from ParameterSet import ParameterSetDefinition
from Algorithms import GFEAlgorithm
import PathManager

TEMP_SCENARIO_FILE = "tuning_scenario.txt"
TEMP_ALGORITHM_FILE = "algo_paramils_wrapper.py"

class ParamILSTuner(ExternalTuner):
    
    reFinalRow = re.compile(".*Final best parameter configuration:")
    reEvaluationRow = re.compile(".*Trial [0-9]+ for calling:")
    
    """A tuner that has parameters defined in tunerParameterSetDefinition
    ( a ParameterSetDefinition class instance )"""
    def __init__(self, path):
        
        cmd = os.path.normpath(path) + os.sep + "paramils"
        ExternalTuner.__init__(self, cmd)
        
        # Wrapper parameters
        self._definition.Add("Discretization steps", "-discretization", 5, (0,MAX_INT), True, False)
        
        # Solution file parameters
        self._definition.Add("Algorithm is deterministic", "-solf_deterministic", 0, (0,1), True, False)       
        self._definition.Add("Combine objectives", "-solf_overall_obj", "mean", ("mean","median","q90","adj_mean","mean1000","geomean"), True, True)
        self._definition.Add("Timeout", "-solf_tunerTimeout", 3600, (0,MAX_INT), True, False)
        self._definition.Add("Tuning target", "-solf_run_obj", "qual", ("qual", "approx","runtime","runlength"), True, False)
        
        # Command line parameters
        self._definition.Add("Seed", "-numRun", 0, (0,MAX_INT), True, False)
        self._definition.Add("Evaluation budget", "-maxEvals", 10, (0,MAX_INT), False, False)
        self._definition.Add("Iterations budget", "-maxIts", 10, (0,MAX_INT), False, False)
        self._definition.Add("Search method", "-approach", "focused", ("basic","focused","random"), True, True)
        self._definition.Add("Evaluations/parameter set", "-N", 1, (0,1000), False, False)
        self._definition.Add("Validate on test set", "-validN", 0, (0,1000), True, False)
        
        self._definition.Add("Runlogging", "-userunlog", 0, (0,1), False, False)
        
        ## Omitted parameters
        
        ## The algorithm returns just one value. Use that (what it means is defined in algorithm)
        #self._definition.Add("tuned objective", "-run_obj", 0, (0,1), True, False)
        ## The algorithms implement the cutoff, not the tuner
        #self._definition.Add("Algorithm cutoff time", "-cutoff time", 0, (0,1), True, False)
        #self._definition.Add("Algorithm cutoff lenght", "-cutoff length", 0, (0,1), True, False)

    def getOutputLineRecognizer(self, key):
        if key=="ops":
            return ParamILSTuner.reEvaluationRow
        elif key=="special":
            return ParamILSTuner.reFinalRow
        else:
            raise KeyError("No such input line recognizer")
             
    def createScenarioFile(self, scenarioFilename, tunerParameters, instancesFile, parametersFile ):
        
        #algo
        #execdir
        #paramfile
        #outdir
        #instance file
        #instance seed file
        
    
        # Tuned algorithm input / output formatting
        apsd = self._algorithm.GetDefinition()
        instanceInDesc = "Instance"
        seedInDesc = "Seed"
        deterministicAlgo = tunerParameters["-solf_deterministic"]==1
        
        if not apsd.HasParameter("Instance"):
            # Algorithm has no instance input
            instanceInDesc = ""
            
        if deterministicAlgo:
            # Deterministic algorithm has no seed input
            seedInDesc = ""
        elif not apsd.HasParameter("Seed"):
            raise TunerError("ParamILS requires stochastic algorithm to have seed parameter (if algorithm is deterministic, set -solf_deterministic to 1).")
    
        algoCmd = self._algorithm.GetCmd(\
            outputFormat="Result for ParamILS: SAT, {time}, 0, {obj}, {seed}",\
            inputFormat="{%s} {} {} {} {%s}" % (instanceInDesc, seedInDesc) )
        
        # ParamILS does not like long commands, so use wrapper of the wrapper
        # "Yo dawg, I herd you like wrappers, so I put an wrappers in your wrappers so you can generalize while you generalize."
        cmdf = open(TEMP_ALGORITHM_FILE,"w")
        cmdf.write("import os, sys\n")
        cmdf.write("algoCmd = '%s'\n" % algoCmd.replace("\"", "\\\"").replace("\'", "\\\'"))
        cmdf.write("args = ['\"\"' if arg==\"\" else arg for arg in sys.argv[1:]]\n")
        cmdf.write("fullCmd = algoCmd+' '+' '.join(args)\n")
        #cmdf.write("print fullCmd\n")
       #cmdf.write('if os.system( "sleep 0.5 && exit 1" )!=0:')
        cmdf.write("if os.system( fullCmd )!=0:")
        cmdf.write("    print 'Result for ParamILS: UNSAT, 1.0, 0, -1, %s'%args[4]")
        cmdf.close()
        
        f = open(scenarioFilename,"w")
        f.write("algo = %s\n" % ("python "+TEMP_ALGORITHM_FILE) )
        f.write("execdir = ./\n")
        f.write("deterministic = %d\n" % tunerParameters["-solf_deterministic"] )
        f.write("run_obj = %s\n" % tunerParameters["-solf_run_obj"] )
        f.write("overall_obj = %s\n" % tunerParameters["-solf_overall_obj"] )
        
        f.write("cutoff_time = max\n" )
        f.write("cutoff_length = max\n" )
        
        if "-solf_tunerTimeout" in tunerParameters:
            f.write("tunerTimeout = %d\n" % tunerParameters["-solf_tunerTimeout"] )
        else:
            f.write("tunerTimeout = max\n" )
        
        f.write("paramfile = %s\n" % parametersFile )
        
        f.write("outdir = paramils_out\n")
        if not os.path.exists("./paramils_out"):
            os.makedirs("./paramils_out")
        
        if (len(self._training_instances)>0):
            if isinstance(self._training_instances[0], str) or isinstance(self._training_instances[0], unicode):
                f.write("instance_file = %s\n" % instancesFile )
                f.write("test_instance_file = %s\n" % instancesFile )
            else:
                f.write("instance_seed_file = %s\n" % instancesFile )
                f.write("test_instance_seed_file = %s\n" % instancesFile )
        
        f.close()
        #Omitted the test_files (tests are done by the Pydoe as needed
    
    def createAlgorithmParametersFile(self, configurationFilename, tunerParameters, ad ):
        
        if "Instance" in ad.AllParameterDescriptions():  
            instanceParameterName = ad.GetParameterSwitch("Instance")
        else:
            instanceParameterName = None
        if "Seed" in ad.AllParameterDescriptions():
            seedParameterName = ad.GetParameterSwitch("Seed")
        else:
            seedParameterName = None

        f = open(configurationFilename,"w")
        
        for fp in ad.FixedParameters():
            if (fp==instanceParameterName) or (fp==seedParameterName):
                continue
            self._WriteParameterLine(f, fp, ad, rangeOfOne=True)
        
        for tp in ad.TunableParameters():
            self._WriteParameterLine(f, tp, ad)
        
        f.close()
    
    # Helper for the parameter file generation
    def _WriteParameterLine(self, f, sw, ad, rangeOfOne=False):
        
        if rangeOfOne:
            prng = []
        else:
            prng = list(ad.GetParameterRange(sw))
            
        pd = ad.GetParameterDefault(sw)
        
        # Make sure default is in the list of discrete values
        if not pd in prng:
            prng.append(pd)
            prng.sort()
        
        prngs = (str(ri) for ri in prng)
        
        ## Todo: Instead of strip, convert to underscore?
        f.write(sw.strip("- "))
        f.write(" {")
        f.write(",".join(prngs))
        f.write("}")
        f.write(" [")
        f.write(str(pd))
        f.write("]\n")

       
    def CreateAlgorithmCommand(self, algoParamSet):
        
        # Build the tuner parameters as cmd line arguments
        cmdargs = list()
        for (k,v) in algoParamSet.items():
            if ("-solf_" in k) or (k=="-discretization"):
                # These are written into scenariofile or handeled otherwise
                continue
            cmdargs.append(k)
            cmdargs.append(str(v))
        
        fullcmd = self._cmd + " -scenariofile " + TEMP_SCENARIO_FILE + " " + " ".join(cmdargs)
        return fullcmd
    
    
    
    def Tune(self, tunerParameterSet=None):
        
        if not self._algorithm:
            raise ValueError("No algorithm to tune")
        
        if not tunerParameterSet:
            tunerParameterSet = self.GetDefinition().NewDefaultParameterSet()
            
        dsteps = tunerParameterSet["-discretization"]
        # Discretized clone
        dAlgoPSD = ParameterSetDefinition( self._algorithm.GetDefinition(), dsteps )
        
        
        # Setup temp files and folder
        self.createAndSetTuningFolder()
        
        self.createAlgorithmParametersFile( TEMP_PARAMETERS_FILE, tunerParameterSet, dAlgoPSD )
        
        if isinstance(self._training_instances[0], str):
            # Only instances are specified
            ExternalTuner.createAlgorithmInstancesFile( TEMP_INSTANCES_FILE, self._training_instances, False )
        else:
            # Seed and instance are specified
            ExternalTuner.createAlgorithmInstancesFile( TEMP_INSTANCES_FILE, self._training_instances, True )
            
        self.createScenarioFile(TEMP_SCENARIO_FILE,\
            tunerParameterSet,\
            TEMP_INSTANCES_FILE,\
             TEMP_PARAMETERS_FILE )
        
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
       
# TODO: Implement cmd line interface (for metatuning)  

""" Code that test the basic operation of the ParamILSTuner """    
def main():
    
    algo = GFEAlgorithm.GFEAlgorithm(10, 1)

    # Run random parameter tuner with defaults and with dummy algo
    tuner = ParamILSTuner(PathManager.GetTuningBasePath()+"Tuners/paramils2.3.5/bin")
    dps = tuner.GetDefinition().NewDefaultParameterSet()
    #dps["-approach"]="basic"
    dps["-solf_deterministic"]=1
    # CMA-ES gets down to f(x*)<1000 with ~850 evals
    # ParamILS produces quality of 339.1, 285.6
    dps["-maxEvals"]=850
    #dps["-maxEvals"]=10
    dps["-numRun"]=0
    #dps["-N"]=1
    dps["-discretization"]=10
    
    
    # Show all
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    tuner.SetAlgorithm(algo)
    tuner.SetInstances([PathManager.GetTuningBasePath()+"Benchmarks/gfe/f1_c/f1_c_1.spc"])
    
    # Tune
    tuningResult = tuner.Tune(dps)
    print "Quality: " + str(tuningResult["obj"])
    print "Evaluations: " + str(tuningResult["ops"])
    print "Tuned parameters: " + str(tuningResult["special"])
    
if __name__ == '__main__':
    main()