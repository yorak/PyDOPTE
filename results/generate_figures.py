# -*- coding: utf-8 -*-
""" This module is used to produce figures and tables from the result data
from the tuning tests.

results is a dictionay with...
... a key of format (tuner, target_algorithm, evaluation_budget)
... a value or a payload of format (repts, mev, meq, seq, tpl, ql, evl ), where
       repts = number of tuning task repetitions
       mev = median/mean/best/worst number of evaluations for the tuning tasks
       meq = median/mean/best/worst quality (utility) for the tuning tasks
       tpl = list of tuned parameters (dict of parameter/values)
       ql = list of quality (utility) for the tuning tasks
       evl = list of number of evaluations for the tuning tasks
"""

from helpers import module_exists
import numpy as np 

if module_exists("parallelplot"):
    import parallelplot

if module_exists("pylab"):
    from pylab import *
    
if module_exists("matplotlib"):
    from matplotlib.ticker import FuncFormatter
    

PCPLOT_LINE_SCALE = 1.5
PCPLOT_LINE_JITTER = 0.01
Y_LABEL = "relative optimality gap (%)"

OUTPUT_NAME_TRANSLATIONS = {\
"cma-es":"CMA-ES",
"cmaes":"CMA-ES",
"irace":"I/F-Race",
}

def _labelize_tuner(tuner):
    tlabel = tuner
    if tuner.lower() in OUTPUT_NAME_TRANSLATIONS:
        tlabel = OUTPUT_NAME_TRANSLATIONS[tuner.lower()]
    return tlabel
    
def _get_styles(pubstyle, bw_steps = 4):
    if pubstyle=='journal':
        if bw_steps==4:
            colors = ['k',
                      '0.75', 
                      '0.5',
                      '0.25']
        else:
            colors = [str(c) for c in np.linspace(0,1.0,bw_steps+1)[:-1]]
            colors.reverse()
            
            
        styles = ["-","--","-.",":"]
        
        markers = None
    elif pubstyle=='poster':
        colors = [(216/255.0,66/255.0,0.0), # Bright red
                   (166/255.0,50/255.0,0.0), # Dark red
                   (62/255.0,84/255.0,151/255.0), # Blue
                   (29/255.0,38/255.0,71/255.0), # Dark blue
                   (194/255.0,194/255.0,194/255.0), # Gray
                   (97/255.0,97/255.0,97/255.0), #Dark grey
                   #(0/255.0,0/255.0,0/255.0), #Black
                  ]

        styles = ["-","--","-.",":"]
        markers = None
    else:
        colors = ['b',
                  'g', 
                  'r', 
                  'c', 
                  'm', 
                  'k',
                  'y',
                  'b']
        styles = ["-"]
        markers = ['o',
                   'x',
                   's',
                   '*',
                   'p',
                   'd',
                   'x',
                   'o']
    return colors, styles, markers
            
    
def _quickfix_preprocess_tuner_parameters(tpk):
    # Ugly quickfix. Remove timeouts and random switch
    if ("-r",1) in tpk: tpk.remove(("-r",1))
    if ("-r",0) in tpk: tpk.remove(("-r",0))
    if ("-cutoff",10.0) in tpk: tpk.remove(("-cutoff",10.0))
    elif ("-t",10.0) in tpk: tpk.remove(("-t",10.0))


