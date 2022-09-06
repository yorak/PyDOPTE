# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 12:39:47 2011

This file is used to generate random instances for the 
general function evaluation parameter tuning task.

@author: jussi
"""
import random
import os

#=== SETTINGS ===

# How many instances of how many constants to create
INSTANCES = 50
CONSTANTS = 20
MAX_VAL = 15.0*15.0

# This defines the subdirectory where the instance files are put
DIRECTORY = "f3_c"

# These define the instance file name. It is PREFIX+ID+POSTFIX.
PREFIX = DIRECTORY + "_"
POSTFIX = ".txt"

# List of generated instances is put to DIRECTORY/INSTANCE_LIST_FILENAME
INSTANCE_LIST_FILENAME = "instances.txt" 

# Create INSTANCES instances with CONSTANTS constants :)
CREATE_N = True
# Create INSTANCES instances for each constants 1..CONSTANTS :)
CREATE_NxM = False


#=== HELPER FUNCTIONS ===

def createConstantFile(filename, CONSTANTS):
    # Create the data
    constlist = []
    for v in range(CONSTANTS):
        cval = random.random()*MAX_VAL
        constlist.append( "p"+str(v)+"="+str(cval)+"\n" )
    
    # Write all the lines at once:    
    f = open(filename,"w")
    f.writelines(constlist)       
    f.close()   

def writeInstanceList(instance_list_file, instance_filenames):
    # Write instance list
    print ("Writing instances file " + instance_list_file)
    f = open(instance_list_file,"w")
    f.writelines(instance_filenames)       
    f.close()
    
#=== CREATION ROUTINES ===

def create_N_Instances(N, directory):
    # Create the instance files
    filenames = []
    for i in range(N):
        filename = directory + "/" + PREFIX + str(i+1)+ POSTFIX
        print ("Writing constant file " + filename)
        filenames.append(filename+"\n")
        createConstantFile(filename, CONSTANTS)
    
    writeInstanceList(PREFIX + INSTANCE_LIST_FILENAME, filenames)

def create_MxN_Instances(N, directory):
    
    # Create the instance files
    filenames = []
    for j in range(CONSTANTS):
        for i in range(N):
            filename = directory + "/" + PREFIX + str(j+1) + "_" + str(i+1)+ POSTFIX
            print ("Writing constant file " + filename)
            filenames.append(filename+"\n")
            createConstantFile(filename, j+1)

    writeInstanceList(PREFIX + INSTANCE_LIST_FILENAME, filenames)

def main():
    
    print "Creating constants files with following settings:"
    print "INSTANCES=" +str(INSTANCES)
    print "CONSTANTS=" +str(CONSTANTS)
    print "MAX_VAL=" +str(MAX_VAL)
    print "DIRECTORY=" +str(DIRECTORY)
    print "FILENAME=" +str(PREFIX)+"{i}"+str(POSTFIX)
    print "INSTANCE_LIST_FILENAME=" +str(INSTANCE_LIST_FILENAME)
    print "CREATE_N=" +str(CREATE_N)
    print "CREATE_NxM=" +str(CREATE_NxM)
    print ""

    # CALL WHAT YOU WANT
    if not os.path.exists(DIRECTORY):
            os.makedirs(DIRECTORY)
        
    if CREATE_N:
        create_N_Instances(INSTANCES, DIRECTORY)
    elif CREATE_MxN:
        create_MxN_Instances(INSTANCES, DIRECTORY)

if __name__ == '__main__':
    main()

