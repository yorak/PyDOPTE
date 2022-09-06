# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 19:09:56 2013

@author: juherask
"""


def read_csv(f):
    rows = []
    rf = open(f)
    header = None
    for line in rf.readlines():
        parts = line.split(";")
        parts = [p.strip() for p in parts]
        if len(parts)>1:
            if not header:
                header = parts
            else:
                rows.append( parts )
    rf.close()
    return header, rows
    
mainfile = "tunerperformance_cat.csv"
joinleft = "solverranks_cat.csv"
joinright = "tunerfeatures.csv"

mheader, mrows = read_csv(mainfile)
lheader, lrows = read_csv(joinleft)
rheader, rrows = read_csv(joinright)

ljoinh = mheader[0]
rjoinh = mheader[-1]

JOINL = True
JOINR = False
SEP = ','

USE_FIELD_TRANSLATORS = False

FIELD_TRANSLATORS = {
'Difficulty':{'1':'easy','2':'bizarre','3':'hard' },
'numParam':{'0':'none','1':'few','2':'some','3':'many' },
'numBoolParam':{'0':'few/none','1':'many'},
'numIntParam':{'0':'few/none','1':'many'},
'numRealParam':{'0':'few/none','1':'many'},
}



#output joined header
if JOINL and JOINR:
    print SEP.join(lheader+mheader[1:]+rheader[1:])
elif JOINL:
    print SEP.join(lheader+mheader[1:])
elif JOINR:
    print SEP.join(mheader+rheader[1:])
else:
    print SEP.join(mheader)
    
for mrow in mrows:
    lmatchrow = None
    rmatchrow = None
    
    ljoinkey = mrow[0]
    matchidx = lheader.index(ljoinh)
    
    if JOINL:
        for lrow in lrows:
            if lrow[matchidx]==ljoinkey:
                lmatchrow = lrow
                break
        if lmatchrow==None:
            print "Error: No match for key",ljoinkey
        
    if JOINR:
        rjoinkey = mrow[-1]
        matchidx = rheader.index(rjoinh)
        for rrow in rrows:
            if rrow[matchidx]==rjoinkey:
                rmatchrow = rrow
                break
        if rmatchrow==None:
            print "Error: No match for key",ljoinkey    
        
    #output joined row
    if USE_FIELD_TRANSLATORS:
        for i in range(len(mheader)):
            if mheader[i] in FIELD_TRANSLATORS:
                mrow[i] = FIELD_TRANSLATORS[mheader[i]][mrow[i]]
        for i in range(len(lheader)):
            if lheader[i] in FIELD_TRANSLATORS:
                lmatchrow[i] = FIELD_TRANSLATORS[lheader[i]][lmatchrow[i]]
        for i in range(len(rheader)):
            if rheader[i] in FIELD_TRANSLATORS:
                rmatchrow[i] = FIELD_TRANSLATORS[rheader[i]][rmatchrow[i]]
                
    if JOINL and JOINR:
        print SEP.join(lmatchrow+mrow[1:]+rmatchrow[1:])
    elif JOINL:
        print SEP.join(lmatchrow+mrow[1:])
    elif JOINR:
        print SEP.join(mrow+rmatchrow[1:])
    else:
        print SEP.join(mrow)
    
