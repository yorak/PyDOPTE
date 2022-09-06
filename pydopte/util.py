# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 19:03:06 2011

@author: juherask
"""

import re

def first(iterable):
    return iterable.__iter__().next()
    
def split_ex(s, seps, skipEmpty=False):
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            if (skipEmpty):
                res += [x for x in seq.split(sep) if x]
            else:
                res += seq.split(sep)
    return res

def alphanum_key(s):   
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    
    def tryint(s):
        try:
            return int(s)
        except:
            return s        
    
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]
    
def natsort(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)

def replace_all(these, tothis, string):
    """ Replaces all substrings mentioned in the iterable to tothis
    from the string.
    """
    rets = string
    for this in these:
        rets = rets.replace(this, tothis)
    return rets

def str2bool(v):
    return v.lower() in ("true", "t", "1", )
    
def test_util():
    """ Simple tests to ensure that the utility functions work.
    """

        
    l = ["a 101","a1","a10","a2"]
    d = {"x 101":1,"x1":4,"x10":2,"x2":3}
    
    # Testing first
    assert first(l)=="a 101", "First item was not first!"
    
    # Testing natural sorting
    natsort(l)
    dk = d.keys()
    natsort(dk) 
    assert l==["a1","a2","a10","a 101"], "Not in natural order"
    assert dk==["x1","x2","x10","x 101"], "Not in natural order"
    
    s = "result: 12, a = 3"
    t1 = ["result","", "12", "", "a", "", "", "3"]
    t2 = ["result", "12", "a", "3"]
    assert t1==split_ex(s, [":", ",", " ", "="], skipEmpty=False)
    assert t2==split_ex(s, [":", ",", " ", "="], skipEmpty=True)

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    test_util()    
