'''
Created on Aug 17, 2011

@author: jussi
'''

import unittest

import PathManager
import VRPHAlgorithms
from TestAlgorithm import TestAlgorithm


class TestVRPHAlgorithms(TestAlgorithm):

    def setUp(self):
        VRPH_PATH = PathManager.GetTuningBasePath()+"Solvers/VRPH/bin"
           
        self.algorithms = [
            VRPHAlgorithms.VRPH_SA_Algorithm(VRPH_PATH),
            VRPHAlgorithms.VRPH_RTR_Algorithm(VRPH_PATH),
            VRPHAlgorithms.VRPH_EJ_Algorithm(VRPH_PATH)
        ]
        
        VRPH_BENCHMARKS = [PathManager.GetTuningBasePath()+"Benchmarks/Christofides/Christofides_01.vrp"]
        
        self.benchmarks = [
            VRPH_BENCHMARKS,
            VRPH_BENCHMARKS,
            VRPH_BENCHMARKS
        ]
        
if __name__ == '__main__':
    import logging
    import time;  # This is required to include time module.
    ticks = time.time()
    logging.basicConfig(level=logging.DEBUG, filename='vrph_test_debug'+str(ticks)+'.log')
    unittest.main()
