# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 17:45:54 2011

@author: jussi
"""

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





test_set = ["zomg hai 2 u 2! I lub j00 so hard.",

           "zomg bai 2 u 2? I haet j00 hard.",

           "G fj sdlfjdjlfjsljdf sdkfj s sla r",

           "g fJ sdlfjdjlfjsljdf sdkfj s sla r",

           "wainscoating",]



last = None

for t in test_set:

   fingerprint = hex(simhash(t.split()))

   print "%35s = %s" % (t, fingerprint)



print "\nHow similar are these?"

a = 'aaaaaaaaaaaaa 111111111111111'

b = 'aaaabaaaaaaaa 111111161111111'

print "'%s' and '%s'? %.2f%%" % ( a, b, similarity(simhash(a), simhash(b))*100 )

a = 'The Pursuit of HAPPINESS'

print "'%s' and '%s'? %.2f%%" % ( a, b, similarity(simhash(a), simhash(b))*100 )

b = 'the pursuit of happiness'

print "'%s' and '%s'? %.2f%%" % ( a, b, similarity(simhash(a), simhash(b))*100 )

b = 'HAPPINESS pursuit'

print "'%s' and '%s'? %.2f%%" % ( a, b, similarity(simhash(a), simhash(b))*100 )

b = 'happiness pursuit'

print "'%s' and '%s'? %.2f%%" % ( a, b, similarity(simhash(a), simhash(b))*100 )

b = 'happiness pursuit of the WHATEVER'

print "'%s' and '%s'? %.2f%%" % ( a, b, similarity(simhash(a), simhash(b))*100 )
