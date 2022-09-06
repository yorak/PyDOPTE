""" Just simple test script to test the tuning out """

import os
import random
import sys
from util import is_integer
import algorithmFactory
import logging
import time

def makeStratifiedKFolds(instances, k, rng_seed):
    """ Disribute instances into k folds using statified sampling. 
    (we assume this makes statification by instance size happen.
    Bigger file => bigger problem instance)"""
    
    #WARN WARN WARN. Fo
    
    # Get file sizes and sort instances by them
    fsizes = []
    for instance in instances:
        if isinstance(instance, str) or isinstance(instance, unicode):
            fsizes.append( os.path.getsize(instance) ) 
        elif isinstance(instance[0], str) or isinstance(instance[0], unicode):
            fsizes.append( os.path.getsize(instance[0]) ) 
    size_instances = zip(fsizes, instances)
    size_instances.sort()
    
    # Generate folds by allocating each approximately similarly sized
    #  groups to folds in random order.
    random.seed(rng_seed);
    print "STATIFIED FOLD SAMPLING WITH SEED", rng_seed
    folds = [[] for i in range(k)]
    for fi_start in range(0, len(size_instances), k):
        fold_targets = range(k)
        random.shuffle(fold_targets) # in place
        for fi in range(k):
            if (fi_start+fi<len(size_instances)):
                instance = size_instances[fi_start+fi][1];
                target_fold = fold_targets[fi]
                folds[target_fold].append( instance )
    #print folds
    return folds


def CreateInstanceList(instanceFolder, instanceExtension, samples = None):
    # Sample instances from instance folder
    instancefiles = []
    for fn in os.listdir(instanceFolder):
        extension = os.path.splitext(fn)[1]
        if extension==instanceExtension:
            instancefiles.append(os.path.join(instanceFolder, fn))
    
    if (samples):
        random.shuffle(instancefiles)
        sampledfiles = instancefiles[0:samples]
        return sampledfiles
    else:
        return instancefiles

    
def RunExperiment(algorithm, instances, tuner, tunerParameters, repetitions, verbosity, k_folds, rng_seed_override):
    
    # Define tuning task
    tuner.SetAlgorithm(algorithm)
    if not k_folds or k_folds==1:
        tuner.SetInstances(instances)
    
    tpd = tuner.GetDefinition()
    tunerSeedSwitch = None
    if tpd.HasParameter("Seed"):
        tunerSeedSwitch = tpd.GetParameterSwitch("Seed") 
        #print "DEBUG:", seedSwitch
    
    
    for repi in range(repetitions):
        if (rng_seed_override):
            seed = repi+rng_seed_override
        else:            
            seed = repi+1
        random.seed(seed)

        # Use the same seed for the tuner
        if (tunerSeedSwitch):
            tunerParameters[tunerSeedSwitch]=seed

        print "%s tuning %s, iteration %d (of %d), seed %d, with parameters: %s" % \
            ((tuner.__class__.__name__), (algorithm.__class__.__name__), repi+1, repetitions, seed, str(tunerParameters) )
        print 
            

        # k-fold cross validation        
        if k_folds>1:
            folds = makeStratifiedKFolds(instances, k_folds, seed)
            for fi, fold in enumerate(folds):
                not_fold = [i for kfold in folds if kfold!=fold for i in kfold]

                print "%d/%d fold" % (fi+1, k_folds)
                
                tuner.SetInstances(not_fold,fold)
                tuningResult = tuner.Tune(tunerParameters)                
                
                print "Quality: " + str(tuningResult["obj"])
                print "Evaluations: " + str(tuningResult["ops"])
                print "Tuned parameters: " + str(sorted(tuningResult["special"].items()))
                print
                print
            
        else:
            # Try tuning, catching allows failures
            #try:
            tuningResult = tuner.Tune(tunerParameters)
            print "Quality: " + str(tuningResult["obj"])
            print "Evaluations: " + str(tuningResult["ops"])
            print "Tuned parameters: " +  str(sorted(tuningResult["special"].items()))
            #except Exception as e:
            #    print e
            print
            print
        
def PrintHelp():
    print "usage: python experiment.py <algo_id> <repetitions> <evaluations> [-v[f] <level>] [-k <folds>] [-rs <random_seed>]"
    print "<repetitions> defines how many tuning runs to run on a stochastic target"
    print "-v optional v turns on verbose output"
    print "-vf writes that verbose output to a log file"
    print "-k specifies how many fold cross validation to do"
    print "-rs seed for RNG. By default, repetition number is used as a tuner and fold generation random seed. -rs overrides this."
    print "and where <algo_id> is one of:"
    algorithmFactory.PrintSupported()
    exit()
        
def ExperimentFromCmdLine(experiment_argv, setup_and_run_experiment_function):
    """
    Give sys.argv and the function that sets the experiment up and runs it.
    The (quite complex) experiment call chain is:
    
    # just pass the argv
     Experiment.__main__() -> 
    # parse argv and let experiment to setup
     template.ExperimentFromCmdLine(...) ->
    # setup algo and tuner (function passed with setup_and_run_experiment_function)
     Experiment.SetupAndRunExperiment(...) ->
    # run the experiment
     template.RunExperiment(...) -> 
    # individual tunings
     Tuner.Tune(...)
    
    """
    CUTOFF = 10.0
    
    if len(experiment_argv)<4 or \
       not is_integer(experiment_argv[2]) or\
       not is_integer(experiment_argv[3]):
        PrintHelp()
        
        
    algo_id = experiment_argv[1]
    repts = int(experiment_argv[2])
    evals = int(experiment_argv[3])
    
    random_seed_override = None    
    verbosity = None
    k_folds = 1
    for i in range(4,len(experiment_argv), 2):
        switch = experiment_argv[i]
        swval = int(experiment_argv[i+1])
        
        if switch=="-v" or switch=="-vf":
            verbosity = int( swval )
            if verbosity > 0:
                logging.basicConfig(level=logging.DEBUG)
                
            if switch=="-vf":
                # Negative verbosity is logging to file
                verbosity = -abs(verbosity)
                
                # Negative verbosity means logging to a logfile
                tuner_name = experiment_argv[0].split(".")[0].replace("experiment_", "")
                timestr = time.strftime("%Y%m%d-%H%M")
                logfile = "%s_tuning_%s_tuning_%s_%de.log" % (timestr, tuner_name, algo_id, evals)
                logging.getLogger('').addHandler( logging.FileHandler(logfile) )
        elif switch == "-k":
            k_folds = int( swval )
        elif switch == "-rs":
            random_seed_override = int( swval )
        else:
            PrintHelp()
        
    setup_and_run_experiment_function(algo_id, repts, evals, CUTOFF, verbosity, k_folds, random_seed_override)
        

if __name__ == '__main__':
    RunExperiment()

