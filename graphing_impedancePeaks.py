# -*- coding: utf-8 -*-
"""
read in the data from excel or csv sheets and graph it.
Works with multi-column data, choose one column as the x axis, denoted by its
column header string
Fit equation-defined curves to the datasets and calculate their parameters,
e.g. fit function R = Rdc*(1+(f/f0)**n) for R(f) in concentrated coils
"""

from graphingtools import short_name, read_in_data
from graphingtools import get_csv_data_WK6500B, get_excel_data
from make_save_string import make_save_string
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from numpy import pi as PI
from numpy import arange, exp
from openpyxl import Workbook
# from pylab import cm # pylab is deprecated. colourmaps are from matplotlib
from rlft_plotter import rlft_plotter
from scipy.optimize import curve_fit
#import itertools
import os

#==============================================================================
#==============================================================================
# USER INPUT HERE
#==============================================================================
#==============================================================================

#It is useful to mess with the parameters until a good fig is produced. When 
#happy with it, change the below to 'True'
save_figs = True #False #
save_fitData = False #True #
av_freqs = False #Take average of multiple readings at each set frequency?
file_save_prefix = '' #optional prefix to file savenames
legend_header = 'Phase windings\nPitch: 12tpm'
short_legend_tag = True #True#False #'tpm'# #Deletes everything after this string in the legend tags. begin string with '!!' to delete the string too.
convert_Z = False #'R' #'X' #convert from Z(f) and PHI(f) in the data to either 'R'esistance(f) or 'X'reactance(f). or False if unwanted

#THE DATA TO READ
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\2S_phase_15MHz\\core-no-core\\Core00'
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\2S_phase_2kHz\\core-no-core\\core00'
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\2S_phase_2kHz\\core-no-core\\2S_extras_0-2kHz'

data_root = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis'
# data_file = '2S_phase_2kHz\\core-no-core\\core00'
data_file = '2S_phase_15MHz\\core-no-core\\Core00'
# data_file = '2S_phase_2kHz\\core-no-core\\2S_extras_0-2kHz' 
#data_file = '2S_phase_2kHz\\2S_no-core_full-set_FINAL'
data_folder = os.path.join(data_root, data_file)

file_type = 'csv' # 'excel' #
if file_type == 'excel':
    excel_fname = 'dcTransient_motorette2_75ADC_6_20_2019.xlsx' #R_vs_f.xlsx'
    excel_sheetNames = ['avTC_data'] #'all'
else:
    excel_fname = None
    excel_sheetNames = None
    
#THE DATA TO PLOT:
# This string and list of strings should match column headers in the data file
x_data_header = 'Frequency (Hz)' # Column header from the data file
y_data_list = ['Meas. Impedance (O)'] #'Meas. Impedance (O)']
               #'Calc. Reactance (O)'] #'Calc. Resistance (O)' used when convert_Z == 'R' above
                #
                #'Calc. Reactance (O)'] #'Calc. Reactance (O)' used when convert_Z == 'X' above
                # 'Meas. Impedance (O)']
               # 'Meas. Angle (°)',
               # 'Meas. Resistance (O)',
               # 'Meas. Inductance (H)']
                
#entries in this list will be used a legend entries. The indices should 
#correspond to those in y_data_list above
y_legend_list = ['Impedance [$\Omega$]'] #'Impedance [$\Omega$]']
                #
                #'Reactance [$\Omega$]']
                #'Impedance [$\Omega$]']
               # 'Ph. Angle [degrees]',
               # 'Resistance [$\Omega$]',
               # 'Inductance [H]']

data_slice = 'all' #[0:200] # graph all the datasets or a selection?

#GRAPH LAYOUT:
x_axis_label = 'Frequency [Hz]' #'Time [s]' #
y_axis_label = 'Impedance [$\Omega$]' #'Resistance [$\Omega$]' #'Reactance [$\Omega$]' #'Impedance [$\Omega$]' #'TC Temperature [degrees C]'
y_axis_multiplier = 1   #to multiply small units i.e. Ohms --> mOhms
                        
normalise_y_data = False #True True, 'min', 'av' or <numeric value>. Normalises y data
#data_labels = 'name' #MUST CORRESPOND TO A KEY IN <parameter_headers> below
#shorten_data_labels = False #'tpm'# #Deletes everything after this string in the legend tags
fit_curves = False #'R_vs_f'# False ##must be a specific name of a fit. Will not fit if <normalise_y_data> != False. See rlft_plotter.py 

#define a curve fitting function
def fit_exponential(x, a, b, c):
    return a - b*exp(c*x)

