# -*- coding: utf-8 -*-

MAX_INT = 2147483647 #operate in 32 bit, sys.maxint
MAX_FLOAT = 1.7976931348623157e+308 #operate in 32 bit, sys.float_info.max
MIN_FLOAT = 2.2250738585072014e-308 #operate in 32 bit, sys.float_info.min
    
def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True
        
if module_exists("scipy"):
    import scipy
        
def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))
    
def median_idxs(l):
    N = len(l)
    sl = zip(l, range(N))
    sl.sort()   
    if N%2==0:
        return [sl[(N-1)/2][1], sl[N/2][1]]
    else:
        return [sl[(N-1)/2][1]]

def str2bool(v):
    result = None
    if v.lower() in ("yes", "true", "t", "1"):
        result = True
    if v.lower() in ("no", "false", "f", "0"):
        result = False
    return result
    
def median(l):
    midxs = median_idxs(l)
    return sum((l[i] for i in midxs))/float(len(midxs))
    
def dictHash(d):
    """Calculate a hash value for a dictinoary
    """
    dh = 0
    for sw,value in d.items():
        # Reset seed and isntance info
        #if sw == "-i" or sw == "-f" or sw == "-s":
        #    value = ""
        dh |= hash(sw) & hash(value)
    return dh
    
def line_y((x1,y1), (x2,y2), x):
    dx=x2-x1
    dy=y2-y1
    m=dy/dx    #slope
    y = m*(x-x1)+y1
    return y
    
def remove_outliers(lval, nsigma=10.0, useMedian=False):
    if useMedian:    
        med = median(lval)
        madl = [abs(val-med) for val in lval]
        mad = median(madl)
    else:
        med = scipy.mean(lval)
        mad = scipy.std(lval)
    return [val for val in lval if abs(med-val)<nsigma*mad]  

def list_Z_outliers(lval, nsigma=10.0):
    med = stats.mean(lval)
    msd = stats.stdev(lval)
    return [val for val in lval if abs(med-val)>nsigma*msd]  

def list_IH_outliers(lval, multiplier=1.0):
    """Iglewicz and Hoaglin outliers"""
    med = median(lval)
    madl = [abs(val-med) for val in lval]
    mad = median(madl)
    return [val for val in lval if (0.6745*abs(med-val)/mad)>multiplier*3.5]  
    
    