def exportOverTunePlot(filename, results_on_training, results_on_validation, algos, tuners, ebs, pubstyle, per = "tuner", ebs_with_colors = False):
    
    if (len(results_on_training)==0 or \
       len(results_on_validation)==0 or \
       len(algos)==0 or \
       len(tuners)==0 or \
       len(ebs)==0):
        print "Not enough data to do the plot"
      
             
    colors, styles, markers = _get_styles(pubstyle, len(algos))

    markers = ['o',
               'v',
               's',
               '*',
               'p',
               'd',
               '^',]
               
    #print
    #print "INPUT:", algos, tuners, ebs
    
    keylist = []    
    onePlotPerTuner = None
    # One algo, show results by tuner
    if len(algos)==1:
        onePlotPerTuner = False
        algo = algos[0]
        for tuner in tuners:             
            for eb in ebs:
                #quickfix. 5000e only for ACO
                if algo!="VRPSD ACO" and eb==5000:
                    continue
                key = (tuner, algo, eb)    
                keylist.append(key)
            key = (None, None, None) # signal change of marker style
            keylist.append(key)
    # One tuner, show results by algo
    elif len(tuners)==1:
        onePlotPerTuner = True
        tuner = tuners[0]
        for algo in algos: 
            for eb in ebs:
                #quickfix. 5000e only for ACO
                if algo!="VRPSD ACO" and eb==5000:
                    continue
                key = (tuner, algo, eb)    
                keylist.append(key)
            key = (None, None, None) # signal change of marker style
            keylist.append(key)
    # many tuners and algos , show results by tuner, but algos as line joined
    else:
        if per=="tuner":
            for tuner in tuners:
                for algo in algos: 
                    for eb in ebs:
                        #quickfix. 5000e only for ACO
                        if algo!="VRPSD ACO" and eb==5000:
                            continue
                        key = (tuner, algo, eb)    
                        keylist.append(key)
                    key = (None, None, None) # signal change of marker style
                    keylist.append(key)
        elif per=="algo":
            for algo in algos: 
                for tuner in tuners:
                    for eb in ebs:
                        #quickfix. 5000e only for ACO
                        if algo!="VRPSD ACO" and eb==5000:
                            continue
                        key = (tuner, algo, eb)    
                        keylist.append(key)
                    key = (None, None, None) # signal change of marker style
                    keylist.append(key)
    #print keylist
    #return 
                
    if onePlotPerTuner==None:
        colors.append('k')

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    #ax1.grid()
    
    def to_percent(y, position):
        # Ignore the passed in position. This has the effect of scaling the default
        # tick locations.
        s = str(y)
    
        # The percent symbol needs escaping in latex
        if matplotlib.rcParams['text.usetex'] == True:
            return s + r'$\%$'
        else:
            return s + '%'
    
    # Create the formatter using the function to_percent. This multiplies all the
    # default labels by 100, making them all percentages
    #pformatter = FuncFormatter(to_percent)

    # Set the formatter
    #plt.gca().yaxis.set_major_formatter(pformatter )
    #plt.gca().xaxis.set_major_formatter(pformatter )
    
    mci = 0
    hasdata = False
    x = []
    y = []             
    labels_w_lineobjects = []
    tuners_labeled = set()
    algos_labeled = set()
    
    grouped_keys = []
    
    max_t = None
    max_v = None
    
    for key in keylist:         
        if key != (None, None, None):        
            (tuner, algo, eb) = key
            
            if (key in results_on_training) and (key in results_on_validation):
                (t_repts, t_mev, t_meq, t_seq, t_tpl, t_ql, t_evl ) = results_on_training[key]
                (v_repts, v_mev, v_meq, v_seq, v_tpl, v_ql, v_evl ) = results_on_validation[key]
            else:
                print "Warning:", key, "results not in both sets."
                continue
            
            x.append(t_meq)
            y.append(v_meq)
            
            if t_meq>max_t:
                max_t = t_meq
            if v_meq>max_v:
                max_v = v_meq    
            
            grouped_keys.append(key)
        
        # End of grouped results. Plot.
        if key == (None, None, None):
            #print "one scatter pattern" 

            # Next colour, if at end, take first color
            if onePlotPerTuner==None:
                if (per=="tuner" and tuner not in tuners_labeled) or \
                   (per=="algo" and algo not in algos_labeled):
                    if ebs_with_colors:
                        c = 'k'
                    else:
                        c = colors[mci%len(colors)]
                    m = markers[mci%len(markers)]
                    mci += 1
            else:
                if ebs_with_colors:
                    c = 'k'
                else:
                    c = colors[mci%len(colors)]

                m = markers[mci%len(markers)]
                mci += 1
                
            print grouped_keys
            print x,y,c,m 
            print
            grouped_keys = []
            
            if onePlotPerTuner==None and per=="tuner":
                l = _labelize_tuner(tuner)
            elif onePlotPerTuner or per=="algo":
                l = algo
            else:
                l = _labelize_tuner(tuner)
               
            #labels_w_lineobjects.append( (l, ax1.scatter(x, y, label = l, c=c, marker=m)) )
            if (onePlotPerTuner!=None) or \
               (per=="tuner" and not tuner in tuners_labeled) or \
               (per=="algo" and not algo in algos_labeled):
                labels_w_lineobjects.append( (l, ax1.plot(x, y, label=l, c=c, marker=m)[0]) )
                tuners_labeled.add(tuner)
                algos_labeled.add(algo)
            else:
                ax1.plot(x, y, label=l, c=c, marker=m)
                
            if ebs_with_colors:
               for i, eb in enumerate(ebs):
                   if i>=len(x):
                       break
                   ax1.plot([x[i]], [y[i]], label=l, c=colors[i%len(colors)], marker=m)
            
            hasdata = True
            
            x = []
            y = []

                                                
    if hasdata:
        x1,x2,y1,y2 = axis()
        #axis((-0.1,1.1,0,y2))
        #xlim([])
        xlabel("Configured quality on training set")
        ylabel("Configured quality on validation set")
        
        
        ax1.plot([0.0, max(max_t,max_v)], [0.0, max(max_t,max_v)], c='k', linestyle='dashed')
        
        # For fitting the legend outside the box    
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
        labels_w_lineobjects.sort()
        lab, lo  = zip(*labels_w_lineobjects)
        #ax1.legend(lo, lab, loc='center left', bbox_to_anchor=(1, 0.5))
        ax1.legend(lo, lab, loc=4)

        print "ExportGraph", "scatter", filename
        fig.savefig(filename,bbox_inches='tight')
    else:
        print "Skip Graph (no data)", "parallel", filename
    
    plt.close('all')      
        
