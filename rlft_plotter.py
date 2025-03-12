# -*- coding: utf-8 -*-

def rlft_plotter(x_datasets, y_datasets, T_datasets=None, data_ids=None, x_label='Frequency [Hz]', y_label='R [m$\Omega$]', y_multiplier=1, normalise_y_axis=False, short_legend_tags=[False, False], legend_header=None, filter_temps='all', num_curves='all', fit_curves=False, save_dir='cwd', save_string='default', save_fitDataString = False):
    """
    Plot multiple datasets on one set of axes and saves the figures.
    Can fit curves to datasets based on R(f) characteristic relationship.
    
    INPUTS:
    1) x, y, T data. Lists of lists of data,
    i.e. x_data = [[x0-xn1], [x0-xn2], ..., [x0-xnN]]
         y_data = [[y0-yn1], [y0-yn2], ..., [y0-ynN]]
         T_data = [[T0-Tn1], [T0-Tn2], ..., [T0-TnN]]
    2) data_ids = list of data identification names. e.g. 'coil 1'
    3) x_label = label for the x axis on saved figures
    4) y_label = label for the y axis on saved figures
    5) y_multiplier = e.g. 1000 Ohms --> mOhms, for converting small units on y axis
    6) normalise_y_axis = normalise the y data to this value:
        if type(normalise_y_axis) == numeric, the y data are normalised to this value
        elif == 'min': y data normalised to the minimum y value in all y data
        elif == 'av': y data normalised to the average of the first points of all y series
        if True and fit_curves != False: the y data are normalised to their y-intercept
        else: the y data are normalised to their first datapoint value
    7) short_legend_tag = either False or a string. Legend labels will be truncated following the
        string, but file numbers are preserved at the ends of labels.
    8) legend_header = title for the legend box on the graph
    9) filter_temp = list any of [25, 50, 75, 100] or 'all' filter data by temperature in degC
    10) num_curves = int(1-N) or 'all' : plots an evenly spaced subset of the data.
    11) fit_curves = 'R_vs_f' or False : fits each dataset to a characteristic fcn.
        Will not display if <normalise_y_axis> != False, BUT DOES EFFECT FIGURE OUTPUT. see (6)
    12) save_dir = 'C://path//to//save//directory' or 'cwd'
    13) save_string = filename to save as. Default is '<y_label>_<x_label>_<date>'
    14) save_fitDataString = filenames to save the fit parameters into. Defaults to False
    
    OUTPUTS:
    1) Figures saved as image files in the save directory
    2) Return dict of fit parameters or None if fit_curves == False    
    3) Save excel workbook of fit parameters if save_fitDataString != False
    
    @author: dn1847
    """
    import os
    import numpy as np    
    import matplotlib.pyplot as plt
    #import matplotlib.ticker as ticker
    from openpyxl import Workbook
    from scipy.optimize import curve_fit
    import itertools
    from make_save_string import make_save_string
    from graphingtools import trim_name, short_name
    
    #--------------------------------------------------------------------------
    # INPUTS
    # 1) x, y, T data. Lists of lists of data,
    # i.e. x_data = [[x0-xn1], [x0-xn2], ..., [x0-xnN]]
    #      y_data = [[y0-yn1], [y0-yn2], ..., [y0-ynN]]
    # 2) fit_curves = 'R_vs_f' or False : fit each dataset to named fcn.
    # 3) num_curves = int(1-N) or 'all' : use evenly spaced subset of datasets.
    # 4) save_dir = 'C://path//to//save//directory' or 'cwd'
    # 5) save_string = 'name_to_save_the_fig_as', or False --> don't save fig
    #--------------------------------------------------------------------------
    
    # file i/o:
    T_data = T_datasets
    if save_dir == 'cwd':
        save_dir = os.getcwd()
    else:
        save_dir = save_dir

    if type(filter_temps) in [int, float]:
        filter_temps = [filter_temps]
    elif type(filter_temps) == str:
        if filter_temps != 'all':
            print('''ENTRY NOT RECOGNISED for variable <filter_temps>:
                <filter_temps> = {}
                  ---> Setting <filter_temps>=\'all'.'''.format(filter_temps))
    elif type(filter_temps) in [list, np.ndarray, tuple]:
        for i in filter_temps:
            if not type(i) in [int, float]:
                print('''NON-NUMERIC ENTRY found in <filter_temps> variable:
                    <filter_temps> = {0}, of type {1}.
                  ---> Setting <filter_temps>=\'all\'.'''.format(filter_temps, type(i)))
                filter_temps = 'all'
    elif filter_temps == []:
        filter_temps = 'all'
    else:
        print('''ENTRY NOT RECOGNISED for variable <filter_temps>:
            <filter_temps> = {0}, of type {1}.
              <filter_temps> must be either:
                  -a list of int or float values,
                  -the string 'all'.
              ---> Setting <filter_temps>=\'all\'.'''.format(filter_temps, type(filter_temps)))
        filter_temps = 'all'
    if T_datasets == None:
        filter_temps = 'all' 
        
    if normalise_y_axis not in [False, 'False']:
        y_multiplier = 1
        norm_const = np.inf # a high number - we use it to start a minimisation later
    #--------------------------------------------------------------------------
    # PROCESSING
    # 1) Define the fit functions
    # 2) Make labelling lambda functions
    # 3) Set up plotting colours / lines / markers cycles
    # 4) Collect indices of datasets to print (if num_curves != len(y_data):)
    # 5) Create axes
    # 6) For each chosen index: 
    # 6a) Fit curve (if fit_curves != False:)
    # 6b) Plot datasets and fit curves if applicable
    # 7) Add legend
    # 8) Scale axes to fit legend 
    #--------------------------------------------------------------------------
    
    # 1) fit functions to correspond with scipy.curve_fit()
    # define function of curve we want to fit, independent variable first:
    def funcR(f, rdc, f0, n):
        return rdc*(1 + (f/f0)**n) # R(f) = Rdc*(1+(f/f0)**n)
