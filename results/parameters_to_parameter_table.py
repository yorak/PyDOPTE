# -*- coding: utf-8 -*-
"""
Created on Tue Feb 09 13:42:28 2016

@author: juherask
"""

headers = {
 "vrph_ej":['', '1ptm', '2ptm', 'two', 'oro', 'tho', '3ptm', '', 'm', 't', 's', '', '', '', '', '', ],
 "vrph_rtr":['', '1ptm', '2ptm', 'two', 'oro', 'tho', '3ptm', '', 'D', '\\delta', 'K', 'N', 'P', 'p', 'a', 't'],
 "vrph_sa":['', '1ptm', '2ptm', 'two', 'oro', 'tho', '3ptm', '', 'T', 'n', 'i', '\\alpha', 'N', '', '', '', ],

 "vrpsd_aco":['', 'p', 't', '', 'm', '\tau', '\\psi', '\rho', 'q', '\\alpha', '', '', '', '', '', '', ],
 "vrpsd_ea":['', 'p', 't', '', 'p', 'mr', 'amr', '', '', '', '', '', '', '', '', '', ],
 "vrpsd_ils":['', 'p', 't', '', 'x', '', '', '', '', '', '', '', '', '', '', '', ],
 "vrpsd_sa":['', 'p', 't', '', '\\mu', '\\alpha', '\\psi', '\rho', '', '', '', '', '', '', '', '', ],
 "vrpsd_ts":['', 'p', 't', '', 'ttf', 'p_t', 'p_o', '', '', '', '', '', '', '', '',]
}

parameter_name_to_header = {
    'vrph':{'-h_oro': 'oro', '-h_tho': 'tho', '-h_1pm': '1ptm', '-h_3pm': '3ptm', '-h_two': 'two', '-h_2pm': '2ptm'},
    'vrph_ej':{'-m': 's', '-t': 't', '-j': 'm'},
    'vrph_rtr':{'-d': '\\delta', '-a': 'a', '-m': 'K', '-N': 'N', '-k': 'D', '-t': 't', '-P': 'P', '-p': 'p'},
    'vrph_sa':{'-t': 'T', '-n': 'n', '-i': 'i', '-c': '\\alpha', '-nn': 'N'},
    
    'vrpsd':{'-u': 't', '-p': 'p'},
    'vrpsd_aco':{'-tau0': '\tau', '-alpha': '\\alpha', '-rho': '\rho', '-psi': '\\psi', '-colonysize': 'm', '-Q': 'q'},
    'vrpsd_ea':{'-popSize': 'P', '-isadaptive': 'amr', '-mr': 'mr'},
    'vrpsd_ils':{'-I': 'x'},
    'vrpsd_sa':{'-itf': '\\mu', '-rtl': '\\psi', '-ilr': '\rho', '-alpha': '\\alpha'},
    'vrpsd_ts':{'-po': 'p_o', '-pt': 'p_t', '-ttf': 'ttf'}
}

BEST_PARAMETERS_FILE="highlevel/best_median_parameters.csv"
DEFAULT_PARAMETERS_FILE="highlevel/default_parameters.csv"
DEBUG=False

def generate_table_lines(from_parameter_sets_file):
    pf = open(from_parameter_sets_file, 'r')
    hlines = []
    olines = []

    ptype = " best" if "best" in from_parameter_sets_file else " default"
    
    for l in pf.readlines():
        parts = l.split(";")
        tkey = parts[0].replace(" ", "_").lower()
        mq = 
        pms = eval(parts[3])
        family_key = tkey.split("_")[0]
        
        key = tkey
        if not tkey in headers:
            key = "_".join( tkey.split('_')[:2] )
        hdr = headers[key]
        
        table_values = {}
        
        pmcount = len([p for p in hdr if len(p)>0])
        pmtot = 0
        for pm,pval in pms.items():
            # convert from arg to pm_name
            if pm in parameter_name_to_header[key]:
                hpn = parameter_name_to_header[key][pm]
                table_values[ hpn ] = pval
                pmtot+=1
            elif pm in parameter_name_to_header[family_key]:
                hpn = parameter_name_to_header[family_key][pm]
                table_values[ hpn ] = pval
                pmtot+=1
            elif DEBUG:
                print "skip", pm, "=", pval
        if pmcount!=pmtot:
            print "ERROR, all header parameters have no value set"
        
        oline = ""
        hline = ""
        oline += tkey.replace('_', " ").upper() +ptype
        first = True
        for h in hdr:
            if first:
                first  = False            
            elif h=='':
                oline += " & "
                hline += " & "
            else:
                hline += "&{$%s$}" % h
                if type(table_values[h]) is float:
                    oline += " & %.2f" % table_values[h]
                else:
                    oline += " & " + str(table_values[h])
    
        hline+="\\\\"
        oline+="\\\\"
        
        olines.append(oline)
        hlines.append(hline)
    return hlines, olines

hlines, def_lines = generate_table_lines(DEFAULT_PARAMETERS_FILE)        
_, best_lines = generate_table_lines(BEST_PARAMETERS_FILE)

for i in range(len(hlines)):
    print hlines[i]
    print def_lines[i]
    print best_lines[i]
    print


            
            
            
    
    