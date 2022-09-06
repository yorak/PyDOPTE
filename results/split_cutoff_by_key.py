# -*- coding: utf-8 -*-
"""
Created on Tue Dec 08 13:42:00 2015

@author: juherask
"""

from os import path

inf = file(r"C:\Users\juherask\Dissertation_TODO_SORT\Phases\Tuning\Utils\Pydoe\Results\cutoff_tests-7717.csv", "r")

outfs = {}
outfsc = {}
for l in inf.readlines():
    pts = l.strip().split(";")
    
    if len(pts)<3:
        continue
    
    if len(pts)!=8:
        print "warning, malformed line :", l
    
    label = pts[0]
        
    if not label in outfs:
        outf_path = path.join(r"C:\Users\juherask\Dissertation_TODO_SORT\Phases\Tuning\Utils\Pydoe\Results\cutoff_tests", label+".csv")
        outf = file(outf_path, "w")
        outfs[label] = outf
        outfsc[label] = 0
        
    outfs[label].write(l)
    outfsc[label]+=1
    
for outf in outfs.values():
    outf.close()
    
for k,v in outfsc.items():
    print k, v
    
inf.close()