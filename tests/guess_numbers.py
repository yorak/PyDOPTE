#!/usr/bin/env python
from os import path
from sys import argv

#clog = open("call_log.txt", "wa")
#clog.write( " ".join(argv) +  "\n" )
#print 0.0
#exit()

def print_help():
  print r"""
Usage: guess_numbers.py /path/to/problem/file.txt -x0 1 -x1 0 -x2 1 ...

Prints out the sum of differences to the correct numbers in the problem file.
The problem file has only one line of format '0 1 0 ...' specifying
the correct numbers.

The numbers can be:
  0/1 (booleans)
  0-N (integers)
  0.0-N.N (floats)
"""

i = 1
T = []
guess = {}
seed = 0
while i<len(argv):
  if argv[i] in ("-h", "--help"):
    print_help()
    exit()
  if argv[i][0]=="-":
    #print "switch", argv[i]
    id = int( argv[i].strip().replace("-x","") )
    try:
      guess[id] = int(argv[i+1])
    except ValueError:
      guess[id] = float(argv[i+1])
    i+=1
  elif path.isfile(argv[i]):
    problemfile = open(argv[i])
    parts = problemfile.readline().split()
    problemfile.close()
    try:
      T = list( int(s) for s in parts )
    except ValueError:
      T = list( float(s) for s in parts )
    seed = argv[i+1]
    i+=1
  else:
    print "ERROR: invalid parameter", argv[i]
    print_help()
    exit()
  i+=1
if i==1:
  print_help()
  exit()

q = 0
if len(T)==len(guess):
  for i,v in enumerate(T):
    if i in guess:
      if v!=guess[i]:
        q+=abs(v-guess[i])
    else:
      print "ERROR: value not specified for the variable x%d" % i
else:
  print "ERROR: not enough values for the problem"
print q