#    def funcRdc(f, rdc, f0, n):
#        return np.linspace(rdc,rdc,num=len(f)) # Rdc(f) = Rdc
#    def funcRac(f, rdc, f0, n):
#        return rdc*((f/f0)**n) # Rac(f) = Rdc*(f/f0)**n
        
    #storage for the optimisation parameters like {temp : [rdc, f0, n]}
    fit_params = {}
    
    # 2) Legend labelling fcns
    #uses fnction short_name from graphingTools.py
    
    if short_legend_tags[0] in [False, None] and short_legend_tags[1] in [False, None]:
        name_label = lambda i: 'Coil: %s, ' % (data_ids[i])
    else:
        omit_tags = [False, False]
        flagEnds = [0, 0]
        if '!!' in short_legend_tags[0][:3]: #do not include tag in the label
            omit_tags[0] = True
            flagEnds[0] = 3
        if '!!' in short_legend_tags[1][:3]:
            omit_tags[1] = True
            flagEnds[1] = 2
        
        short_legend_tags[0] = short_legend_tags[0][flagEnds[0]:]
        short_legend_tags[1] = short_legend_tags[1][flagEnds[1]:]
        # name_label = lambda i: 'Coil: %s, ' % (short_name(data_ids[i], short_legend_tag, omit_tag, reverse_trim, keep_trailing_num=False))
        name_label = lambda i: 'Coil: %s, ' % (trim_name(data_ids[i], short_legend_tags, omit_tags, keep_trailing_num=False))
        
    
    #lambda to get the temperature for each legend label
    if T_data != None:
        temp_label = lambda i: 'Rac|T=%.1f C' % (np.mean(T_data[i]))
    else:
        temp_label = lambda i: ''
    rdc_temp_label = lambda i: 'Rdc_component|T=%.1f C' % np.mean(T_data[i])
    rac_temp_label = lambda i: 'Rac_component|T=%.1f C' % np.mean(T_data[i])
    
    # 3) plotting setup
    #setup colours
    #generate a colourmap for the traces
    #see the colourmaps at https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html
    #colour_cycle = cm.get_cmap('tab20', len(y_datasets))
    colour_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    marker_cycle = itertools.cycle(('x', '^', '+', '.'))    
    
    # 4) choose which datasets to plot  
    # filter by temperature
    if filter_temps != 'all':
        use_datasets = [] # indices of datasets to use
        av_data_temps = [int(round(np.mean(t_list))) for t_list in T_data]
        for i in range(len(av_data_temps)):
            for ifilter in filter_temps:
                t_low, t_hi = ifilter*0.9, ifilter*1.1 # allow range around nominal temp
                if t_low <= av_data_temps[i] <= t_hi:
                    use_datasets.append(i)
        if len(use_datasets) == 0: #it's empty
            print('''ZERO USEABLE TEMPERATURES FOUND AFTER FILTERING.
              filter: <filter_temps> = {0},
              available temps: {1}.
              ---> Setting <filter_temps> = 'all'.'''.format(filter_temps, av_data_temps))
            filter_temps = 'all'
    if filter_temps == 'all':
        use_datasets = [j for j in range(len(x_datasets))]
    
    #--------------------------------------------------------------------------
    # apply temp_filters to all data
    #--------------------------------------------------------------------------
    x_data = [x_datasets[d] for d in use_datasets]
    y_data = [y_datasets[d] for d in use_datasets]
    if T_data != None:
        T_data = [T_datasets[d] for d in use_datasets]
    if data_ids != None:
        data_ids = [data_ids[d] for d in use_datasets]
        
    if num_curves == 'all': # plot them all
        num_curves = len(y_data)
    else: # plot a subset of <num_curves> of the included datasets
        pass #num_curves = num_curves
        
    # line_indices correspond to the indices in x_data, y_data, T_data
    line_indices = np.linspace(0, len(y_data)-1, num=num_curves, dtype='int')
    ctmp = None #to check for duplicates in line_indices

    # 5)----------create the axes------------#
    #set font sizes
    SMALL_SIZE = 24 #12 #8
    MEDIUM_SIZE = 28 #14 #10
    BIGGER_SIZE = 36 #18 #12
    
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    
#    fig, ax = plt.subplots(figsize=(12,9))
    fig = plt.figure(figsize = (9,9)) #figsize is in inches, default = (6.4, 4.8)
    # ax = fig.add_axes([0, 0, 1, 1]) #([x0, y0, xwidth, ywidth])
    ax = fig.add_subplot(111)
    
    for c in line_indices:
        if c == ctmp:
            #same file number ==> skip it
            #DEBUGGING
            #print('c=%d, ctmp=%d, skipping' %(c, ctmp))
            continue
        #DEBUGGING
        #print('line_indices = ', line_indices)
        #DEBUGGING
        #print('c: %d, line_indices[c]: %d, line_indices[c-1]: %d' % (c, line_indices[c], line_indices[c-1]))
        popt = [None]
        if fit_curves not in [False, 'False']:
            if fit_curves == 'R_vs_f':
                fit_func = funcR
            # 6a) Fit curves to get y-intercept (RDC)
            #where popt = array([rdc, f0, n]) w.r.t. funcR above
            popt, pcov = curve_fit(fit_func, x_data[c], y_data[c])
            fit_params[c] = [popt, pcov] #store fit params
            fit_label = 'Rdc=%.2g m$\Omega$, fo=%.2f kHz, n=%.2g' % (popt[0]*10.**3, popt[1]/1000., popt[2])
        col = colour_cycle[np.where(line_indices == c)[0][0] % len(colour_cycle)]
        imarker = next(marker_cycle)
        
        if normalise_y_axis not in [False, 'False']:
            if type(normalise_y_axis) in [int, float]:
                #norm to this value
                y_norm = normalise_y_axis
                print('Normalising y data to user value: ', y_norm)
                y_label = 'R / %.1e' % (y_norm)
            elif normalise_y_axis == 'min':
                #norm to the lowest y value available
                if norm_const == np.inf: #haven't set the min yet
                    y_gen = (min(y_data[i]) for i in line_indices)
                    for imin in y_gen:
                        if imin < norm_const:
                            norm_const = imin
                y_norm = norm_const
                print('Normalising y data to lowest y value found: ', y_norm)
                y_label = 'R [normalised]'#'R / %.1e (lowest y value)' % (y_norm)
            elif normalise_y_axis == 'av':
                #norm to the average of the curves' first y-data points
                if norm_const == np.inf: #haven't set the average yet
                    first_points = [y_data[cc][0] for cc in line_indices]
                    norm_const = np.mean(first_points)
                y_norm = np.mean(first_points)
                print('Normalising y data to average of first points of all curves: ', y_norm)
                y_label = 'R / %.1e (average of first points)' % (y_norm)
            elif normalise_y_axis == 'first':
                #norm to the first point in each series
                y_norm = y_data[c][0]
                print('Normalising y data to first point in each data series: ', y_norm)
                y_label = 'R [normalised]'
            elif popt[0] != None:
                #norm to first entry in popt
                y_norm = popt[0]
                print('Normalising y data to y-intercept of each curve: ', y_norm)
                y_label = 'Rac / Rdc'
                #y_data[c] = [y/popt[0] for y in y_data[c]]
            else:
                if c == 0: #this is the first datapoint - use it to norm the rest
                    y_norm = y_data[c][0]
                print('Normalising y data to first available datapoint, in first available curve: ', y_norm)
                y_label = 'Z [normalised]'#'R / %.1e (first point in Coil 01)' % (y_norm)
                
            y_data[c] = [y/y_norm for y in y_data[c]]
            
            #Re-fit the curves to the normalised data
