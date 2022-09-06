from parse_results import parseResultsFromFiles, DEFAULT
from pprint import pprint

files = [
r"christofides_3cv/result_CMAES_vrph_christofides_ej_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_CMAES_vrph_christofides_ej_10sec_100eval_3cv_5repts.txt",    
r"christofides_3cv/result_CMAES_vrph_christofides_ej_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_CMAES_vrph_christofides_rtr_10sec_1000eval_3cv_5repts.txt",  
r"christofides_3cv/result_CMAES_vrph_christofides_rtr_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_CMAES_vrph_christofides_rtr_10sec_500eval_3cv_5repts.txt",   
r"christofides_3cv/result_CMAES_vrph_christofides_sa_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_CMAES_vrph_christofides_sa_10sec_100eval_3cv_5repts.txt",    
r"christofides_3cv/result_CMAES_vrph_christofides_sa_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_GGA_vrph_christofides_ej_10sec_1000eval_3cv_5repts.txt",     
r"christofides_3cv/result_GGA_vrph_christofides_ej_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_GGA_vrph_christofides_ej_10sec_500eval_3cv_5repts.txt",      
r"christofides_3cv/result_GGA_vrph_christofides_rtr_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_GGA_vrph_christofides_rtr_10sec_100eval_3cv_5repts.txt",     
r"christofides_3cv/result_GGA_vrph_christofides_rtr_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_GGA_vrph_christofides_sa_10sec_1000eval_3cv_5repts.txt",     
r"christofides_3cv/result_GGA_vrph_christofides_sa_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_GGA_vrph_christofides_sa_10sec_500eval_3cv_5repts.txt",      
r"christofides_3cv/result_IRace_vrph_christofides_ej_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_IRace_vrph_christofides_ej_10sec_100eval_3cv_5repts.txt",    
r"christofides_3cv/result_IRace_vrph_christofides_ej_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_IRace_vrph_christofides_rtr_10sec_1000eval_3cv_5repts.txt", 
r"christofides_3cv/result_IRace_vrph_christofides_rtr_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_IRace_vrph_christofides_rtr_10sec_500eval_3cv_5repts.txt",   
r"christofides_3cv/result_IRace_vrph_christofides_sa_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_IRace_vrph_christofides_sa_10sec_100eval_3cv_5repts.txt",    
r"christofides_3cv/result_IRace_vrph_christofides_sa_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_ParamILS_vrph_christofides_ej_10sec_1000eval_3cv_5repts.txt", 
r"christofides_3cv/result_ParamILS_vrph_christofides_ej_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_ParamILS_vrph_christofides_ej_10sec_500eval_3cv_5repts.txt", 
r"christofides_3cv/result_ParamILS_vrph_christofides_rtr_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_ParamILS_vrph_christofides_rtr_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_ParamILS_vrph_christofides_rtr_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_ParamILS_vrph_christofides_sa_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_ParamILS_vrph_christofides_sa_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_ParamILS_vrph_christofides_sa_10sec_500eval_3cv_5repts.txt",  
r"christofides_3cv/result_REVAC_vrph_christofides_ej_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_REVAC_vrph_christofides_ej_10sec_100eval_3cv_5repts.txt",     
r"christofides_3cv/result_REVAC_vrph_christofides_ej_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_REVAC_vrph_christofides_rtr_10sec_1000eval_3cv_5repts.txt",  
r"christofides_3cv/result_REVAC_vrph_christofides_rtr_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_REVAC_vrph_christofides_rtr_10sec_500eval_3cv_5repts.txt",    
r"christofides_3cv/result_REVAC_vrph_christofides_sa_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_REVAC_vrph_christofides_sa_10sec_100eval_3cv_5repts.txt",    
r"christofides_3cv/result_REVAC_vrph_christofides_sa_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_RTnR_vrph_christofides_ej_10sec_1000eval_3cv_5repts.txt",    
r"christofides_3cv/result_RTnR_vrph_christofides_ej_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_RTnR_vrph_christofides_ej_10sec_500eval_3cv_5repts.txt",    
r"christofides_3cv/result_RTnR_vrph_christofides_rtr_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_RTnR_vrph_christofides_rtr_10sec_100eval_3cv_5repts.txt",    
r"christofides_3cv/result_RTnR_vrph_christofides_rtr_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_RTnR_vrph_christofides_sa_10sec_1000eval_3cv_5repts.txt",    
r"christofides_3cv/result_RTnR_vrph_christofides_sa_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_RTnR_vrph_christofides_sa_10sec_500eval_3cv_5repts.txt",      
r"christofides_3cv/result_SMAC_vrph_christofides_ej_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_SMAC_vrph_christofides_ej_10sec_100eval_3cv_5repts.txt",      
r"christofides_3cv/result_SMAC_vrph_christofides_ej_10sec_500eval_3cv_5repts.txt",
r"christofides_3cv/result_SMAC_vrph_christofides_rtr_10sec_1000eval_3cv_5repts.txt",    
r"christofides_3cv/result_SMAC_vrph_christofides_rtr_10sec_100eval_3cv_5repts.txt",
r"christofides_3cv/result_SMAC_vrph_christofides_rtr_10sec_500eval_3cv_5repts.txt",     
r"christofides_3cv/result_SMAC_vrph_christofides_sa_10sec_1000eval_3cv_5repts.txt",
r"christofides_3cv/result_SMAC_vrph_christofides_sa_10sec_100eval_3cv_5repts.txt",      
r"christofides_3cv/result_SMAC_vrph_christofides_sa_10sec_500eval_3cv_5repts.txt",
]

# Validate that all folds are the same

fold_sets = {}

all_results = {}
for filen in files:
    try:
        results = parseResultsFromFiles(filen, crossValidation=True)
    except Exception as e:
        print str(e)
        continue
        
    all_results = dict(results.items()+all_results.items())
    for key, result in results.items():
        (repts, rl, fl, mev, meq, seq, tpl, ql, evl, ctsl, cvsl ) = result
        print key
        print "---------------------------------"
        print "repeats=", repts
        print "mev=", mev
        print "meq=", meq            
        print "seq=", seq
        print
        continue
        for i in range(len(rl)):
            print "  rep#=", rl[i]
            print "  fold#=", fl[i]
            print "  q=", ql[i]
            print "  ev=", evl[i]
            print "  ps=",
            pprint(tpl[i])
            print "  training set="
            pprint(ctsl[i])
            print "  validation set="
            pprint(cvsl[i])
            print
            
            # Verify that fold sets are the same            
            fk = (rl[i],fl[i])
            if fk in fold_sets:
                rkey, rcvs = fold_sets[fk]
                if set(rcvs)!=set(cvsl[i]):
                    pprint(rcvs)
                    pprint(cvsl[i])
                    raise IOError( "Error, fold set for %d. fold, repetition %d for %s is different than the previous recorded one for %s."%\
                    (fl[i], rl[i], key, rkey) )
                
            else:
                fold_sets[fk] = (key, cvsl[i])
        print
    