def exportScatterPlot(filename, results, algo, tuners, ebs, parameters, pubstyle):
    
    colors, styles, markers = _get_styles(pubstyle)
    
    markers = ['o',
               'x',
               's',
               '*',
               'p',
               'd',
               'x',
               'o']
               
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    #ax1.grid()

    x = []
    y = []
   
    mci = 0
    
    hasdata = False
    
    labelized = set()
             
    labels_w_lineobjects = []
    
    for tuner in tuners: 
        x = []
        y = []
        for eb in ebs:
            # Get tuned parameters list
            tpl = None
            key = (tuner, algo, eb)    
            if key in results:
                (repts, mev, meq, seq, tpl, ql, evl ) = results[key]
            if not tpl:
                continue
            
            for tpi, tp in enumerate(tpl):
                tpk = tp.items()
                tpk.sort()
                
                tpx = []
                tpy = []
                
                _quickfix_preprocess_tuner_parameters(tpk)
                
                for tp_key,tp_val in tpk:
                    if tp_key in parameters:
                
                        x.append(tp_val)
                        y.append(ql[tpi])
                        
                        tpx.append(tp_val)
                        tpy.append(ql[tpi])
                if len(tpx)>0:
                    c = colors[mci/len(colors)]
                    m = markers[mci%len(markers)]
                    l = _labelize_tuner(tuner)
                    
                    if tuner in labelized:
                        ax1.plot(tpx, tpy, c=c, marker=m)
                    else:
                        labels_w_lineobjects.append(
                          (l, ax1.plot(tpx, tpy, label=l, c=c, marker=m)[0])
                        )
                        labelized.add(tuner)
                    hasdata = True
                                                
        #labels.append(tuner)
        #if len(x)>0 and ax1:
        #    c = colors[mci/len(colors)]
        #    m = markers[mci%len(markers)]
        #    
        #    ax1.scatter(x, y, label = _labelize_tuner(tuner), c=c, marker=m)

        # Next colour, if at end, take first color
        mci += 1
    
    if hasdata:
        x1,x2,y1,y2 = axis()
        axis((-0.1,1.1,0,y2))
        #xlim([])
        xlabel("/".join(parameters) + ' values')
        ylabel(Y_LABEL.capitalize())
        
        # For fitting the legend outside the box    
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
        labels_w_lineobjects.sort()
        lab, lo  = zip(*labels_w_lineobjects)
        ax1.legend(lo, lab, loc='center left', bbox_to_anchor=(1, 0.5))

        print "ExportGraph", "scatter", parameters, algo, filename
        fig.savefig(filename, bbox_inches='tight')
    else:
        print "Skip Graph (no data)", "parallel", algo, eb, filename
    
    clf()