#            popt, pcov = curve_fit(fit_func, x_data[c], y_data[c])
#            fit_params[c] = popt
#            fit_label = 'Rdc=%.2g m$\Omega$, fo=%.2f kHz, n=%.2g' % (popt[0]*10.**3, popt[1]/1000., popt[2])


        # 6b) plot dataset and fit curve
        ax.plot(x_data[c], [y_val*y_multiplier for y_val in y_data[c]], marker=imarker, color=col, linestyle='None', label=(name_label(c)))
        if fit_curves == 'R_vs_f' and normalise_y_axis in [False, 'False']:
            ax.plot(x_data[c], funcR(x_data[c], *popt)*10**3, color=col, label=fit_label)
    #    ax_r_t.plot(x_data[c], funcRdc(x_data[c], *popt)*10**3, color=col, linestyle=':', label=rdc_temp_label(c))
    #    ax_r_t.plot(x_data[c], funcRac(x_data[c], *popt)*10**3, color=col, linestyle='--', label=rac_temp_label(c))
        #ax_L_t.plot(x_data[c], l_array[c]*10**6, marker='x', linestyle='None', label=temp_label(c))
        ctmp = c #to check for duplicate entries in line_indices
    
    #theoretical resistance markers
    print_horizontal_lines = False
    if print_horizontal_lines:
        rdc_broken_strands = {
                'labels' : ['3 broken strands', '2 broken strands', '1 broken strand', '8 strands intact'],#['7 broken strands', '6 broken strands', '5 broken strands', '4 broken strands', 
                'resistances' : [7.4, 6.2, 5.3, 4.6],#[36.9, 18.5, 12.3, 9.2, 
                'line_style' : ['-', '--', '-.', ':'],
                'line_col' : ['red', 'orange', 'green', 'blue']
                }
        for irdc in np.arange(len(rdc_broken_strands['labels'])):
            ax.axhline(y=rdc_broken_strands['resistances'][irdc],
                       linestyle=rdc_broken_strands['line_style'][irdc],
                       color=rdc_broken_strands['line_col'][irdc],
                       linewidth='1',
                       label=rdc_broken_strands['labels'][irdc])
    
    # 7) sort out the legend and labels
    ax.legend(loc='center left', bbox_to_anchor=(1,0.5), title=legend_header)
    #ax.legend()
    #ax.set_ylim(2.5,18.5)
