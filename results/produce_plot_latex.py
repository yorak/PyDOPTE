# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 13:43:21 2012

@author: jussi
"""

import glob
import os
import re

files_with_sections = [
    ("tuning_results*.eps", "Tuning result quality comparison plots"),
    ("box_plot*.eps", "Box plots of the tuning results"),
    ("parallel_plot*.eps", "Parallel coordinate plots of the tuned parameter configurations")
]
resfold = "appendix/plots/"   

for files, section_name in files_with_sections:

    print "\\clearpage"
    print "\\section{%s}" % section_name
    print

    tmp_filelist = list(glob.glob(files))
    tmp_filelist.sort()
    
    filelist = []
    for plotfile in tmp_filelist:
        # Swap best/median order in file list
        if "tuning_results" in plotfile:
            if "best" in plotfile:
                plotfile = plotfile.replace("best", "median")
            elif "median" in plotfile:
                plotfile = plotfile.replace("median", "best")
        filelist.append(plotfile)
    
    i = 0

    for plotfile in filelist:

        if i!=0 and i%2==0:
            print "\\clearpage"
            print 
        i+=1
        
        basename = plotfile.replace(".eps", "")
        fullpath = resfold+plotfile
        
        width = 0.8
        
        if "tuning_results" in plotfile:
            # tuning_results_VRPH-RTR.worst_testset.png
            parts =  basename.replace(".", "_").split("_")
            target = parts[2]
            avgf = parts[3]
            title = "Tuning results for the target %s (%s quality as the function of evaluation budget)" % \
                (target, avgf)
                
            width = 0.7
            
        elif "box_plot" in plotfile:
            # box_plot_VRPH-SA_1-100-1000-500.testset.png
            parts =  basename.split("_")
            target = parts[2]
            title = "Tuning results boxplot for the target %s." % target
            
            width = 0.8
                
        elif "parallel_plot" in plotfile:
            # parallel_plot_VRPSD-ACO_100.testset.png
            parts =  basename.split("_")
            target = parts[2]
            evals = parts[3]
            
            width = 0.6
            
            titlefilename = basename+".txt"
            with open (titlefilename, "r") as myfile:
                title=myfile.read().replace('\n', ' ')
            #Parallel coordinate plot for tuning VRPSD ILS with evaluation
            # budget of 1000. Coordinate key: 0=\texttt{-I}, 1=\texttt{-n},...
            
            title = title.replace(
                "plot for tuning",
                "plot of resulting parameter configurations in tuning"
            )
            title = title.replace(
                ". Coordinate key",
                ". Solution quality is propotional to the line thickness, where thicker line indicates better quality. Coordinate key",
            )
            
            # Round each with math ( $blah$ )
            title = re.sub(r'(\d+=\\texttt\{-\w+\})', r'$\1$', title)
            title = re.sub(r'(\w+)\=(\w+[,.])', r'\1$=$\2', title)
            title = re.sub(r'(\w+)_', r'\1\_', title)
    
        
        print "\\begin{figure}[!ht]"
        print "\\begin{center}"
        print "\\includegraphics[width=%.1f\\textwidth]{%s}" % (width,fullpath)
        print "\\caption{%s}" % title
        print "\\label{fig:%s}" % basename
        print "\\end{center}"
        print "\\end{figure}"
        print
    