# -*- coding: utf-8 -*-
"""
read in the data from compressed coil AC experiment data, mainly R(f,T), and 
graph it. Fit curves to the datasets and calculate Rdc, f/f0 and n in the fit
function R = Rdc*(1+(f/f0)**n).
"""
from graphingtools import short_name, read_in_data
from get_csv_data_WK6500B import get_csv_data_WK6500B
from get_excel_data import get_excel_data
#import matplotlib.pyplot as plt
#from scipy.optimize import curve_fit
#import itertools
from rlft_plotter import rlft_plotter
from make_save_string import make_save_string
from numpy import pi as PI
from numpy import arange, any


#==============================================================================
#==============================================================================
# USER INPUT HERE
#==============================================================================
#==============================================================================

#THE DATA TO READ
###### 
# 0-2kHz single coils
######
# 0tpm - air core
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\1S_0tpm_2kHz\\0tpm_airCore_2kHz\\0tpm_RL_airCore_2kHz'
# 0tpm - iron core
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\1S_0tpm_2kHz\\0tpm_ironCore_2kHz\\0tpm_RL_ironCore_2kHz'
# 12tpm - air core
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\1S_12tpm_2kHz\\12tpm_airCore_2kHz\\12tpm_RL_airCore_2kHz_210302'
# 12tpm - iron core
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\1S_12tpm_2kHz\\12tpm_ironCore_2kHz\\12tpm_RL_ironCore_2kHz_210302'

# phase coils - air core
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\2S_phase_airCore_2kHz\\RL_2kHz'
# data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\2S_phase_2kHz\\core-no-core\\core00'
data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\2S_phase_2kHz\\2S_no-core_full-set_FINAL'

#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\0tpm_1S_2kHz\\0tpm_2kHz_airCore\\0tpm_RL_airCore_2kHz'
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\0tpm_1S_2kHz\\RL_0-2kHz\\Uncalibrated_21-02-22'
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\0tpm_1S_2kHz\\RL_0-2kHz'
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\0tpm_1S_2kHz\\Zphi_0-2kHz'
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\1S_single_airCore_2kHz\\RL_0-2kHz'
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\1S_single_airCore_2kHz\\Zphi_0-2kHz'
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\Z-f-analysis\\2S_phase_airCore_2kHz\\RL_2kHz'
#data_folder = 'C:\\Users\\dn1847\\OneDrive - University of Bristol\\PhD\\Experimental\\CompressedCoils\\Impedance_Analysis\\RacVsT\\EnvironmentalChamber'#\\Coil1_2019-03-20'
#data_folder = 'C:\\Users\\dn1847\\Local Documents\\Google Drive\\PhD\\Experimental\\Compressed Coils\\Impedance_Analysis\\RacVsPitch_BatchTesting\\12tpm_RL\\repeat'#FreeWound_RL'#
#data_folder = r'C:\Users\dn1847\Local Documents\Google Drive\PhD\Experimental\Motorette Testing\CoilImpedanceChecks\motorette2\PostManufactureChecks'

file_type = 'csv' # 'excel' #

if file_type == 'excel':
    excel_fname = 'dcTransient_motorette2_75ADC_6_20_2019.xlsx' #R_vs_f.xlsx'
    excel_sheetNames = ['avTC_data'] #'all'
else:
    excel_fname = None
    excel_sheetNames = None

convert_Z = 'R' #False #'X' #convert from Z(f) and PHI(f) in the data to either 'R'esistance(f) or 'X'reactance(f). or False if unwanted

#THE DATA TO PLOT:
x_axis = 'frequency' #MUST CORRESPOND TO A KEY IN <parameter_headers> below
y_axis = 'resistance' #MUST CORRESPOND TO A KEY IN <parameter_headers> below
temperature_data = 'temperature' #MUST CORRESPOND TO A KEY IN <parameter_headers> below
HOW_MANY_DATA_FILES = 'all' # graph all the datasets or a selection?
TEMPERATURES_TO_PLOT = 'all'#[25,100] # #only plot data from these temperatures
TRIM_EARLY_DATA = 5 #Trim first X datapoints - there is often noise in low-f measurements on some DAQs


#GRAPH LAYOUT:
x_axis_label = 'Frequency [Hz]'
#y_axis_label = 'Resistance [m$\Omega$]'#'Inductance [$\mu$H]'#'Impedance [m$\Omega$]'#'Angle [degrees]'#
#y_axis_multiplier = 10**3 #1 #to multiply small units i.e. Ohms --> mOhms
normalise_y_data = True #'av' #False, 'min', 'av', 'first', <numeric value> or (True when fit_curves != False). Normalises y data.
data_labels = 'name' #MUST CORRESPOND TO A KEY IN <parameter_headers> below
shorten_data_labels = ['!!zth_', '!!_core'] #[None, None] #[None, 'tpm'] #Trims the legend entries by deleting everything before the first and after the second string.
#begin string with '!!' or 'r!!' to delete the string too. 
legend_header = 'phase windings'
fit_curves = 'R_vs_f'#False # #must be a specific name of a fit. Will not fit if <normalise_y_data> != False. See rlft_plotter.py 
plot_fitcurves = True #plot the trend lines fit by the function in fit_curves
plot_data = True #plot the data points? Can be set false with plot_fitcurves = True to only plot fit curves
y_axis_label = {
        'resistance' : 'Resistance [m$\Omega$]',
        'impedance' : 'Impedance [m$\Omega$]',
        'inductance' : 'Inductance [$\mu$H]',
        'phi' : 'Angle [degrees]'
        }.get(y_axis)
