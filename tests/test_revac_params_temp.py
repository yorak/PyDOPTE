# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 20:36:07 2011

@author: juherask
"""

I = 14

for evaluations in range(100, 1100, 100):
        
    M = max(4, int(evaluations/(I*11)+0.5))
    N = max(2, int(M/2+0.5))
    H = max(2, int(N/10+0.5))
    
    G = (evaluations-M*I)/I
    print "E=%d"%evaluations, "M=%d"%M, "N=%d"%N, "H=%d"%H, "G=%d"%G
    