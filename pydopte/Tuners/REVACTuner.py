# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 17:28:01 2011

@author: juherask
"""



from ParameterSet import MAX_INT, MAX_FLOAT
from ExternalTuner import *
import PathManager
from BaseTuner import TunerError

import re
import time
import random
import logging
import os

class REVACTuner(ExternalTuner):
    
    # The REVACTuner handles floats with decimals. At min, this many decimals are taken into account
    #  exmaples,
    #  range [0.1, 0.90000000000001] -> [10,90], 1 decimal
    #  range [0.01, 0.9] -> [1,90], 2 decimals
    #  range [1.5, 4.5] -> [150,450], 2 decimals
    MAX_DECIMAL_ACCURACY = 3
    
    # TODO: IRace final row and evaluated?
    reEvaluationCountRow = re.compile("Evaluations: ([0-9]+)")
    reTunedStarts = re.compile(".*FINAL CONFIGURATION")
    
    """A python wrapper for a REVAC tuner"""
    def __init__(self, path):
        
        cmd = os.path.normpath(path) + os.sep + "REVAC"
        ExternalTuner.__init__(self, cmd)
        
        #self._definition.Add("Timeout", "-cutoff", 0, (0,MAX_INT), False, False)
        self._definition.Add("Seed", "-seed", 0, (0,MAX_INT), False, False)
        self._definition.Add("Evaluation budget", "-eb", 0, (0,MAX_INT), False, False)
        
        # Algorithm parameters
        self._definition.Add("Iterations", "-I", 1000, (0,10000), False, True)
        self._definition.Add("Population", "-m", 100, (0,1000), False, True)
        self._definition.Add("Crossover operation size", "-n", 50, (0,500), False, True)
        self._definition.Add("Mutation operation size", "-h", 5, (0,MAX_INT), False, True)
        
        self._definition.Add("Seed with default values", "-d", 0, (0,1), False, False)
        
        #self._definition.Add("Float accuracy", "-fa", 2, (0,MAX_INT), True, True)
        
        
        self._definition.Add("Verbosity", "-v", 0, (0,MAX_INT), False, False)
        
    def ParseExternalOutput(self, row, rowresult):
        """ Specialized parsing for REVAC (default does not work here)
        """
        
        ecr = self.reEvaluationCountRow.match(row)
        if ecr:
            rowresult["ops"] = int(ecr.group(1))
            
        elif self.reTunedStarts.match(row):
            # This means we are ready to add new results
            rowresult["special"] = {}
        
        elif "special" in rowresult:
            # We are reading rows of parameters
            apsd = self._algorithm.GetDefinition()
            # Strip id 
            parts = row.split()
            if len(parts)==3:
                paramName = parts[0]
                paramValue = parts[1] 
                if paramName in apsd.AllParameterSwitches():
                    paramType = type(apsd.GetParameterDefault(paramName))
                    rowresult["special"][paramName]=paramType(paramValue)
            
        return rowresult
    
    def getOutputLineRecognizer(self, key):
        pass
         
   
    def createAlgorithmParametersFile(self, configurationFilename, tunerParameterSet, ad ):
        
        f = open(configurationFilename,"w")
        
        f.write(str(len(list(ad.TunableParameters()))))
        f.write("\n")
        
        write_defaults = False
        if "-m" in tunerParameterSet and tunerParameterSet["-m"]==1:
            write_defaults = True
            
        for tp in ad.TunableParameters():
            self._writeParameterLine(f, tp, ad, write_defaults)
        
        f.close()
    
    # Helper for the parameter file generation
    def _writeParameterLine(self, f, sw, ad, write_defaults):
        
        prng = tuple(ad.GetParameterRange(sw))
        defaultValue = ad.GetParameterDefault(sw)
        paramObjType = type(defaultValue)
        
        if len(prng)>2:
            # No way of differing ordinal and categorical -> all categrocial
            raise TunerError("REVAC does not support categorical parameters.")
        
        rmin = prng[0]
        rmax = prng[-1]
        
        if paramObjType==float:
            #  range [0.1, 0.90000000000001] -> [10,90], 1 decimal
            #  range [0.01, 0.9] -> [1,90], 2 decimals
            #  range [1.5, 4.5] -> [150,450], 2 decimals
            #  range [1.0, 4.0] -> [150,450], 2 decimals
            
            min_dc = 0
            max_dc = 0
            
            # Use best possible accuracy, if it cannot be inferred
            if float(int(rmin))==rmin:
                min_dc = REVACTuner.MAX_DECIMAL_ACCURACY
            if float(int(rmax))==rmax:
                max_dc = REVACTuner.MAX_DECIMAL_ACCURACY
            
            da = 0
            while min_dc<REVACTuner.MAX_DECIMAL_ACCURACY or max_dc<REVACTuner.MAX_DECIMAL_ACCURACY:
                if int((rmin-int(rmin))*10**da)>0:
                    min_dc+=1
                if int((rmax-int(rmax))*10**da)>0:
                    max_dc+=1
                da+=1
                
            decimals_multiplier = 10**max(REVACTuner.MAX_DECIMAL_ACCURACY, min_dc, max_dc)
                
            rmin = int(rmin*decimals_multiplier)
            rmax = int(rmax*decimals_multiplier)
            # this feels silly, but it is right, the codREVAC
            #  calculates the value with the formula
            # cal_temp->parametro[i]/((float)configuracion_parametros[i].decimales
            da = decimals_multiplier
            
            dv = defaultValue*da
             
        elif paramObjType==int:
            da = 0
            dv = defaultValue
        else:
            raise TunerError("String (or other more exotic) parameter types are not supported by REVAC")
        
            
        # Switch
        f.write(sw) 
        f.write(" ")
        # Range/values
        f.write(str(rmin))
        f.write(" ")
        f.write(str(rmax))
        f.write(" ")
        # Type
        f.write(str(da))
        f.write(" ")
        
        if write_defaults:
            # Optional default value
            # TODO: The codREVAC does not yet support this!
            f.write(str(dv))
            f.write("\n") 
       
    def CreateAlgorithmCommand(self, algoParamSet):
        
        # Build the algorithm command
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
            
        algoCmd = self._algorithm.GetCmd( inputFormat="{%s} {%s}" % (instanceInDesc, seedInDesc) ).replace('"', '\\"')
        
        # Fixed parameters do not change so embed them inside algorithm hook files
        fixedParams = ""
        for fpsw in apsd.FixedParameters():
            if (fpsw!=isw) and (fpsw!=ssw):
                fixedParams+=(" %s %s" % (fpsw, apsd.GetParameterDefault(fpsw)))
        fixedParams.strip()
        algoCmd += " " + fixedParams
        
        #Usage: REVAC <algo_exe> <algo_parameter_config_file> <instances_file> <seed> [<verbosity> <max_iter> <M> <N> <H> <eval_budget>]
        seed = random.randint(0, MAX_INT)
        verbosity = self._definition.GetParameterDefault("Verbosity")
        max_iter = self._definition.GetParameterDefault("-I")
        M = self._definition.GetParameterDefault("-m")
        N = self._definition.GetParameterDefault("-n")
        H = self._definition.GetParameterDefault("-h")
        eb = self._definition.GetParameterDefault("-eb")
        
        if "-seed" in algoParamSet:
            seed = algoParamSet["-seed"]
        if "-v" in algoParamSet:
            verbosity = algoParamSet["-v"]
        if "-I" in algoParamSet:
            max_iter = algoParamSet["-I"]
        if "-m" in algoParamSet:
            M = algoParamSet["-m"]
        if "-n" in algoParamSet:
            N = algoParamSet["-n"]
        if "-h" in algoParamSet:
            H = algoParamSet["-h"]
        if "-eb" in algoParamSet:
            max_eval = algoParamSet["-eb"]
        
        fullcmd = self._cmd +\
         " \"" + algoCmd + "\""\
         " \"" + TEMP_PARAMETERS_FILE + "\""\
         " \"" + TEMP_INSTANCES_FILE + "\""\
         " " + str(seed) + \
         " " + str(verbosity) + \
         " " + str(max_iter) + \
         " " + str(M) + \
         " " + str(N) + \
         " " + str(H) + \
         " " + str(max_eval)
         
        return fullcmd
       
# TODO: Implement cmd line interface (for metatuning)  


""" Code that test the basic operation of the REVACTuner """    
def main():
    
    from Algorithms.GFEAlgorithm import GFEAlgorithm
    algo = GFEAlgorithm(10, 1)

    # Run random parameter tuner with defaults and with dummy algo
    tuner = REVACTuner(PathManager.GetTuningBasePath()+"Tuners/codREVAC/bin/")
    dps = tuner.GetDefinition().NewDefaultParameterSet()
    
    # CMA-ES gets down to f(x*)<1000 with ~850 evals
    # IRace produces quality of
    
    # Show all
    logging.basicConfig(level=logging.DEBUG)
    
    INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/gfe/f1_c'
    INSTANCE_REQUIRED_EXT = ".txt"
    SAMPLES = 14
    
    # Sample instances from instance folder
    instancefiles = []
    for fn in os.listdir(INSTANCE_FOLDER):
        extension = os.path.splitext(fn)[1]
        if extension==INSTANCE_REQUIRED_EXT:
            instancefiles.append(os.path.join(INSTANCE_FOLDER, fn))
    #random.shuffle(instancefiles)
    instances = instancefiles[0:SAMPLES]
    
    #instances = [PathManager.GetTuningBasePath()+"Benchmarks/gfe/f1_c/f1_c_1.spc"]
    
    tuner.SetAlgorithm(algo)
    tuner.SetInstances(instances) 
    
    for i in range(4):
        if i==0:
            dps["-m"]=5
            dps["-n"]=2
            dps["-h"]=2
            dps["-eb"]=10
        if i==1:
            dps["-m"]=5
            dps["-n"]=2
            dps["-h"]=2
            dps["-eb"]=100
        elif i==2:
            dps["-m"]=10
            dps["-n"]=5
            dps["-h"]=2
            dps["-eb"]=500
        elif i==3:
            dps["-m"]=20
            dps["-n"]=10
            dps["-h"]=2
            dps["-eb"]=1000
        
        #dps["-v"]=5

        # Tune
        tuningResult = tuner.Tune(dps)
        print "Quality: " + str(tuningResult["obj"])
        print "Evaluations: " + str(tuningResult["ops"])
        print "Tuned parameters: " + str(tuningResult["special"])
        
        #break
    
if __name__ == '__main__':
    main()