y_axis_multiplier = { #to multiply small units i.e. Ohms --> mOhms
        'resistance' : 10**3,
        'impedance' : 10**3,
        'inductance' : 10**6,
        'phi' : 1
        }.get(y_axis)

#SAVING THE DATA:
save_dir = data_folder
date_stamp = True
time_stamp = True
save_string = make_save_string([y_axis_label, x_axis_label], date_stamp=date_stamp, time_stamp=time_stamp) #False #
save_fitDataString = make_save_string(['CurveFitResults', y_axis_label, x_axis_label], date_stamp=date_stamp, time_stamp=time_stamp) #False #save_fitDataString = 
#==============================================================================
#==============================================================================


#list keys for the parameters we want
parameter_headers = {
        'name' : ['name', 'id'],
        'frequency' : ['freq', 'freq1'],
        'resistance' : ['Rs1', 'Resistance'],
        'reactance' : ['X1', 'Reactance'],
        'phi' : ['phi', 'angle', 'phi 1', 'phi1'],
        'inductance' : ['L1', 'Inductance'],
        'impedance' : ['Z1', 'Impedance'],
        'temperature' : ['temp', 'temperature']
        }

parameter_datasets = {k : [] for k in parameter_headers.keys()} #keys match

#get the data   
# if file_type == 'csv':
#     data_dict_list = get_csv_data_WK6500B(num_files='all', data_folder=data_folder)   
    
# elif file_type == 'excel':
#     data_dict_list = get_excel_data(filename=excel_fname, sheetNames='all', data_folder=data_folder, compute_freq_averages=True)

data_dict_list = read_in_data(data_folder, file_type, exclude_subdirs=True, excel_fname=None, excel_sheets=excel_sheetNames, convert_Z=convert_Z, compute_freq_averages=False)

#sort the data into arrays of x_data, y_data and T_data
#frequency_data, resistance_data, reactance_data, phi_data, temperature_data= [], [], [], [], []
for d in data_dict_list:              
    for p_key in parameter_headers.keys():
        found = 0 #flag
        for param in parameter_headers[p_key]:
            if found == 0:
                for d_key in d.keys():
                    if 'EC' in d_key: #ignore the Equivalent Circuit data
                      continue  
                    elif param.casefold() in d_key.casefold():
                        found = 1
#                        print('found <%s> in data header <%s>' %(param, d_key))
                        parameter_datasets[p_key].append(d[d_key])
                        break
        if found == 0:
            parameter_datasets[p_key].append(None)
    
    #if reactance is recorded instead of inductance, calculate inductance.
    if None in parameter_datasets['inductance'] and None not in parameter_datasets['reactance']:
        print('INDUCTANCE not found in datafile. Calculating based on REACTANCE (assumed purely inductive)')
        for i in range(len(parameter_datasets['frequency'])):
            fX_tuples = zip(parameter_datasets['frequency'][i], parameter_datasets['reactance'][i])
            parameter_datasets['inductance'][i] = [reac/(2*PI*freq) for freq, reac in fX_tuples]
    
#Trim early data points if desired
if TRIM_EARLY_DATA not in [False, None, '']:
    print('Trimming the first <%d> datapoints from each series, because parameter <TRIM_EARLY_DATA> is set to <%d>.' %(TRIM_EARLY_DATA, TRIM_EARLY_DATA))
    for ikey in parameter_datasets.keys():
        if ikey.casefold() not in parameter_headers['name']:
            #do not trim the series name or id
            #do trim all the data values
            try:
                for iseries in range(len(parameter_datasets[ikey])):
                    if any(parameter_datasets[ikey][iseries]):
                        parameter_datasets[ikey][iseries] = parameter_datasets[ikey][iseries][TRIM_EARLY_DATA:]
            except TypeError as err:
                    print('Skipping data series with key <%s> due to error:\n%s' %(ikey, err))



#------------------------------------------------------------------------------
# got the data, now plot it
#------------------------------------------------------------------------------

# some files may not contain the correct data. Trim them now
data_indices = []
check_data = parameter_datasets[y_axis]
for y in arange(len(check_data)):
    if any(check_data[y]): #check_data[y] != None:
        data_indices.append(y)

fit_params = rlft_plotter(x_datasets = [parameter_datasets[x_axis][i] for i in data_indices],
                          y_datasets = [parameter_datasets[y_axis][i] for i in data_indices],
                          T_datasets = [parameter_datasets[temperature_data][i] for i in data_indices],
                          x_label = x_axis_label,
                          y_label = y_axis_label,
                          y_multiplier = y_axis_multiplier,
                          normalise_y_axis = normalise_y_data,
                          short_legend_tags = shorten_data_labels,
                          legend_header = legend_header,
                          data_ids = [parameter_datasets[data_labels][i] for i in data_indices],
                          filter_temps = TEMPERATURES_TO_PLOT,
                          num_curves = HOW_MANY_DATA_FILES,
                          fit_curves = fit_curves,
                          plot_fitcurves = plot_fitcurves,
                          plot_data = plot_data,
                          save_dir = data_folder,
                          save_string = save_string,
                          save_fitDataString = save_fitDataString)

print(fit_params)
