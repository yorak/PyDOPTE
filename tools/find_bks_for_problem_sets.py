# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 10:50:37 2013

@author: juherask
"""

import glob

def calc_best_known(folder):
    totalbest = 0.0
    for fn in glob.glob(folder):
        f = open(fn, 'r')
        best = 100000000000000        
        for line in f.readlines():
            if "best_known" in line.lower():
                best = float( line.split(":")[1] )
                break
        print fn, best
        totalbest+=best
    return totalbest
    
def main():
    datasets = {
    'augerat_a_folder':r"""C:\MyTemp\juherask\Dissertation\Phases\Tuning\Benchmarks\Augerat\A\14\*.vrp""",
    'augerat_b_folder':r"""C:\MyTemp\juherask\Dissertation\Phases\Tuning\Benchmarks\Augerat\B\14\*.vrp""",
    'christofides_folder':r"""C:\MyTemp\juherask\Dissertation\Phases\Tuning\Benchmarks\Christofides\*.vrp""",
    }
    
    for k,v in datasets.items():
        print k, calc_best_known(v)
    
    
if __name__ == "__main__":
    main()
    #cvrp_we_to_testset()
