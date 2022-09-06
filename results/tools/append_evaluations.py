# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 20:27:13 2012

@author: juherask

This file is used to convert old style "new" files to new style "we" files.
"""

def read_csv(f):
    rows = []
    rf = open(f)
    for line in rf.readlines():
        parts = line.split(";")
        if len(parts)>1:
            rows.append( parts )
    rf.close()
    return rows
    

def combine_evaluation_files(actual_evals_field_filename, rest_fields_filename, result_filename):
    
    aer = read_csv(actual_evals_field_filename)
    arr = read_csv(rest_fields_filename)
    
    print "%s has %d entries" % (actual_evals_field_filename, len(aer)), "%s has %d entries" % (rest_fields_filename, len(arr))

    # Assume
    if len(aer)!=len(arr):
        print "WARNING: Files %s and %s do not have same number of records, we file not produced." % (actual_evals_field_filename,rest_fields_filename)
        return 

    
    #Rows are:
    #<key>;<tuned parameter set Id>;<repeat idx>;<benchmark_name>; (continues...)
    # (continues...) <seed>;<evaulation result>;<actual tuning evaluations>;<hash_of_the_parameter_set_seed_and_benchmark>
                    
    evaluations_d = {}
    for row_e in aer:
        key = str(row_e[0:4])
        payload_evaluations = row_e[6]
        #print key
        evaluations_d[key]=payload_evaluations
    
    rf = open(result_filename,"w")
    for row_r in arr:
        key = str(row_r[0:4])
        if not key in evaluations_d:
            raise IOError("No corresponding evaluations field for %s" % key)
        if len(row_r)==8:
            rf.write( "%s;%d;%d;%s;%d;%f;%d;%d\n" % (str(row_r[0]), int(row_r[1]), int(row_r[2]), row_r[3],\
                  int(row_r[4]), float(row_r[5]), int(row_r[6]), int(row_r[7])) )
        else:
            rf.write( "%s;%d;%d;%s;%d;%f;%d;%d\n" % (str(row_r[0]), int(row_r[1]), int(row_r[2]), row_r[3],\
                  int(row_r[4]), float(row_r[5]), int(evaluations_d[key]), int(row_r[6])) )
    rf.close()

def cvrp_we_to_testset():
    filesc = "evals_*_VRPH*_we.txt"
    filess = "evals_*_vrph*_we.txt"
    
    import glob
    import shutil

    for evalFile in list( glob.glob(filesc) ) + list( glob.glob(filess) ):
        tgtFile = evalFile.replace("_we.", "_testset.")
        print "cp %s %s" % (evalFile, tgtFile)
        shutil.copy2(evalFile, tgtFile)        
        
def main():
    files = "evals_*_new.txt"
    
    import glob
    from evaluate_results import evaluate_results        
    import time
    import os
    import shutil
    
    for evalFile in glob.glob(files):
        tmpFile = evalFile.replace("_new", "_we_tmp")
        tgtFile = evalFile.replace("_new", "_we")

	# Prefer to use testset if such is available
        #testEvalFile = evalFile.replace("_new", "_testset")
	#if os.path.isfile(testEvalFile)
        #    evalFile = testEvalFile

	# Check if the file is already new style file, copy (but do not replace) the we file
	if open(evalFile).readline().count(';')==7:
           if not os.path.isfile(tgtFile):
              print "cp %s %s" % (evalFile, tgtFile)
              shutil.copy2(evalFile, tgtFile)        
              continue

        
        #evals_CMAES_VRPHSA_10repts.txt -> result_CMAES_VRPHSA_10sec_1000eval_10repts.txt
        srcFile = evalFile.replace("evals_", "result_").replace("_new", "").replace("_10repts.", "*repts.");
        #print evalFile, srcFile
        evl_lines = evaluate_results(10, srcFile, True)
        
        if not os.path.isfile(tgtFile):
            ef = open(tmpFile,"w")
            for l in evl_lines:
                ef.write(l+"\n")
            ef.flush()
            ef.close()
            #print len(evl_lines)
    
        
            print "combine %s+%s=%s" % (srcFile, evalFile, tgtFile)
            combine_evaluation_files(tmpFile, evalFile, tgtFile)
            
            os.remove(tmpFile)
        
    #aeffn = "evals_GGA_vrpsd_ea_10repts_test_w_evals.txt"
    #rqffn = "evals_GGA_vrpsd_ea_10repts_new.txt"    
    #rfn = "test.txt"
    #combine_evaluation_files(aeffn, rqffn, rfn)
        
if __name__ == "__main__":
    main()
    #cvrp_we_to_testset()
