'''
Created on Aug 17, 2011

@author: jussi
'''
import unittest

import PathManager
import VRPSDAlgorithms
from TestAlgorithm import TestAlgorithm


class TestVRPSDAlgorithms(TestAlgorithm):

    def setUp(self):
        VRPSD_PATH = PathManager.GetTuningBasePath()+"Solvers/VRPSD/bin"
           
        self.algorithms = [
            VRPSDAlgorithms.VRPSD_ACS_Algorithm(VRPSD_PATH),
            VRPSDAlgorithms.VRPSD_EA_Algorithm(VRPSD_PATH),
            VRPSDAlgorithms.VRPSD_FR_Algorithm(VRPSD_PATH),
            VRPSDAlgorithms.VRPSD_ILS_Algorithm(VRPSD_PATH),
            VRPSDAlgorithms.VRPSD_SA_Algorithm(VRPSD_PATH),
            VRPSDAlgorithms.VRPSD_TS_Algorithm(VRPSD_PATH),
        ]
        
        VRPSD_BENCHMARKS = [PathManager.GetTuningBasePath()+"Benchmarks/VRPSD/rcn050.f04.d50.r50.s05551.vrpsd"]
        
        self.benchmarks = [
            VRPSD_BENCHMARKS,
            VRPSD_BENCHMARKS,
            VRPSD_BENCHMARKS,
            VRPSD_BENCHMARKS,
            VRPSD_BENCHMARKS,
            VRPSD_BENCHMARKS,
        ]
        
if __name__ == '__main__':
    unittest.main()