#SAVING THE DATA:
if save_figs != False:
    save_dir = data_folder
    date_stamp = True
    time_stamp = True
    save_string = make_save_string([file_save_prefix, y_axis_label, x_axis_label], 
                                   date_stamp=date_stamp, 
                                   time_stamp=time_stamp)
else:
    save_string = False

if save_fitData != False:
    save_dir = data_folder
    date_stamp = True
    time_stamp = True
    save_fitDataString = make_save_string([file_save_prefix, 'CurveFitResults', y_axis_label, x_axis_label],
                                          date_stamp=date_stamp, 
                                          time_stamp=time_stamp)
else:
    save_fitDataString = False
        

#==============================================================================
#==============================================================================
#get the data   
#==============================================================================
#==============================================================================
data_dict_list = read_in_data(data_folder, 'csv', exclude_subdirs=True, excel_fname=None, excel_sheets=excel_sheetNames, convert_Z=convert_Z, compute_freq_averages=False)

#==============================================================================
#==============================================================================
#Set up the plot figure
#==============================================================================
#==============================================================================

#set font and axis line styles
mpl.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 18
plt.rcParams['axes.linewidth'] = 2

#generate a colourmap for the traces
#see the colourmaps at https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html
colours = plt.get_cmap('tab20', max(len(y_data_list), len(data_dict_list)))

#create a new figure and add an axes object
fig = plt.figure(figsize = (9,9)) #figsize is in inches, default = (6.4, 4.8)
ax = fig.add_axes([0, 0, 1, 1]) #([x0, y0, xwidth, ywidth])

#remove the top and right spines from the axes
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

#change the axes ticks
ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in')
ax.xaxis.set_tick_params(which='minor', size=7, width=1, direction='in')
ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in')
ax.yaxis.set_tick_params(which='minor', size=7, width=1, direction='in')

#log axes?
#ax.set_yscale('log')

#set axes limits
#ax.set_xlim(0, 500)
#ax.set_ylim(10, 50)

#set the tick locations
#ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(200))
#ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
#ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(10))
#ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(5))
#ax.yaxis.set_major_locator(mpl.ticker.LogLocator(base=10.0))

#add axes labels
ax.set_xlabel(x_axis_label, labelpad=5)
ax.set_ylabel(y_axis_label, labelpad=5)

#create lambda function for the series labels
#uses fnction short_name from graphingTools.py
    
# if short_legend_tag in [False, None]:
#     name_label = lambda i: 'Coil: %s, ' % (data_ids[i])
# else:
#     if short_legend_tag[:2] == '!!': #do not include the tag in the label
#         omit_tag = True
#         reverse_trim = False #see short_name docstring
#         short_legend_tag = short_legend_tag[2:]
#     else:
#         omit_tag = False
#     name_label = lambda i: 'Coil: %s, ' % (short_name(data_ids[i], short_legend_tag, omit_tag))



#==============================================================================
#==============================================================================
#fit curves to the data and plot it!  
#==============================================================================
#==============================================================================
    
#X-axis shift?
#The data is shifted in the +ve x-axis direction, which affects the curve 
#fitting (x values are too high) for a given y. i.e. we want to 'start' the 
#x-axis at 00:00 when the y curve begins rising.
dataLen = len(data_dict_list[0][x_data_header])
y_go = 0 #69
y_end = dataLen #dataLen-10
num_points = y_end - y_go
x_go = 0 #69
x_end = x_go + num_points

#store the curve fitting params and covariance matrices,
#in the same way as the data in 'data_dict_list'
results_dict_list = [{}]

#selected ids chosen by graphing_impedancePeaks_SCRIPT.py
selected_ids_by_grad =      [1, 11, 14, 16, 17, 18, 21, 22, 24, 26, 27, 28]
selected_ids_by_zpk =       [3,  6,  8, 10, 17, 18, 21, 23, 24, 27, 28, 31]
selected_ids_by_fpk =       [1,  6,  7,  8, 10, 12, 21, 24, 25, 27, 28, 31]
#selected_ids_from_excel =   [1,  3,  8, 10, 12, 13, 19, 21, 23, 24, 25, 27]

#########################################################
##### THIS IS THE LIST OF IDs THAT WILL BE PLOTTED ######
selected_ids = selected_ids_by_grad #'all' #[19, 20, 21, '19b', '20b', '21b'] #
#########################################################

if selected_ids == 'all':
    data_ids = [i+1 for i in range(len(data_dict_list))] #zero based range
    legend_header = 'All phase windings'