def exportParallelCoordinatePlot(filename, results, algo, tuners, ebs, pubstyle):
    
    colors, styles, markers = _get_styles(pubstyle)
    coloredstyles = [str(c+s) for c in colors for s in styles]    
    
    print coloredstyles 
    
    figure(1)
    
    current_style = 0
    
    data = []
    style = []
    weight = []
    labels = []
    style_per_label = []
    coordinate_names = []
    
    rangeq = 1.0
    for tuner in tuners:
        # Calculate min and max q over all (active) evaluation budgets
        #  and tuners.
        qll = []
        for eb in ebs:
            key = (tuner, algo, eb)
            if key in results:
                (repts, mev, meq, seq, tpl, ql, evl ) = results[key]
                qll+=ql
        if len(qll)>0:
            minq = min(qll)
            maxq = max(qll)
            rangeq = maxq - minq 
            
    for tuner in tuners: 
        tuned_pc_count = 0
        
        for eb in ebs:
            tpl = None
            
            key = (tuner, algo, eb)    
            if key in results:
                (repts, mev, meq, seq, tpl, ql, evl ) = results[key]
    
            if not tpl:
                continue
            
            for tpi, tp in enumerate(tpl):
                tpk = tp.items()
                tpk.sort()
                
                _quickfix_preprocess_tuner_parameters(tpk)
                
                # Only show numeric values (create vector only containing those)
                tpk_num = [(tp_key,tp_val) for tp_key,tp_val in tpk if isinstance(tp_val, (int,float,long))]
                tp_values = list(zip(*tpk_num)[1])
                
                #for i in range(len(tp_values)):
                #    if isinstance(tp_values[i], (int,long)):
                #        jitter = gauss(0.0, PCPLOT_LINE_JITTER)
                #        tp_values[i] = float(tp_values[i])+jitter 
                        
                data.append( tp_values )
                
                # Use normalized q to get line width 
                #  (thicker the better)
                nq_inv = 0.0
                if rangeq != 0.0:                        
                    nq_inv = 1.0-(ql[tpi]-minq)/rangeq
                weight.append( max(1.0, 1.0+(nq_inv)*PCPLOT_LINE_SCALE) )
            tuned_pc_count+=len(tpl)
        
        #labels.extend( [tuner]*tuned_pc_count )
        style_per_label.append( (_labelize_tuner(tuner), coloredstyles[current_style] ) )
        style.extend( [coloredstyles[current_style]]*tuned_pc_count )
        
        # Next colour, if at end, take first color
        current_style+=1
        if current_style==len(coloredstyles):
            current_style=0
            
    #print labels
    if len(data)>0:
        coordinate_names = zip(*tpk_num)[0]
        print "ExportGraph", "parallel", algo, eb, filename
      
        # Shuffle data so that one line color does not dominate
        dcw = zip(data, style, weight)
        shuffle(dcw)
        data, style, weight = zip(*dcw)
        
        labels = []
        unique_tuners = set()
        for s in style:
            for tuner,scode in style_per_label:
                #print tuner,color,ccode, c
                if s==scode:
                    labels.append(_labelize_tuner(tuner))
                    if tuner not in unique_tuners:
                        unique_tuners.add(tuner)
                    break
                
        #print labels
        
        if len(unique_tuners)<=1:
            labels = None
            
        # QUICKFIX. clean up cnames
        ccn = [cn.replace("-h_","").replace("-","") for cn in coordinate_names]
        
        fig, lgd = parallelplot.parallel_coordinates(data, axislabels=ccn, style=style, lweight=weight, labels=labels, jitter_sd=PCPLOT_LINE_JITTER)
        
        #if lgd:
        #    fig.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight') 
        #else:
        fig.savefig(filename, bbox_inches='tight')
        
    else:
        print "Skip Graph (no data)", "parallel", algo, eb, filename
    
    clf()
        
