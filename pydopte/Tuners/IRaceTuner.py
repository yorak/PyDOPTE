# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 15:07:41 2011

@author: jussi
"""

import os

from ParameterSet import MAX_INT, MAX_FLOAT
from ExternalTuner import *
from BaseTuner import TunerError
from ParameterSet import ParameterSetDefinition 

from time import time, sleep
import re
import logging
import PathManager


TEMP_HOOK_RUN_FILE = "hook-run"
TEMP_HOOK_EVALUATE_FILE = "hook-evaluate"
TEMP_DEFAULTS_FILE = "algo_defaults.txt"
TEMP_OUT_DIR = "./irace_out"


TEMP_HOOK_EVALUATE_CONTENTS = \
"""#!/bin/bash
INSTANCE=$1
CANDIDATE=$2
TOTALCANDIDATES=$3

STDOUT=c${CANDIDATE}.stdout
STDERR=c${CANDIDATE}.stderr

error() {
    echo "`TZ=UTC date`: error: $@"
    exit 1
}

# This assumes that the objective value is the first number in
# the first column of the only line starting with a digit.
if [ -s "${STDOUT}" ]; then
    COST=$(cat ${STDOUT} | grep -e '^[[:space:]]*[+-]\?[0-9]' | cut -f1)
    echo "$COST"
    rm -f "${STDOUT}" "${STDERR}"
    exit 0
else
    error "${STDOUT}: No such file or directory"
fi
"""

TEMP_HOOK_RUN_CONTENTS =  \
"""#!/bin/bash
EXE="%s" # PyDote algorithm wrapper is inserted here
FIXED_PARAMS="%s" # Fixed paramters (excluding instance and seed) are here
INSTANCE=$1
CANDIDATE=$2

shift 2 || exit 1

CAND_PARAMS=$*

STDOUT=c${CANDIDATE}.stdout
STDERR=c${CANDIDATE}.stderr

