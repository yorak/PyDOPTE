# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 15:07:41 2011

@author: jussi
"""

import os
import re
import random

from ParameterSet import MAX_INT, MAX_FLOAT
from ExternalTuner import *
import PathManager

MAX_POP_SIZE = 1000
MAX_GENERATIONS = 1000
MIN_P = 15
MIN_G = 2
DEFAULT_P = 30
DEFAULT_G = 40

# Used when determining P and G when evaluation budget is set
P_IN_G_EVAL_RATIO = 0.45

# Print extra debug info
DEFAULT_VERBOSITY = 2

class GGATuner(ExternalTuner):
    
    reFinalRow = re.compile(".*Final most fit command")
    reEvaluationRow = re.compile(".*Runner [0-9]+ running next instance")
    
    def __init__(self, path):
        """A tuner that has parameters defined in tunerParameterSetDefinition
        ( a ParameterSetDefinition class instance )
        """
        cmd = os.path.normpath(path) + os.sep + "gga"
        ExternalTuner.__init__(self, cmd)
        
        ## GGA specifig parameters (enforce the use of defaults from Ansotegui2009)
        self._definition.Add("Population Size", "-p", 100, (DEFAULT_P,MAX_POP_SIZE), True, True)
        self._definition.Add("Generations", "-g", 100, (DEFAULT_G,MAX_GENERATIONS), True, True)
        self._definition.Add("Percent winners", "-w", 0.125, (0.0,1.0), True, True)
        self._definition.Add("Mutation rate", "-m", 0.1, (0.0,1.0), True, True)
        self._definition.Add("Cross tree split probablility", "-st", 0.1, (0.0,1.0), True, True)
        self._definition.Add("Mutation gaussian sigma", "-sp", 0.05, (0.0,1.0), True, True)
        
        self._definition.Add("Seed", "-s", 0, (0,MAX_INT), False, False)
        
        ## Evaluation specific parameters        
        self._definition.Add("Tournament size", "-t", 8, (1,100), False, False)
        self._definition.Add("Evaluation budget", "-me", 0, (0,MAX_INT), False, False)
        # This flag is set automatically if no seed are given in instance sets.
        # THIS FLAG DOES NOT WORK WITH THE CURRENT VERSION! (EVEN IF IT IS LISTED IN HELP)
        #self._definition.Add("Force random seed for instances", "-r", 0, (0,1), False, False)
        
        self._definition.Add("Instances/gen at the start", "-is", 0, (0,MAX_INT), False, False)
        self._definition.Add("Instances/gen at the end", "-ie", 0, (0,MAX_INT), False, False)
        self._definition.Add("Instances/gen end generation", "-gf", 0, (0,MAX_INT), False, False)
 
        ## Target algorithm parameter values
        self._definition.Add("Normalize continuous parameters", "-nc", 0, (0,1), False, False)
        self._definition.Add("Number of seeded genomes from defaults", "-sg", 0, (0,MAX_POP_SIZE), False, True)
        
        ## Other
        self._definition.Add("Verbosity", "-v", DEFAULT_VERBOSITY, (0,5), True, False)
        self._definition.Add("Timeout", "-c", 2147483647, (0,2147483647), True, False)
        # Usually defined in the algorithm wrapper, set to max
        self._definition.Add("Algorithm Timeout", "-tc", 2147483647, (0,2147483647), True, False) 
        
        self._definition.Add("Optimize objective function", "-out", 1, (0,0), True, False)
        
        
        # Omitted parameters
        
        ### in Pydoe Algorithm cutoff is enforced by the algorithm wrapper
        #-pe	penalty for reaching cutoff time per instance (performance[i] = penalty*cutoff)
        
        ### Use default learning stragety
        #-l	Specify a learning strategy. {0 = ALL, 1 = Linear (default), 2 = Step, 3 = Parabola, 4 = Exponential}
        #-lsd	Generation to start the learning strategy at. Until then -is instances will be used.
        #-lss	# Generations / step for the step strategy.
        
        ### Other
        #-config	Configuration is done using cmd line

    def getOutputLineRecognizer(self, key):
        if key=="ops":
            return GGATuner.reEvaluationRow
        elif key=="special":
            return GGATuner.reFinalRow
        else:
            raise KeyError("No such input line recognizer")
        
    def createAlgorithmParametersFile(self, configurationFilename, tunerParameters, ad ):
        
        if ad.HasParameter("Instance"):  
            instanceParameterName = ad.GetParameterSwitch("Instance")
        else:
            # Perhaps the algorithm does not support instances?
            instanceParameterName = None
            
        if ad.HasParameter("Seed"):
            seedParameterName = ad.GetParameterSwitch("Seed")
        else:
            seedParameterName = None

        
        fixedParameters = []
        for fp in ad.FixedParameters():
            if (fp==instanceParameterName) or (fp==seedParameterName):
                continue
            fixedParameters.append( fp ) 
            fixedParameters.append( str(ad.GetParameterDefault(fp)) ) 
        
        tunableParameterNames = dict()
        for tp in ad.TunableParameters():
            tunableParameterNames[tp]=tp.strip("-/ ")
        
        # Build the header (algorithm command definition)
        HEADER = """<algtune>\n"""
        cmdstring = """<cmd>"""
        cmdstring+=self._algorithm.GetCmd("{obj}") + " "
        if (instanceParameterName):
            cmdstring+=instanceParameterName + " $instance "
        # TODO: Disabled the seed because the <cmd> does not respect the -s $seed order
        #if (seedParameterName):
        #    cmdstring+=seedParameterName + " $seed "
        cmdstring+=" ".join(fixedParameters)
        cmdstring+=" $" + " $".join(tunableParameterNames.values())
        cmdstring+="""</cmd>\n\n"""
        
        MIDDLER = """<node type="and" name="root" start="0" end="0">\n"""
        FOOTER = """</node>\n</algtune>"""

        seedgenome = ""
        seedgenome+='''<seedgenome> <!-- Default parameters -->\n\t<variable name="root" value="0" />\n'''
        for sw in ad.TunableParameters():
            seedgenome+='\t<variable name="%s" value="%s" />\n' % \
                ( tunableParameterNames[sw], str( ad.GetParameterDefault(sw) ) )
        seedgenome+='</seedgenome>\n\n'

        paramstr = ""
        for sw in ad.TunableParameters():
            prng = ad.GetParameterRange(sw)
            if (len(prng)>0 and len(prng)<=2):
                paramstr += '\t<node type="and" name="%s" prefix="%s " start="%s" end="%s" />\n' % \
                    ( tunableParameterNames[sw], sw,  str(prng[0]), str(prng[-1]) )
            if (len(prng)>2):
                paramstr += '\t<node type = "and" name="%s" prefix="%s " categories = "%s" categorical = "true" />\n' % \
                    ( tunableParameterNames[sw], sw, ",".join( (str(p) for p in prng) ) )

            # TODO: After ParameterSetDefinition supports dependencies, add them

        # Glue it together
        f = open(configurationFilename,"w")
        f.write(HEADER + cmdstring + seedgenome + MIDDLER + paramstr + FOOTER )       
        f.close()
                    
    def CreateAlgorithmCommand(self, algoParamSet):
        # Build the tuner parameters as cmd line arguments
        cmdargs = list()
        instancesCount = len(self._training_instances)
        for (k,v) in algoParamSet.items():
            # These are flags
            if (k=="-out" or k=="-nc"  or k=="-r" ):
                if util.str2bool(str(v)):
                    cmdargs.append(k)
                    continue
            elif k=="-is" or k=="-ie":
                instancesAtStartOrEnd = int(v)
                if (instancesAtStartOrEnd<1):
                    v = 1
                if (instancesAtStartOrEnd>instancesCount):
                    v = instancesCount
            elif k=="-gf":
                generations = algoParamSet["-g"]
                saturationGeneration = int(v)
                if (saturationGeneration<1):
                    v = 1
                if (saturationGeneration>generations):
                    v = generations
            
            cmdargs.append(k)
            cmdargs.append(str(v))
        
        fullcmd = self._cmd + " " + TEMP_PARAMETERS_FILE \
            + " " + TEMP_INSTANCES_FILE + " "  + " ".join(cmdargs)
        return fullcmd
    
    def Tune(self, tunerParameterSet=None):
        if not tunerParameterSet:
            tunerParameterSet = self.GetDefinition().NewDefaultParameterSet()
        
        # GGA does not support instance file without seeds. Therefore if
        #  there is no seeds given for the instances, set instance seed to 0,
        #  for each, BUT enable -r flag that 
        #  forces the use of a different random seed on each evaluation.
        if self._training_instances and type(self._training_instances[0]) is str:
            onlyfiles = list(self._training_instances)
            self._training_instances = []
            for instancefile in onlyfiles:
                iseed = random.randint(0, MAX_INT)
                self._training_instances.append( (iseed, instancefile) )
            #tunerParameterSet['-r'] = 1
                
        return ExternalTuner.Tune(self, tunerParameterSet)    
        

    

# TODO: Implement cmd line interface (for metatuning)

""" Code that test the basic operation of the GGATuner """    
def test_basic():
    
    from Algorithms.GFEAlgorithm import GFEAlgorithm
    algo = GFEAlgorithm(10, 1)

    # Run random parameter tuner with defaults and with dummy algo
    tuner = GGATuner(PathManager.GetTuningBasePath()+"Tuners/gga")
    dps = tuner.GetDefinition().NewDefaultParameterSet()
    dps["-p"]=20
    dps["-g"]=14
    dps["-gf"]=14
    dps["-is"]=5
    dps["-ie"]=14
    
    #dps["-me"]=100
    
    dps["-t"]=8
    dps["-out"] = 1
    
    # Show all
    dps["-v"] = 5
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    tuner.SetAlgorithm(algo)
    instances = []
    for i in range(14):
        instance = PathManager.GetTuningBasePath()+"Benchmarks/gfe/f1_c/f1_c_%d.txt" % (i+1)
        instances.append(instance)
    tuner.SetInstances(instances)
    
    # Tune
    tuningResult = tuner.Tune(dps)
    print "Quality: " + str(tuningResult["obj"])
    print "Evaluations: " + str(tuningResult["ops"])
    print "Tuned parameters: " + str(tuningResult["special"])

def give_estimate(p = DEFAULT_P, g = DEFAULT_G, ist = 5, ie = 14, epgp = P_IN_G_EVAL_RATIO):  
    idelta = float(ie-ist)/(g-1)
    ipg = []
    for i in range(g):
        ipg.append(int(ist+idelta*(i)))
    
    #print "Instances per generation = " + str(ipg)
    epg = map(lambda ic : ic*(p*epgp), ipg )
    #print "Evaluations per generation = " + str(epg)
    te = sum(epg)
    return int(te)

def reverse_estimate_linear(evals = 1000, ist = 5, ie = 14):
    p = DEFAULT_P
    g = DEFAULT_G
    ratio = DEFAULT_P/float(DEFAULT_G)
    
    tp=p
    tg=g
        
    estimate = give_estimate(p, g, ist, ie)
    while (estimate>evals):
        p=tp
        g=tg
        
        tg = max(MIN_G, g-1)
        if (tg==MIN_G):
            tp = p-1
        else:
            tp = max(MIN_P, int(ratio*tg))
        
        estimate = give_estimate(tp, tg, ist, ie)
    return (p,g)
    
def reverse_estimate(evals = 1000, ist = 5, ie = 14):
    p = DEFAULT_P
    g = DEFAULT_G
    
    # Loop vars
    tp = p 
    tg = g
    decg = 1
    
    #Ansotegui used p=30 g=40 in tuning SAT, SAPS
    # p=50 g=100 for SPEAR
    # 
    
    while (tp>=MIN_P or tg>=MIN_G):
        e = give_estimate(tp, tg, ist, ie)
        if e < evals:
            # p,g have values just over evals 
            #print "found"
            break
        
        p = tp
        g = tg 
        
        if decg>0 and tg>=MIN_G:
            tg-=1
            decg-=1
        else:
            decg=1
            tp-=1
        
    return (p,g)

def test_reverse_estimate():
    # Tune GFE (type 1)
    from Algorithms.GFEAlgorithm import GFEAlgorithm
    algo = GFEAlgorithm(10, 1)
    INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/gfe/f1_c'
    INSTANCE_REQUIRED_EXT = ".txt"
    SAMPLES = 14
    
    # Sample instances from instance folder
    instancefiles = []
    for fn in os.listdir(INSTANCE_FOLDER):
        extension = os.path.splitext(fn)[1]
        if extension==INSTANCE_REQUIRED_EXT:
            instancefiles.append(os.path.join(INSTANCE_FOLDER, fn))
    random.shuffle(instancefiles)
    instances = instancefiles[0:SAMPLES]
    
    
    for evals in range(100, 10000, 100):
        if evals>500 and evals%500!=0:
            continue
        if evals>1000 and evals%1000!=0:
            continue
        if evals>5000 and evals%5000!=0:
            continue
        
        ist = min(5, SAMPLES)
        ien = SAMPLES
        
        p,g = reverse_estimate_linear(evals, ist, ien)
        
        tuner = GGATuner(PathManager.GetTuningBasePath()+"Tuners/gga")
        dps = tuner.GetDefinition().NewDefaultParameterSet()
        dps["-p"]=p
        dps["-g"]=g
        dps["-gf"]=g
        dps["-is"]=ist
        dps["-ie"]=ien
        dps["-me"]=evals
        dps["-t"]=8
        dps["-out"]=1
        #dps["-v"]=2
        
        tuner.SetAlgorithm(algo)
        tuner.SetInstances(instances)
        
        result = tuner.Tune(dps)
        
        print "target %d, actual %d, estimated P:%d G:%d" % (evals, result["ops"], p, g) 
    
    reverse_estimate(evals = 100, ist = 5, ie = SAMPLES)

def print_reverse_estimates():
    print "Total evaluations for p20,g20,is5,ie15 = " + str( give_estimate() )
    for evals in range(100, 10000, 100):
        if evals>500 and evals%500!=0:
            continue
        if evals>1000 and evals%1000!=0:
            continue
        if evals>5000 and evals%5000!=0:
            continue
        
        (p,g) = reverse_estimate_linear(evals, ist = 5, ie = 14)
        print "Target %s evals, P=%d, G=%d, ee=%d" % (evals, p, g, give_estimate(p, g, ist = 5, ie = 14))
    
if __name__ == '__main__':
    #import logging
    #logging.basicConfig(level=logging.DEBUG)
    
    #test_basic()
    #exit()
    
        
    test_reverse_estimate()
    