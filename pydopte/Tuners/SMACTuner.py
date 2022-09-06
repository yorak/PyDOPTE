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
TEMP_ALGORITHM_FILE = "algo_smac_wrapper.py"

class SMACTuner(ExternalTuner):
    
    
    reEvaluationCountRow = re.compile(".*Total Number of runs performed: ([0-9]+)")
    reTuningComplete = re.compile(".*Number of runs ([0-9]+) is greater than the number permitted ([0-9]+)")
    reQualityRow = re.compile(".*Performance of the Incumbent: ")
    
    """A tuner that has parameters defined in tunerParameterSetDefinition
    ( a ParameterSetDefinition class instance )"""
    def __init__(self, path):
        
        cmd = os.path.normpath(path) + os.sep + "smac"
        ExternalTuner.__init__(self, cmd)
        
        # Solution file parameters
        self._definition.Add("Algorithm is deterministic", "-solf_deterministic", 0, (0,1), True, False)       
        self._definition.Add("Combine objectives", "-solf_overall_obj", "MEAN", ("MEAN", "MEAN1000", "MEAN10"), True, True)
        self._definition.Add("Timeout", "-solf_tunerTimeout", 3600, (0,MAX_INT), False, False)
        self._definition.Add("Tuning target", "-solf_run_obj", "QUALITY", ("QUALITY", "RUNTIME"), True, False)
        
        # Command line parameters
        self._definition.Add("Seed", "--numRun", 0, (0,MAX_INT), True, False)
        self._definition.Add("Evaluation budget", "--totalNumRunsLimit", 10, (0,MAX_INT), False, False)
        self._definition.Add("Iterations budget", "--numIterations", 10, (0,MAX_INT), False, False)
        self._definition.Add("Wall time configuration time limit", "---runtimeLimit", 3600, (0,MAX_INT), False, False)
        
        self._definition.Add("Perform validation", "--doValidation", "false", ("false","true"), True, False)
        self._definition.Add("Search method", "--executionMode", "SMAC", ("SMAC","ROAR"), True, True)
        
        # Output
        self._definition.Add("Verbosity", "--consoleLogLevel", "ERROR", ('OFF', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'), False, False)
        
        
        
        # Omitted parameters
        #
        #--imputationIterations amount of times to impute censored data when building model
        #Default Value: 2, Domain: [0, 2147483647]
        #
        #--intensificationPercentage percent of time to spend intensifying versus model learning
        # Default Value: 0.5, Domain: (0.0, 1.0)
        #
        # --maxIncumbentRuns maximum number of incumbent runs allowed
        # Default Value: 2000, Domain: (0, 2147483647]
        #
        #--numChallengers number of challengers needed for local search
        # Default Value: 10, Domain: (0, 2147483647]
        #
        #--numEIRandomConfigs number of random configurations to evaluate during EI search
        # Default Value: 10000, Domain: [0, 2147483647]
        #
        #--numPCA number of principal components features to use when building the model
        # Default Value: 7, Domain: (0, 2147483647]
        

    def getOutputLineRecognizer(self, key):
        if key=="ops":
            return SMACTuner.reEvaluationRow
        elif key=="special":
            return SMACTuner.reFinalRow
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
        
        f.write("cutoff_time = %d\n" % MAX_INT)
        #if apsd.HasParameter("Timeout"):
        #    algo_cutoff_sw = apsd.GetParameterSwitch("Timeout")
         

        
        if "-solf_tunerTimeout" in tunerParameters:
            f.write("tunerTimeout = %d\n" % tunerParameters["-solf_tunerTimeout"] )
        else:
            f.write("tunerTimeout = %d\n" % MAX_INT)
        
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
        
        if ad.HasParameter("Instance"):  
            instanceParameterName = ad.GetParameterSwitch("Instance")
        else:
            instanceParameterName = None
            
        if ad.HasParameter("Seed"):
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
        
        # Make sure default is in the list
        if len(prng)!=2 and not pd in prng:
            prng.append(pd)
            prng.sort()
        
        prngs = (str(ri) for ri in prng)
        
        ## Todo: Instead of strip, convert to underscore?
        f.write(sw.strip("- "))
        
        # Range (categocial)
        if len(prng) != 2:
            f.write(" {")
            f.write(",".join(prngs))
            f.write("}")
        # Range (numeric)
        else:
            f.write(" [")
            f.write(",".join(prngs))
            f.write("]")
            
        # Default
        f.write(" [")
        f.write(str(pd))
        f.write("]")

        if isinstance(prng[0], (int, long)):            
            f.write("i")
        f.write("\n")

    def ParseExternalOutput(self, row, rowresult):
        """ Specialized parsing for SMAC (default does not work here)
        """
        
        if not "special" in rowresult:
            if self.reTuningComplete.match(row):
                # Adding empty placeholder means we expect new results
                rowresult["special"] = []
        else:
            ecr = self.reEvaluationCountRow.match(row)
            if ecr:
                rowresult["ops"] = int(ecr.group(1))
              
            qr = self.reQualityRow.match(row)
            if qr:
                rowresult["obj"] = float( row.split()[-1] )
            
        return rowresult
       
    def CreateAlgorithmCommand(self, algoParamSet):
        
        # Build the tuner parameters as cmd line arguments
        cmdargs = list()
        for (k,v) in algoParamSet.items():
            if ("-solf_" in k):
                # These are written into scenariofile or handeled otherwise
                continue
            cmdargs.append(k)
            cmdargs.append(str(v))
        
        fullcmd = self._cmd + " --optionFile " + TEMP_SCENARIO_FILE + " " + " ".join(cmdargs)
        return fullcmd
    
    def Tune(self, tunerParameterSet=None):
        
        if not self._algorithm:
            raise ValueError("No algorithm to tune")
        
        if not tunerParameterSet:
            tunerParameterSet = self.GetDefinition().NewDefaultParameterSet()
        
        
        # Setup temp files and folder
        self.createAndSetTuningFolder()
        
        
        self.createAlgorithmParametersFile( TEMP_PARAMETERS_FILE, tunerParameterSet, self._algorithm.GetDefinition() )
        if isinstance(self._training_instances[0], str) or isinstance(self._training_instances[0], unicode):
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
        
        # Dig the "winning" configuration from the trajectory file
        N = tunerParameterSet["--numRun"]
        pilsdir = "paramils_out"
        apsd = self._algorithm.GetDefinition()
        for dn in os.listdir(pilsdir):
            # Get the 
            traj_dir_path = os.path.join(pilsdir, dn)
            if "RunGroup" in dn and os.path.isdir(traj_dir_path):
                
                
                # Get the last (best) configuration
                traj_filename = os.path.join(traj_dir_path, "traj-run-%d.txt" % N)
                for line in open(traj_filename, "r"):
                    last=line
                
                #print last
                tuningResult["special"] = self.convertStringToParameters(apsd, last)
                
        # Run the algo once to get the objective value
        BaseTuner.initFixedParameters(self._algorithm, tuningResult["special"])
        tuningResult["obj"] = self.calculateAlgorithmPerformance(\
            self._algorithm,\
            tuningResult["special"],\
            self._validation_instances )["obj"]

        #Quickfix. Sometimes the ["ops"] (evaluation budget) output row is
        # not recognized. IF that happens, just use given budget
        # (SMAC tends to respect that)
        #TODO: Find root cause
        if "ops" not in tuningResult:
            tuningResult["ops"]=tunerParameterSet["--totalNumRunsLimit"]
        
        # Delete temp files and folder
        if CLEAN_UP_TEMP_FILES:
            self.cleanUpTuningFolder()
        
        return tuningResult
       
# TODO: Implement cmd line interface (for metatuning)  

""" Code that test the basic operation of the SMACTuner """    
def main():
    
    # Run random parameter tuner with defaults and with dummy algo
    tuner = SMACTuner(PathManager.GetTuningBasePath()+"Tuners/smac-v2.02.00-master-375")
    dps = tuner.GetDefinition().NewDefaultParameterSet()
    #dps["-approach"]="basic"
    dps["-solf_deterministic"]=1
    # CMA-ES gets down to f(x*)<1000 with ~850 evals
    # ParamILS produces quality of 339.1, 285.6
    dps["--totalNumRunsLimit"]=10
    dps["--numRun"]=0
    dps["--consoleLogLevel"]="INFO"
            
    # Show all
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    #VRPSD_PATH = PathManager.GetTuningBasePath()+"Solvers/VRPSD/bin"           
    #VRPSDAlgorithms.VRPSD_ACS_Algorithm(VRPSD_PATH)
    
    algo = GFEAlgorithm.GFEAlgorithm(10, 1)
    tuner.SetAlgorithm(algo)
    tuner.SetInstances([PathManager.GetTuningBasePath()+"Benchmarks/gfe/f1_c/f1_c_1.spc"])
    
    # Tune
    tuningResult = tuner.Tune(dps)
    print "Quality: " + str(tuningResult["obj"])
    print "Evaluations: " + str(tuningResult["ops"])
    print "Tuned parameters: " + str(tuningResult["special"])
    
if __name__ == '__main__':
    main()