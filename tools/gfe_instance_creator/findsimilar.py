# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
/home/jussi/.spyder2/.temp.py
"""

import os
import sys

# Implementation of Charikar simhashes in Python
# See: http://dsrg.mff.cuni.cz/~holub/sw/shash/#a1

def simhash(tokens, hashbits=32):
   if hashbits > 64: hashbits = 64
   v = [0]*hashbits

   for t in [x.__hash__() for x in tokens]:
       bitmask = 0
       for i in xrange(hashbits):
           bitmask = 1 << i
           if t & bitmask:
               v[i] += 1
           else:
               v[i] -= 1


   fingerprint = 0
   for i in xrange(hashbits):
       if v[i] >= 0:
           fingerprint += 1 << i

   return fingerprint



def similarity(a, b, hashbits=32):
   # Use Hamming Distance to return % of similar bits
   x = (a ^ b) & ((1 << hashbits) - 1)
   tot = 0
   while x:
       tot += 1
       x &= x-1
   return float(hashbits-tot)/hashbits

def print_usage():
    print "usage: python findsimilar.py <folder_for_recursive_scan> <ext1> <ext2> ..."
    
# List of extensions can be given as arguments
if len(sys.argv)<3:
    print_usage()
    exit()

exts = sys.argv[2:]

fileList = []
rootdir = sys.argv[1]
for root, subFolders, files in os.walk(rootdir):
    for file in files:
        filename = os.path.join(root,file)
        extension = os.path.splitext(filename)[1].lower()[1:]
        if extension in exts:
            fileList.append(os.path.join(root,file))

simList = []
for i in range(len(fileList)-1):
    for j in range(i+1,len(fileList)):
        f1_linestring = open(fileList[i], 'r').read()
        f2_linestring = open(fileList[j], 'r').read()
        f1_f2_sim = similarity(
            simhash(f1_linestring.split(), 64),
            simhash(f2_linestring.split(), 64) )
        simList.append( (f1_f2_sim, fileList[i], fileList[j] ) )

simList.sort(reverse=True)
for li in simList:
    print(li)