#    ax.set_xlim(0)
#    ax.set_ylim([None, None])#([3., 8.])#([60, 90])#([16.5, 19.5])#([0.5, 6])#
    #ax.tick_spacing = 1
    #ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.grid(visible=True, which='major', linestyle='-', alpha = 0.2)
    ax.set_xlabel(x_label, labelpad=5)
    ax.set_ylabel(y_label, labelpad=5)
    #ax.set_position([0.125, 0.125, 0.7, 0.9])
    #ax_L_t.set_xlabel('Frequency [Hz]')
    #ax_L_t.set_ylabel('L [$\mu$H]')
    plt.show()
    #plt.close()
    


    #--------------------------------------------------------------------------
    # OUTPUTS:
    # 1) Figures saved as image files in the save directory
    # 2) Return dict of fit parameters or None if fit_curves == False  
    #--------------------------------------------------------------------------
    if save_string != False:
        if save_string == 'default':
            save_string = make_save_string([y_label, x_label], date_stamp=True)
        print('saving figure as: ', save_string)
        print('save directory: ', save_dir)
    
        save_fname = os.path.join(save_dir, save_string)
        fig.savefig(save_fname, dpi=300, transparent=False, bbox_inches='tight')
        fig.savefig('%s.pdf' %save_fname, format='pdf', transparent=False, bbox_inches='tight')
            
        # fig.savefig(save_dir+'\\'+save_string+'.jpg', dpi=300)
        # fig.savefig(save_dir+'\\'+save_string+'.pdf')
        #fig_L_t.savefig(data_folder+'\\L_vs_t.jpg', dpi=300)
        #fig_L_t.savefig(data_folder+'\\L_vs_t.pdf')
    
    if save_fitDataString != False:
        fitData_fname = os.path.join(save_dir, save_fitDataString)
        wb = Workbook()
        wb_fname = fitData_fname
        
        ws1 = wb.active
        ws1.append(['Curve fitting data for compressed coil impedance sweep tests.'])
        ws1.append(['fit equation: R = Rdc(1+(f/f0)^n)'])
        ws1.append(['fit using scipy.optimize.curve_fit (non-linear least squares)'])
        ws1.append(['params returned as 3x1 array:'])
        ws1.append(['pars = [Rdc, f0, n]'])
        ws1.append(['covariance matrix returned as 3x3 array on the fitting params'])
        ws1.append(['cov = [ 3x3 ]'])
        ws1.append(['stdevs of the fitting params found from sqrt of cov diagonals:'])
        ws1.append(['stdevs = np.sqrt(np.diag(cov))'])
        ws1.append(['---------------------------'])
        
        for idata in fit_params.keys():
            pars,cov = fit_params[idata]
            parList = [i for i in pars]
            covList0 = [j for j in cov[0]]
            covList1 = [jj for jj in cov[1]]
            covList2 = [jjj for jjj in cov[2]]
            stdevs = np.sqrt(np.diag(cov))
            ws1.append(['curve id:', str(idata)])
            ws1.append(['pars ='])
            ws1.append([i for i in parList])
            ws1.append(['cov ='])
            ws1.append([j for j in covList0])
            ws1.append([jj for jj in covList1])
            ws1.append([jjj for jjj in covList2])
            ws1.append(['stdevs ='])
            ws1.append([k for k in stdevs])
            ws1.append(['--- --- ---'])
            ws1.append([''])
        
        wb.save(filename = f'{wb_fname}.xlsx')
            
        
    plt.close(fig)
    #plt.close(fig_L_f)
    
    if fit_curves not in [False, 'False']:
        return fit_params
    else:
        return None
    
    