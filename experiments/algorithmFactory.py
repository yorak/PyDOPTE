import experiment_template
from Algorithms.VRPHAlgorithms import *
from Algorithms.VRPSDAlgorithms import *
from Algorithms.GFEAlgorithm import GFEAlgorithm
from Algorithms.GuessValuesAlgorithm import GuessValuesAlgorithm, KNOWN_TYPES
import PathManager

def PrintSupported():
    for algo in GetSupported():
        print algo;
    
def GetSupported():
    return [ #christofides
             'vrph_rtr_c',
             'vrph_sa_c',
             'vrph_ej_c',
             # 4 pcs realword instances from fischer (3) + taillard (1)
             # instance id may be one of "F-n45", "F-n72", "F-n135", "RT_385"
             'vrph_rtr_rw[_<instance_id>][_testset]', 
             'vrph_sa_rw[_<instance_id>][_testset]',
             'vrph_ej_rw[_<instance_id>][_testset]',
             #augerat
             'vrph_rtr_a[_testset]', 
             'vrph_sa_a[_testset]',
             'vrph_ej_a[_testset]',
             #IRIDIA
             'vrpsd_acs[_testset]',
             'vrpsd_ea[_testset]',
             'vrpsd_fr[_testset]',
             'vrpsd_ils[_testset]',
             'vrpsd_sa[_testset]',
             'vrpsd_ts[_testset]',
             'gfe',
             'guess[_b|_i|_f[<N>]]']

def BuildAlgorithm(mh):
     
    algo = None
    
    if "vrph_" in mh:
        vrph_path = PathManager.GetTuningBasePath()+"Solvers/VRPH/bin"
        
        if "_c" in mh:
            INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/Christofides/'
        elif "_rw" in mh:
            complement_set = ""
            if "_testset" in mh:
                complement_set = "'"
            if "f-n45" in mh:
                INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/Realworld/F-n45%s/' % complement_set
            elif "f-n72" in mh:
                INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/Realworld/F-n72%s/' % complement_set
            elif "f-n135" in mh:
                INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/Realworld/F-n135%s/' % complement_set
            elif "rt_385" in mh or "rt-385" in mh:
                INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/Realworld/RT_385%s/' % complement_set
            else:
                INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/Realworld/All/'
        elif "_a" in mh:
            if "_testset" in mh:
                INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/Augerat/B/14/'
            else:
                INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/Augerat/A/14/'
        else:
            raise Exception(mh +": no such tuning target metaheuristic")
    
        INSTANCE_REQUIRED_EXT = ".vrp"
        
        if ("_rtr" in mh):
            algo = VRPH_RTR_Algorithm(vrph_path)
        elif ("_sa" in mh):
            algo = VRPH_SA_Algorithm(vrph_path)
        elif ("_ej" in mh):
            algo = VRPH_EJ_Algorithm(vrph_path)
        else:
            raise Exception(mh +": No such vrph metaheuristic")
    
    if "vrpsd_" in mh:
        vrpsd_path = PathManager.GetTuningBasePath()+"Solvers/VRPSD/bin"
        
        if "_testset" in mh:
            INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/VRPSD/14test'
        else:
            INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/VRPSD/14'
                

        INSTANCE_REQUIRED_EXT = ".vrpsd"
    
        if ('vrpsd_acs' in mh) or ('vrpsd_aco' in mh):
            algo = VRPSD_ACS_Algorithm(vrpsd_path)
        elif ('vrpsd_ea' in mh):
            algo = VRPSD_EA_Algorithm(vrpsd_path)
        elif ('vrpsd_fr' in mh):
            algo = VRPSD_FR_Algorithm(vrpsd_path)
        elif ('vrpsd_ils' in mh):
            algo = VRPSD_ILS_Algorithm(vrpsd_path)
        elif ('vrpsd_sa' in mh):
            algo = VRPSD_SA_Algorithm(vrpsd_path)
        elif ('vrpsd_ts' in mh):
            algo = VRPSD_TS_Algorithm(vrpsd_path)
        else:
            raise Exception(mh +": No such vrpsd metaheuristic")
    
    if mh=="gfe":
        algo = GFEAlgorithm(10, 1)
        INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/gfe/f1_14/'
        INSTANCE_REQUIRED_EXT = '.txt'
        
    if "guess_" in mh:
        parts = mh.split("_")
        var_type = int
        num_var = 1        
        stype = "i"
        if len(parts)==2:
            _,stype = parts 
        if len(stype)>1:
            num_var = int(stype[1:])           
            var_type = KNOWN_TYPES[stype[0]]
        
        algo = GuessValuesAlgorithm(num_var,var_type)
        INSTANCE_FOLDER = PathManager.GetTuningBasePath()+'Benchmarks/guess/%s%d/'%(stype[0],num_var)
        INSTANCE_REQUIRED_EXT = '.txt'
    
    if not algo:
        raise Exception("Invalid algorithm")
    
    instances = experiment_template.CreateInstanceList(INSTANCE_FOLDER, INSTANCE_REQUIRED_EXT)
    
    return (algo, instances)
