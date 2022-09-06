'''
Created on Aug 17, 2011

@author: jussi
'''
import unittest

import PathManager
import GuessValuesAlgorithm
import GFEAlgorithm
from TestAlgorithm import TestAlgorithm
from os import path


class TestBuiltinAlgorithms(TestAlgorithm):

    def setUp(self):
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        self.algorithms = [
            GuessValuesAlgorithm.GuessValuesAlgorithm(10, int),
            GFEAlgorithm.GFEAlgorithm(10, 1) # Have to give the the # of parameters
             ]
        
        SILLY_BENCHMARK = [path.join(PathManager.GetTuningBasePath(),r"Benchmarks/guess/i10/01.txt")]
        GFEA_BENCHMARK = [path.join(PathManager.GetTuningBasePath(),r"Benchmarks/gfe/f1_c/f1_c_1.txt")]
        
        self.benchmarks = [
            SILLY_BENCHMARK,
            GFEA_BENCHMARK
        ]

if __name__ == '__main__':
    unittest.main()