def exportBoxPlot(filename, results, algo, (minQ,maxQ), pubstyle):
    
    print "ExportGraph", "boxplot", algo, (minQ,maxQ), filename
    
    
    data = []
    labels = []
    for key in results:        
        if key[1]!=algo:
            continue
        
        (tuner, algo, eb) = key
        (repts, mev, meq, seq, tpl, ql, evl ) = results[key]
            
        if ql:
            data.append( ql )
            labels.append( _labelize_tuner(tuner)+"_"+str(eb) )
        
    data.reverse()
    labels.reverse()
    
    if len(results)>22:        
        fsize = rcParams['figure.figsize']
        fsize = (fsize[0], fsize[1]*len(results)/22)
        figure(1, figsize=fsize)
    else:
        figure(1)
    
    xlim( (minQ,maxQ) )      
    xlabel(Y_LABEL.capitalize())      
    
    
    bp = boxplot(data, vert=False, widths=0.4)
    
    if pubstyle=='journal':
        BBLINE = 1.0
        setp(bp['boxes'], color='k', linewidth=BBLINE)
        setp(bp['whiskers'], color='k', linestyle = 'solid', linewidth=BBLINE)
        setp(bp['fliers'], color='k', alpha = 0.9, marker= 'o', markersize = 2)
        setp(bp['medians'], color='k', linewidth=BBLINE*1.5)
        
    yticks(range(1, len(labels)+1), labels)
    savefig(filename, pad_inches=0.1, bbox_inches='tight')
    clf()
    
def exportLineGraph(filename, results, algo, avglabel, (minQ,maxQ), (minEv,maxEv), pubstyle):
    """
    Suggested:
        tuners=DEFAULT+TUNERS
        ebs=[1]+EBS+EXTRA_EBS
    """
    print "ExportGraph", "line", algo, (minQ,maxQ), (minEv,maxEv), filename
    
    colors, styles, markers = _get_styles(pubstyle)
    
    figure(1)

    # Build tuners and ebs list from results
    # (use filtering)
    tuners = []
    ebs = []
    for key in results:
        (tunerk, algok, ebk) = key
        if algok==algo and not tunerk in tuners:
            tuners.append(tunerk)
        if algok==algo and not ebk in ebs:
            ebs.append(ebk)
    
    # Loop all tuners and ebs
    i = -1
    ls = '-'
    col = 'k'
    mk = ''
    for tuner in tuners:
        xv = []
        yv = []
        #lyv = []
        #hyv = []
        
        for eb in ebs:
            key = (tuner, algo, eb)
            dkey = (tuner, algo, 1)
            
            if dkey in results:
                ls = ':'
                col = 'k'
                mk = ''
                (repts, mev, meq, seq, tpl, ql, evl ) = results[dkey]
                yv.append(meq)
                xv.append(eb)
            else:
                while True:
                    col = colors[mod(i/len(styles),len(colors))]
                    ls = styles[mod(i,len(styles))]
                    if markers:
                        mk = markers[mod(i,len(markers))]
                    i+=1
                    # This is reserved for defaults
                    if col!='k' and ls!=':':
                        break
                
                if key in results:
                    (repts, mev, meq, seq, tpl, ql, evl ) = results[key]
                    yv.append(meq)
                    xv.append(mev)
                    #lyv.append(meq-seq)
                    #hyv.append(meq+seq)
            
        #if len(lyv)>0:
        #    plot(xv, lyv, c=col, linestyle = ":" )
        if len(xv)>0:
            plot(xv, yv, label = _labelize_tuner(tuner), c=col, marker=mk, linestyle = ls )
            
        #if len(hyv)>0:
        #    plot(xv, hyv, c=col, linestyle = ":" )
    
    ylim( (minQ,maxQ) )
    xlim( (minEv,maxEv) )
    
    if(maxEv>4000):
        #xscale('log')
        xticks([100,500,1000,5000], [100,500,1000,5000])
            
    xlabel('Evaluation budget')
    if avglabel:
        ylabel( avglabel + " " + Y_LABEL )
    else:
        ylabel( Y_LABEL.capitalize() ) 
    
    legend(loc='upper right')
    savefig(filename, bbox_inches='tight')#, dpi=400)
    clf()    

