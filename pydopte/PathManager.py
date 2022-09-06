import os
from sys import argv

def GetTuningBasePath():
    defaultTuningRoot = "./" 
    abspath = os.path.abspath(argv[0])
    
    # Walk upwards in tree until we find a folder called Tuning
    prevpath = ""
    while abspath!=prevpath:
        if os.path.basename(abspath)=="Tuning":
            defaultTuningRoot = abspath
            break
        prevpath = abspath
        abspath = os.path.dirname(abspath)
        
    
    # Can be owerridden with this
    tuningRoot = os.environ.get("TUNING_ROOT", defaultTuningRoot)
    
    # Make sure we have the trailing / or \ right
    return os.path.normpath(tuningRoot) + os.sep

def GetExternalExecutablePath(className):
    
    """
    
    """
    pass
    # TODO: Write later to make configuring paths possible
    