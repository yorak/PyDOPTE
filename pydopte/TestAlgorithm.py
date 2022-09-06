'''
Created on Aug 17, 2011

@author: jussi
'''
import unittest
import subprocess
import time

from ParameterSet import MAX_FLOAT, MAX_INT
import logging
import re
from BaseAlgorithm import reFmtVar, toFmtVar
import random

class TestAlgorithm(unittest.TestCase):
    """All the algorithms share the same functionality, so testing
    of that functionality is implemented here. To derive this and
    set up the self._algorithms and self._benchmarks ( 
    """
    def setUp(self):
        self.algorithms = [] #A list of tested algorithms
        self.benchmarks = [] #A list of benchmarks to test the corresponding algorithm with

    def shared_call_for_all(self, testFuncDesc, testFuncToCall):
        for i in range(len(self.algorithms)):
            algo = self.algorithms[i]
            benchmarks = self.benchmarks[i]
            
            print "\n" + testFuncDesc + " " + algo.__class__.__name__
            
            defaults = algo.GetDefinition().NewDefaultParameterSet()
            
            for benchmark in benchmarks:
                
                apsd = algo.GetDefinition()
                
                if apsd.HasParameter( "Instance" ):
                    isw = apsd.GetParameterSwitch("Instance")
                    defaults[isw]=benchmark
                    
                if apsd.HasParameter( "Seed" ):
                    ssw = apsd.GetParameterSwitch("Seed")
                    defaults[ssw]=random.randint(0, MAX_INT)
                
                # Run the test
                testFuncToCall(algo, defaults)
                    
            
    def test_cmdline(self):
        # A closed function to call for each tested algorithm and parameter set combination
        def testCmdLineFunc(algo, ps):
            algo.SetTimeLimit("1.0") # Just check that the call goes trough
            full_wrapper_cmd = algo.GetCmd() + " " + " ".join( (str(k)+" "+str(v) for k,v in ps.items()) )
            #fullcmd = algo.CreateAlgorithmCommand(ps)
            
            print full_wrapper_cmd
            
            proc = subprocess.Popen([ full_wrapper_cmd ], \
                shell=True, \
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            output = proc.communicate()
            
            print ("Raw output=%s" % output[0])
            
            if (proc.returncode!=0):
                logging.debug(output[0])
                logging.debug(output[1])
            
            self.assertTrue(proc.returncode==0, "Wrong returncode, expected 0, got %d"%proc.returncode)
            self.assertTrue(output[0]!=None)
        
        # Call closed function for all algorithms and all benchmarks
        self.shared_call_for_all("Testing cmdline for algorithm", testCmdLineFunc)
            
    def test_timeouting(self):
        # A closed function to call for each tested algorithm and parameter set combination
        def testTimeoutFunc(algo, ps):
            algo.SetTimeLimit(5.0)
            start = time.time()
            value = algo.Evaluate(ps)["obj"]
            wt =  time.time() - start   
            print "Value=%f" % value
            print wt, "seconds wall time"
            
            self.assertTrue(value<MAX_FLOAT) # Just to check we have a result
            self.assertTrue(wt-7.0<0.0) # 2 sec tolerance
        
        # Call closed function for all algorithms and all benchmarks
        self.shared_call_for_all("Testing timeout for algorithm", testTimeoutFunc)             
   
    def test_tunable_range_ends(self):    
        # A closed function to call for each tested algorithm and parameter set combination
        def testRangeEndsFunc(algo, ps):
            apsd = algo.GetDefinition()
            
            algo.SetTimeLimit(5.0)
            
            maxps = dict(ps.items())
            minps = dict(ps.items())
            
            for sw in apsd.TunableParameters():
                prange =  apsd.GetParameterRange(sw)
                if len(prange)>0:
                    maxps[sw] = prange[-1]
                    minps[sw] = prange[0]
            
            #import logging
            #logging.basicConfig(level=logging.DEBUG)

            # Just check that is is OK to call on the range ends
            value_on_max = algo.Evaluate(maxps)["obj"]
            value_on_min = algo.Evaluate(minps)["obj"]
            
            print "On max parameters: %f  abd on min parameters: %f"%(value_on_max, value_on_min)

        # Call closed function for all algorithms and all benchmarks
        self.shared_call_for_all("Testing parameter ranges for algorithm", testRangeEndsFunc)              
                    
    def test_cmdline_outputformat(self):
        """test to test output formatting of an algorithm.
        The obj and time should always be valid""" 
       
        def makeTestOuputFormatFunc(closedOutputFormat):
            # outputFormat is "closed" in the definition of inc
            # A closed function to call for each tested algorithm and parameter set combination
            def testOuputFormatFunc(algo, ps):
                algo.SetTimeLimit("1.0") # Just check that the call goes trough
                fullcmd = algo.GetCmd(outputFormat=closedOutputFormat) + \
                    " " + " ".join( (str(k)+" "+str(v) for k,v in ps.items()) )
                print fullcmd
                
                proc = subprocess.Popen([ fullcmd ], \
                    shell=True, \
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                output = proc.communicate()
                
                print ("test_cmdline_outputformat raw output = %s" % output[0])
                
                if (proc.returncode!=0):
                    logging.debug(output[0])
                    logging.debug(output[1])
                
                self.assertTrue(ore.match(output[0])!=None, fullcmd+" Produced not right output (was=" +output[0]+" expected="+ore.pattern+")" )
        
            return testOuputFormatFunc
        
        validOfmt = "obj:{obj} ; seed:{seed} ; operations={ops} ; elapsed time={time};"
        invalidOfmt = "obj={obj},foo={bar}"
        ore = re.compile("obj:[0-9]+\.[0-9]+ ; seed:-?[0-9]+ ; operations=[0-9]+ ; elapsed time=[0-9]+\.[0-9]+;")
        
        testValidOuputFormatFunc = makeTestOuputFormatFunc(validOfmt) 
        self.shared_call_for_all("Testing valid cmdline outputformat for algorithm", testValidOuputFormatFunc)
        
        
        testInvalidOuputFormatFunc = makeTestOuputFormatFunc(invalidOfmt)
        # This should fail
        if len(self.algorithms)>0:
            self.assertRaises(AssertionError, self.shared_call_for_all, "Testing invalid cmdline outputformat for algorithm (should fail)", testInvalidOuputFormatFunc)
                
    def test_inputformat(self):
        def makeTestInputFormatFunc(closedInputFormat):
            
            # A closed function to call for each tested algorithm and parameter set combination
            def testInputFormatFunc(algo, ps):
                algo.SetTimeLimit("1.0") # Just check that the call goes trough
                apsd = algo.GetDefinition()
                
                inputFormatPs = []
                normalPs = []
                
                cif = str(closedInputFormat)
                
                if cif=="":
                    psl = ps.items()
                    halfway = len(psl)/2
                    
                    inputFormatPs = psl[:halfway]
                    normalPs = psl[halfway:]
                    
                    for ip in inputFormatPs:
                        pdesc = apsd.GetParameterDescription(ip[0])
                        cif += toFmtVar(pdesc) + " "
                    cif.strip()
                else:
                    fmtVals = reFmtVar.findall(cif)
                    
                    for fmt in fmtVals:
                        if (fmt!=""):
                            if apsd.HasParameter( fmt ):
                                isw = apsd.GetParameterSwitch( fmt )
                                iv = ps[isw]
                            else:
                                # It is ignored
                                cif = cif.replace(fmt, "")
                                isw = ""
                                iv = 101 #dummy, will be ignored
                        else:
                            isw = ""
                            iv = 101 #dummy, will be ignored
                            
                        inputFormatPs.append( (isw, iv) )
                    for p in ps.items():
                        if not p in inputFormatPs:
                            normalPs.append(p)
                    
                # Unzip to switches and values
                ifpSw, ifpVal  = zip(*inputFormatPs)
                
                fullcmd = algo.GetCmd(inputFormat=cif) + " " + \
                    " ".join( (str(ipv) for ipv in ifpVal) ) + \
                    " " + " ".join( (str(k)+" "+str(v) for k,v in normalPs) )
                print fullcmd
                
                proc = subprocess.Popen([ fullcmd ], \
                    shell=True, \
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                output = proc.communicate()
                
                print ("Raw output = %s" % output[0])
                
                if (proc.returncode!=0):
                    logging.debug(output[0])
                    logging.debug(output[1])
                
                self.assertTrue(proc.returncode==0)
                self.assertTrue(output[0]!=None)
                
                return output[0]
            
            return testInputFormatFunc

        basicIf = makeTestInputFormatFunc("{Instance} {} {} {} {Seed}")
        halfIf = makeTestInputFormatFunc("") # This uses 1/2 of the params as forced inputs
        
        basicRes = self.shared_call_for_all("Testing cmdline inputformat for algorithm", basicIf)
        halfRes = self.shared_call_for_all("Testing cmdline inputformat for algorithm", halfIf)
        
        # Call closed function for all algorithms and all benchmarks
        self.assertTrue( basicRes == halfRes )