def produceLatexTable(results, caption, notes, label, ebs, algorithms, tuners, printSd=True, printDefaultsRow=True, sbs=3, significantlyDifferent=None, warn_ebd=0.15, vert=False, set_label=None):
    """
    sbs = how many tuner results are side by side.
    """
    
    #for k in results:
    #    print k, results[k][2]
    
    # Table consists of bigger rows and col
    #  with each "cell" containing results of a algorithm

    #use_vert_lines
    if not vert:
        uvl = "|"
        BOLD_HEADERS = "\\textbf"
    else:
        uvl = ""
        BOLD_HEADERS = ""
    extra_hlines = False
    IJOC_STYLE = vert
    OUTPUT_MEVALS = False
        
    # Table dimensions
    cols = sbs
    if vert:
        one_box_cols = len(tuners)
    else:
        one_box_cols = len(ebs)
    rows = int(ceil(len(algorithms)/float(sbs)))    
        
    # TABLE DEFINITION
    print "\\begin{table}[!ht]"
    if IJOC_STYLE:
        print "\\TABLE"
        print "{%s \\label{table:%s}}" % (caption, label)
        print "{"
        algo_cols_align = ["p{1.6cm}"]*one_box_cols*sbs
    else:
        print "\\caption{%s}" % caption+" "+notes
        print "\\label{table:%s}" % label
        print "\\begin{center}"
        algo_cols_align = ["p{1.38cm}"]*one_box_cols*sbs
    #print "{\\tinysmall"
    print "\\begin{tabular}{ l "+" ".join(algo_cols_align)+" }"
    
    #print "sbs", sbs, "algos", algorithms, "ebs", ebs
    if set_label:
        set_label = " "+set_label
    else:
        set_label = ""
            
            
    # ALGORITHM NAME ROW
    fullcols=0
    for row in range(rows):
        fullcols=0
                
        # 1. Algorithm names on this row
        
        rowsolvers = []
        for col in range(cols):
            idx = row*cols+col
            if idx<len(algorithms):
                algo = algorithms[row*cols+col]
                colstyle = "%sc%s" % (uvl,uvl)
                fullcols+=1
            else:
                algo = ""
                colstyle = "c"
            
            if IJOC_STYLE:
                defkey = ("Defaults", algo, 1)        
                if defkey in results:
                    if defkey in significantlyDifferent:
                        defaultval = "\\textbf{%.2f (%.2f)}" % (results[defkey][2] , results[defkey][3])
                    else:
                        defaultval = "%.2f (%.2f)" % (results[defkey][2] , results[defkey][3])
                    colstyle = "%sc%s" % (uvl,uvl)
                else:
                    defaultval = ""
                    colstyle = "c"
                rowsolvers.append("\\multicolumn{%d}{%s}{%s{%s}, defaults: %s }" % (one_box_cols, colstyle, "\\textbf", algo.replace(" ", "-")+set_label, defaultval))
            else:
                rowsolvers.append("\\multicolumn{%d}{%s}{%s{%s}}" % (one_box_cols, colstyle, BOLD_HEADERS, algo.replace(" ", "-")+set_label))
        hlinelength = (1+fullcols*one_box_cols)
        print "  \\hline" if fullcols==cols else "  \cline{1-{%d}}"%(hlinelength)  
        if IJOC_STYLE:
            print "\\up & "+" & ".join(rowsolvers) + " \\\\"
        else:
            print "  \\multicolumn{1}{%sc%s}{%s{Target}} & " % (uvl, uvl, BOLD_HEADERS) + " & ".join(rowsolvers) + " \\\\"
        if extra_hlines:
            print "  \\hline" if fullcols==cols else "  \cline{1-{%d}}"%(hlinelength)    
        
        # 2. Defaults on this row
        if not IJOC_STYLE and printDefaultsRow:
            rowdefaults = []
            for col in range(cols):
                idx = row*cols+col
                if idx<len(algorithms):
                    algo = algorithms[row*cols+col]
                else:
                    algo = ""
                defkey = ("Defaults", algo, 1)        
                if defkey in results:
                    if defkey in significantlyDifferent:
                        defaultval = "\\textbf{%.2f (%.2f)}" % (results[defkey][2] , results[defkey][3])
                    else:
                        defaultval = "%.2f (%.2f)" % (results[defkey][2] , results[defkey][3])
                    colstyle = "%sc%s" % (uvl,uvl)
                else:
                    defaultval = ""
                    colstyle = "c"
                rowdefaults.append( "\\multicolumn{%d}{%s}{%s}" % (one_box_cols, colstyle, defaultval ))
            print "  \\multicolumn{1}{%sc%s}{%s{Defaults}} & " % (uvl, uvl, BOLD_HEADERS) + " & ".join(rowdefaults) + " \\\\"   
            if extra_hlines:
                print "  \\hline" if fullcols==cols else "  \cline{1-{%d}}"%(hlinelength)    
        
        # 3. Tuners/EBs row
        if IJOC_STYLE:
            print "\\down",
        if vert:
            tuner_multi_cols = []
            for col in range(cols):
                idx = row*cols+col
                if idx<len(algorithms):
                    tuner_multi_cols+=["\\multicolumn{1}{%sl%s}{%s"%(uvl,uvl,BOLD_HEADERS)+"{%s}}"% _labelize_tuner(t) for t in tuners]
                else:
                    tuner_multi_cols+=["" for t in tuners]
            if IJOC_STYLE:
                print " %s{EB} & "%(BOLD_HEADERS) + (" & ".join(str( val ) for val in tuner_multi_cols)) + " \\\\"
            else:
                print "  \\multicolumn{1}{%sc%s}{%s{EB}}  & "%(uvl,uvl, BOLD_HEADERS) + (" & ".join(str( val ) for val in tuner_multi_cols)) + " \\\\"
        else:
            eb_multi_cols = []
            for col in range(cols):
                idx = row*cols+col
                if idx<len(algorithms):
                    eb_multi_cols+=["\\multicolumn{1}{%sl%s}{%s"%(uvl,uvl,BOLD_HEADERS)+"{%d}}"%e for e in ebs]
                else:
                    eb_multi_cols+=["" for e in ebs]                    
            if IJOC_STYLE:
                print " %s{Tuner} & "%(BOLD_HEADERS)+ (" & ".join(str( val ) for val in eb_multi_cols)) + " \\\\"
            else:
                print "  \\multicolumn{1}{%sc%s}{%s{Tuner}}  & "%(uvl,uvl,BOLD_HEADERS)+ (" & ".join(str( val ) for val in eb_multi_cols)) + " \\\\"
        print "  \\hline" if fullcols==cols else "  \cline{1-{%d}}"%(hlinelength)    
    
        
        # 4. TUNING RESULTS
        
        # Build a indexing set of the right format
        tuners_cols_ebs = []
        if vert:
            for eb in ebs:
                for col in range(cols):
                    for tuner in tuners:
                        key = (tuner, algo, eb)
                        if key in results:
                            tuners_cols_ebs.append( (tuner, col, eb) )
        else:
            for tuner in tuners:
                for col in range(cols):
                    for eb in ebs:
                        key = (tuner, algo, eb)
                        if key in results:                        
                            tuners_cols_ebs.append( (tuner, col, eb) )
                        
        #print tuners_cols_ebs
        
        result_multi_cols = []
        prevtuner = 0
        preveb = 0
        
        if IJOC_STYLE:
            print "\\up",
            
        for tuner, col, eb in tuners_cols_ebs:
            #print tuner, col, eb
            if ( len(result_multi_cols)>0 and
                 ((vert and preveb != eb) or (not vert and prevtuner != tuner) )):
                label = str(preveb) if vert else str(prevtuner)
                result_multi_cols[-1] = "\\multicolumn{1}{l%s}"%uvl+"{%s}" % result_multi_cols[-1]
                if IJOC_STYLE:
                    labelfield = "  %s"%BOLD_HEADERS+"{%s} & "%label
                else:
                    labelfield = "  \\multicolumn{1}{%sl%s}{%s"%(uvl,uvl,BOLD_HEADERS)+"{%s}} & " % label
                print labelfield + " & ".join(result_multi_cols) + " \\\\"
                if extra_hlines and vert:
                    print "  \\hline" if fullcols==cols else "  \cline{1-{%d}}"%(hlinelength)
                result_multi_cols = [] 
            preveb = eb
            prevtuner = tuner
                
            idx = row*cols+col
            if idx<len(algorithms):
                algo = algorithms[idx]
            else:
                algo = ""
                
            key = (tuner, algo, eb)
            
            if key in results:
                (ar, mev, meq, seq, tpl, ql, evl ) = results[key]
                
                fn = "" #str(key)
                
                prefix = ""
                postfix = ""
                if mev-eb>warn_ebd*eb:
                    prefix = "\\textit{"+prefix
                    postfix = postfix+"$^+$}"
                if mev-eb<-warn_ebd*eb:
                    prefix = "\\textit{"+prefix
                    postfix = postfix+"$^-$}"
                
                
                if OUTPUT_MEVALS:
                    postfix = postfix + "["+str(int(mev))+"]"
                    
                if significantlyDifferent and key in significantlyDifferent:
                    if printSd:
                        result_multi_cols.append( prefix + ("\\textbf{%.2f(%.2f)}%s" % \
                            (meq , seq, fn)) + postfix )
                        
                    else:
                        result_multi_cols.append( prefix + ("\\textbf{%.2f}%s" % (meq,fn)) + postfix )
                else:
                    if printSd:

                        result_multi_cols.append(  prefix + ("%.2f(%.2f)%s" % \
                            (meq , seq, fn)) + postfix )
                    else:
                        result_multi_cols.append( prefix + ("%.2f%s"  % (meq,fn)) + postfix)
                    
            else:
                #print "Key %s not in results" % str(key)
                result_multi_cols.append("")
        label = str(eb) if vert else str(tuner)
        
        last_ne_idx = -1
        for i in range(0, len(result_multi_cols)):
            if result_multi_cols[-i]!="":
                last_ne_idx = -i
                break
        #print "DEBUG:",last_ne_idx
        if not last_ne_idx!=0:
            #result_multi_cols[last_ne_idx] = "\\multicolumn{1}{l%s}"%uvl+"{%s}" % result_multi_cols[-1]                
            if IJOC_STYLE:
                print "\\down",
                labelfield = "  %s"%BOLD_HEADERS+"{%s} & "%label
            else:
                labelfield = "  \\multicolumn{1}{%sl%s}{%s"%(uvl,uvl,BOLD_HEADERS)+"{%s}} & " % label   
            print labelfield + " & ".join(result_multi_cols) + " \\\\"
            print "  \\hline" if fullcols==cols else "  \cline{1-{%d}}"%(hlinelength)
        elif fullcols==cols:
            print "  \\hline"
            
        if row<rows-1:
             print "\\\\[1pt]"
    
    # END OF TABLE
    print "\\end{tabular}"
    #print "}"
    if IJOC_STYLE:
        print "}{%s}" % notes
    else:
        print "\\end{center}"
    print "\\end{table}"
    print
    #print "\\footnotetext{Exceeded evaluation budget by over 10 \\%}"
    #for tuner, experiment in results.items():
    #    for algo, values in experiment.items():
    #        print tuner, algo, values