else:
    data_ids = selected_ids
    
#there are multiple data files loaded into data_dict_list, as lists of dictionaries
for iDataSet in data_ids:
    print('iDataSet: ', iDataSet, ' out of ', data_ids)
    for iy in range(len(y_data_list)):
        print('iy: ', iy, ' out of ', range(len(y_data_list)))
        
        searchToken = str(iDataSet)
        if str(iDataSet)[-1].isdigit(): #in case some keys have 'b' appended
            if iDataSet < 10:
                searchToken = ('0' + searchToken)
        else:
            if int(str(iDataSet)[:-1]) < 10:
                searchToken = ('0' + searchToken)
        searchToken = ('_'+ searchToken +'_')
        
        #get the item from data_dict_list
        foundId = False
        for index in range(len(data_dict_list)):
            if searchToken in data_dict_list[index]['name']:
                foundId = index
                break
        if foundId is False:
            raise ValueError            
        
        y_data = data_dict_list[foundId][y_data_list[iy]][y_go:y_end]
        x_data = data_dict_list[foundId][x_data_header][x_go:x_end]
        # #zero base counting in data_dict_list
        # iDataSet -= 1 
        # y_data = data_dict_list[iDataSet][y_data_list[iy]][y_go:y_end]
        # x_data = data_dict_list[iDataSet][x_data_header][x_go:x_end]
        
        #get legend entry
        if short_legend_tag not in [False, None]:
            iLegend = short_name(data_dict_list[index]['name'], '_core', omit_tag=True, reverse_trim=False) #[iDataSet]['name']
            iLegend = 'Phase %s' % (short_name(iLegend, 'zth_', omit_tag=True, reverse_trim=True, keep_trailing_num=False))
        else:
            iLegend = data_dict_list[index]['name'] #[iDataSet]['name']
        
        #plot the data
        #ax.scatter(x_data, y_data, s=15, color=colours(iDataSet), label=data_dict_list[iDataSet]['name'])
        ax.plot(x_data, y_data, color=colours(index), label=iLegend)
        #ax.scatter(data_dict_list[0][x_data_header], data_dict_list[0][y_data_list[0]], s=10, color=colours(0), label=y_data_list[0])
        #ax.scatter(data_dict_list[0][x_data_header], data_dict_list[0][y_data_list[1]], s=10, color=colours(1), label=y_data_list[1])
        #ax.scatter(data_dict_list[0][x_data_header], data_dict_list[0][y_data_list[2]], s=10, color=colours(2), label=y_data_list[2])
        
        if fit_curves != False:
            p0 = None #[np.floor(y_data[-1]),0,0] #initial guess for pars
            pars, cov = curve_fit(f=fit_exponential, xdata=x_data, ydata=y_data)#, p0=p0, bounds=(-np.inf, np.inf))
            #print('pars: a,b,c = ', pars)
            results_dict_list[iDataSet][y_data_list[iy]] = pars, cov
            #add the fit curve to the axes
            ax.plot(x_data, fit_exponential(np.linspace(x_data[0], x_data[-1], len(x_data)), *pars), linestyle='--', linewidth=1.5, color='black')

#add legend
ax.legend(bbox_to_anchor=(1, 0.5), loc=6, frameon=True, fontsize=16, title=legend_header)

if save_figs != False:
    save_fname = os.path.join(data_folder, save_string)
    plt.savefig(save_fname, dpi=300, transparent=False, bbox_inches='tight')

if save_fitData != False:
    fitData_fname = os.path.join(data_folder, save_fitDataString)
    wb = Workbook()
    wb_fname = fitData_fname
    
    ws1 = wb.active
    ws1.append(['Curve fitting data for motorette DC thermal transient tests.'])
    ws1.append(['fit equation: y = a - b*exp(c*x)'])
    ws1.append(['fit using scipy.optimize.curve_fit (non-linear least squares)'])
    ws1.append(['params returned as 3x1 array:'])
    ws1.append(['pars = [a, b, c]'])
    ws1.append(['covariance matrix returned as 3x3 array on the fitting params'])
    ws1.append(['cov = [ 3x3 ]'])
    ws1.append(['stdevs of the fitting params found from sqrt of cov diagonals:'])
    ws1.append(['stdevs = np.sqrt(np.diag(cov))'])
    ws1.append(['---------------------------'])
    
    for idata in results_dict_list[0].keys():
        pars,cov = results_dict_list[0][idata]
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

plt.show()
plt.close(fig)

# if __name__ == '__main__'():
#     ddata = data_dict_list