# We use 'exec' to avoid creating another process. There can be no
# other commands after exec.
exec ${EXE} ${INSTANCE} ${FIXED_PARAMS} ${CAND_PARAMS} 1> ${STDOUT} 2> ${STDERR}
"""

class IRaceTuner(ExternalTuner):
    
    # TODO: IRace final row and evaluated?
    reEvaluationCountRow = re.compile(".*# experimentsUsedSoFar: ([0-9]+)")
    reTunedStarts = re.compile(".*# Best candidates \(as commandlines\)")
    
    """A tuner that has parameters defined in tunerParameterSetDefinition
    ( a ParameterSetDefinition class instance )"""
    def __init__(self, path):
        
        cmd = os.path.normpath(path) + os.sep + "irace"
        ExternalTuner.__init__(self, cmd)
        
        # Wrapper parameters
        self._definition.Add("Timeout", "--timeBudget", 0, (0,MAX_INT), False, False)
        self._definition.Add("Seed", "--seed", 0, (0,MAX_INT), False, False)
        self._definition.Add("Evaluation budget", "--max-experiments", 100, (0,MAX_INT), False, False)
        
        self._definition.Add("Significant digits for real parameters", "--signif-digits", 4, (0,MAX_INT), False, True)
        self._definition.Add("Test type", "--test-type", "F-test", ("F-test","t-test"), False, True)
        self._definition.Add("Instances for first test", "--first-test", 5, (0,MAX_INT), False, True)
        self._definition.Add("Instances for each test after first", "--each-test", 1, (0,MAX_INT), False, True)
        self._definition.Add("Enable soft restart", "--soft-restart", 1, (0,1), False, True)
     
        self._definition.Add("Verbosity", "--debug-level", 0, (0,MAX_INT), False, False)
        
        self._definition.Add("Number of evaluations to execute in parallel", "--parallel", 0, (0,MAX_INT), False, False)
        
        # Not recommended to touch these
        self._definition.Add("Number of race iterations (see manual)", "--iterations", 0, (0,MAX_INT), False, False)
        self._definition.Add("Number of experiments per iteration (see manual)", "--experiments-per-iteration", 0, (0,MAX_INT), False, False)
        self._definition.Add("Instance sampling (see manual)", "--sample-instances", 1, (0,1), False, False)
        self._definition.Add("Max. instances per iteration (see manual)", "--max-instances", 1000, (0,MAX_INT), False, False)
        self._definition.Add("Required survivals to continue (see manual)", "--min-survival", 0, (0,MAX_INT), False, False)
        self._definition.Add("New candidates per iteration (see manual)", "--num-candidates", 0, (0,MAX_INT), False, False)
        self._definition.Add("Value for automatic candidate sampling (see manual)", "--mu", 5, (0,MAX_INT), False, False)

        ## Omitted parameters
        #self._definition.Add("Configuration file", "-c", "", (), False, False)
        self._definition.Add("Algorithm instances directory", "--instance-dir", "", (), True, False)
        #self._definition.Add("Experiment name", "--exp-name", "", (), False, False)
        #self._definition.Add("Experiment description", "--exp-description", "", (), False, False)

        ## TODO: If cluster / distributed computing is implemented
        #self._definition.Add("Cluster mode (see manual)", "--sge-cluster", 0, (0,1), False, False)
        #self._definition.Add("Enable/disable MPI (see manual)", "--mpi", 0, (0,1), False, False)
       
        
        ### Omitted, but set by the wrapper
        #self._definition.Add("Parameter file", "-p", "", (), False, False)
        #self._definition.Add("Algorithm working directory", "--exec-dir", "", (), False, False)
        #self._definition.Add("Instance", "--instance-file", "", (), False, False)
        ## If timeBudget is positive, this must be set
        #self._definition.Add("Evaluation time estimate", "--time-estimate", 1, (0,MAX_INT), False, False)
        #self._definition.Add("Candidates file", "--candidates-file", "", (), False, False)
        
    def ParseExternalOutput(self, row, rowresult):
        """ Specialized parsing for iRace (default does not work here)
        """
        
        ecr = self.reEvaluationCountRow.match(row)
        if ecr:
            rowresult["ops"] = int(ecr.group(1))
            
        elif self.reTunedStarts.match(row):
            # This means we are ready to add new results
            rowresult["special"] = []
        
        elif "special" in rowresult:
            # We are reading rows of parameters
            apsd = self._algorithm.GetDefinition()
            # Strip id 
            parts = row.split()[1:]
            tunableParamCount = len(list(apsd.TunableParameters()))
            if len(parts) >= 2*tunableParamCount:
                paramrow = " ".join(parts)
                tuned = ExternalTuner.convertStringToParameters(apsd, paramrow)
                rowresult["special"].append( tuned )
            
        return rowresult
    
    def getOutputLineRecognizer(self, key):
        pass
         
    def createAlgorithmHookFiles(self, runHookFileName, evaluateHookFileName, hasSeed ):
        
        # Run hook file
        
        #  requires some knowledge about algo cmd
         
        apsd = self._algorithm.GetDefinition()
        instanceInDesc = "Instance"
        seedInDesc = "Seed"
        if not apsd.HasParameter("Instance"):
            instanceInDesc = ""
            isw = None
        else:
            isw = apsd.GetParameterSwitch("Instance")
            
        if not apsd.HasParameter("Seed"):
            seedInDesc = ""
            ssw = None
        else:
            ssw = apsd.GetParameterSwitch("Seed")
            
        if hasSeed and seedInDesc=="":
            raise TunerError("Seeds were given, but algorithm cannot use them (no seed parameter)")
        if hasSeed:
            algoCmd = self._algorithm.GetCmd( inputFormat="{%s} {%s}" % (seedInDesc, instanceInDesc) )
        else:
            algoCmd = self._algorithm.GetCmd(inputFormat="{%s}" % instanceInDesc )
        
        # Fixed parameters do not change so embed them inside algorithm hook files
        fixedParams = ""
        for fpsw in apsd.FixedParameters():
            if (fpsw!=isw) and (fpsw!=ssw):
                fixedParams+=(" %s %s" % (fpsw, apsd.GetParameterDefault(fpsw)))
        fixedParams.strip()
        
        # Write the file
        rhf = open(runHookFileName,"w")
        rhf.write( TEMP_HOOK_RUN_CONTENTS % (algoCmd, fixedParams) )
        rhf.close()
        
        
        # Eval hook file
        
        ehf = open(evaluateHookFileName,"w")
        ehf.write(TEMP_HOOK_EVALUATE_CONTENTS)
        ehf.close()
        
        
        # Make them executable
        
        os.chmod(runHookFileName, 0755)
        os.chmod(evaluateHookFileName, 0755)

        
    def createAlgorithmParametersFile(self, configurationFilename, tunerParameters, ad ):
  
        # Parameter ranges, types, conditions etc.      
        f = open(configurationFilename,"w")      
        f.write("# name \t switch \t type \t range [| conditions] \n")
        #param1          "--param1 "          i  (1, 10) | mode %in% c("x1", "x2")    
        for tp in ad.TunableParameters():
            self._WriteParameterLine(f, tp, ad)      
        f.close()
        
    def createAlgorithmDefaultsFile(self, defaultsFilename, ad ):
        # Parameter defaults
        tp = list( ad.TunableParameters() )
        
        f = open(defaultsFilename,"w")        
        # header 
        
        mtp = [sw.strip("-").replace(" ", "_" ) for sw in tp]
        line = "\t".join(mtp)
        f.write(line+"\n")
        #values
        #line = "\t".join( [str(ad.GetParameterDefault(t)) for t in tp] )
        dvls = [str(ad.GetParameterDefault(sw)) for sw in tp]
        line = "\t".join( dvls )
        f.write(line+"\n")        
        f.close()
    
    # Helper for the parameter file generation
    def _WriteParameterLine(self, f, sw, ad, rangeOfOne=False):
        
        #param2          "--param2 "          i  (1, 10) | mode %in% c("x1", "x3") && real > 2.5 && real <= 3.5
        #mode            "--"                 c  ("x1" ,"x2", "x3")
        #real            "--paramreal="       r  (1.5, 4.5)
        #mutation        "--mutation="        o  ("none", "very low", "low", "medium", "high", "very high", "all")
        ##unused         "-u "                c  (1, 2, 10, 20)

        if rangeOfOne:
            prng = tuple([ad.GetParameterDefault(sw), ad.GetParameterDefault(sw)])
        else:
            prng = tuple(ad.GetParameterRange(sw))
        
        if len(prng)>2:
            # No way of differing ordinal and categorical -> all categrocial
            paramType = "c" 
        else:
            paramObjType = type(ad.GetParameterDefault(sw))
            if paramObjType==int:
                paramType = "i"
            elif paramObjType==float:
                paramType = "r"
            elif paramObjType==str:
                paramType = "c"
            
        # Name
        f.write(sw.strip("-").replace(" ", "_" ))
        f.write(" \t ")
        # Switch
        f.write('"'+sw+' "') 
        f.write(" \t ")
        # Category
        f.write(paramType) 
        f.write(" \t ")
        # Range/values
        f.write(str(prng).replace("\'", "\"")+"\n")

       
    def CreateAlgorithmCommand(self, algoParamSet):
        
        # Build the tuner parameters as cmd line arguments
        cmdargs = list()
        for (k,v) in algoParamSet.items():
            cmdargs.append(k)
            cmdargs.append(str(v))
        
        ## These need to be set by the wrapper
        #self._definition.Add("Parameter file", "-p", "", (), False, False)
        #self._definition.Add("Algorithm working directory", "--exec-dir", "", (), False, False)
        #self._definition.Add("Instance", "--instance-file", "", (), False, False)
        ## If timeBudget is positive, this must be set
        #self._definition.Add("Evaluation time estimate", "--time-estimate", 1, (0,MAX_INT), False, False)
   
        fullcmd = self._cmd +\
         " -p " + TEMP_PARAMETERS_FILE +\
         " --exec-dir %s " % TEMP_OUT_DIR +\
         " --instance-file " + TEMP_INSTANCES_FILE +\
         " --candidates-file " + TEMP_DEFAULTS_FILE 
        
        # If timebudget is set, we have to give an estimate of the
        #  time that takes to do one evaluation.
        if ("--timeBudget" in cmdargs):
            apsd = self._algorithm.GetDefinition()
            if apsd.HasParameter("Timeout"):
                timeEstimate = apsd.GetParameterDefault("Timeout")
            else:
                one_instance = []
                if len(self._training_instances)>0:
                    one_instance = [self._training_instances[0]]
                
                start = time()
                self.calculateAlgorithmPerformance(\
                    self._algorithm,\
                    apsd.NewDefaultParameterSet(),\
                    one_instance)
                timeEstimate = int( time()-start )
                
            fullcmd+=" --timeEstimate " + timeEstimate
            
        fullcmd+=" " + " ".join(cmdargs)
         
        return fullcmd

    def _strip_dir_from_instance_paths(self, training_instance_paths):
        ipath = None
        training_instace_files = []
        for tipath in self._training_instances:
            training_instace_files.append(  os.path.basename(tipath) )
            if not ipath:
                ipath = os.path.dirname(tipath)
            else:
                # irace 1.07 seems not supprort this
                if ipath != os.path.dirname(tipath):
                    raise ValueError("irace requires all instances to be at the same folder")
        return ipath, training_instace_files
    
    
    def Tune(self, tunerParameterSet=None):
        
        if not self._algorithm:
            raise ValueError("No algorithm to tune")
        
        if not tunerParameterSet:
            tunerParameterSet = self.GetDefinition().NewDefaultParameterSet()
        
        
        # Setup temp files and folder
        self.createAndSetTuningFolder()
    

        if isinstance(self._training_instances[0], str) or isinstance(self._training_instances[0], unicode):
            
            ipath, training_instace_files = self._strip_dir_from_instance_paths(self._training_instances)
            tunerParameterSet["--instance-dir"] = ipath
                
            # Only instances are specified
            ExternalTuner.createAlgorithmInstancesFile( TEMP_INSTANCES_FILE, training_instace_files, False )
            hasSeed = False
        else:
            instance_seeds, instance_paths = zip(*self._training_instances)
            if not isinstance(instance_paths[0], str) and not isinstance(instance_paths[0], unicode):
                instance_paths, instance_seeds = zip(*self._training_instances)
            
            ipath, training_instace_files = self._strip_dir_from_instance_paths(instance_paths)
            tunerParameterSet["--instance-dir"] = ipath
            
            # Seed and instance are specified
            ExternalTuner.createAlgorithmInstancesFile( TEMP_INSTANCES_FILE, zip(instance_seeds, instance_paths), True )
            hasSeed = True
          
        if not os.path.exists(TEMP_OUT_DIR):
            os.makedirs(TEMP_OUT_DIR)
  
        self.createAlgorithmParametersFile( TEMP_PARAMETERS_FILE, tunerParameterSet, self._algorithm.GetDefinition() )
        self.createAlgorithmDefaultsFile( TEMP_DEFAULTS_FILE, self._algorithm.GetDefinition() )
        self.createAlgorithmHookFiles(TEMP_HOOK_RUN_FILE, TEMP_HOOK_EVALUATE_FILE, hasSeed)
        
        tuningResult = self.Evaluate(tunerParameterSet)
        
        if len(tuningResult["special"])>1:
            logging.debug("Warning: IRace returned multiple tuned parameter sets")
        if len(tuningResult["special"])>0:
            tuningResult["special"] = tuningResult["special"][0]
        
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


""" Code that test the basic operation of the IRaceTUner """    
def main():
    
    from Algorithms.GFEAlgorithm import GFEAlgorithm
    algo = GFEAlgorithm(10, 1)

    # Run random parameter tuner with defaults and with dummy algo
    tuner = IRaceTuner(PathManager.GetTuningBasePath()+"Tuners/irace-0.9/")
    dps = tuner.GetDefinition().NewDefaultParameterSet()
    # CMA-ES gets down to f(x*)<1000 with ~850 evals
    # IRace produces quality of 
    
    #dps["--max-experiments"]=850
    #dps["--iterations"]=4
    
    dps["--max-experiments"]=500
    #dps["--experiments-per-iteration"]=500
    #dps["--iterations"]=4
    
    INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/gfe/f1_c'
    INSTANCE_REQUIRED_EXT = ".txt"
    SAMPLES = 14
    
    # Show all
    logging.basicConfig(level=logging.DEBUG)
    
    # Sample instances from instance folder
    instancefiles = []
    for fn in os.listdir(INSTANCE_FOLDER):
        extension = os.path.splitext(fn)[1]
        if extension==INSTANCE_REQUIRED_EXT:
            instancefiles.append(os.path.join(INSTANCE_FOLDER, fn))
    import random
    random.shuffle(instancefiles)
    instances = instancefiles[0:SAMPLES]
    
    tuner.SetAlgorithm(algo)
    tuner.SetInstances(instances)
    
    # Tune
    tuningResult = tuner.Tune(dps)
    print "Quality: " + str(tuningResult["obj"])
    print "Evaluations: " + str(tuningResult["ops"])
    print "Tuned parameters: " + str(tuningResult["special"])
    
if __name__ == '__main__':
    main()