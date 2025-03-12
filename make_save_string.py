# -*- coding: utf-8 -*-
def make_save_string(list_strings, date_stamp=False, time_stamp=False):
    """
    Concatenates the strings in <list_strings>, removes units, replaces spaces
    with underscores, adds a datestamp.
    
    Created on Fri Apr 26 12:28:04 2019
    
    @author: dn1847
    """
    
    from datetime import datetime
    
    #check inputs
    if type(list_strings) == str:
        list_strings = [list_strings]
    
    if type(list_strings) in [list, tuple]:
        #get each item
        for s in range(len(list_strings)):
            istr = list_strings[s]
            #remove units if units are in (brackets)
            istr = istr.split('[')[0]
            istr = istr.split('(')[0]
            istr = istr.split('{')[0]
            #strip whitespace
            istr = istr.strip()
            #replace spaces with underscores
            istr = istr.replace(' ', '_')
            #return istr to the list
            list_strings[s] = istr
        
        newstr = '_'.join(list_strings)
        
        if date_stamp or time_stamp == True:
            dt = datetime.today()
        if date_stamp == True:
            #get a datestamp
            d = dt.strftime('%d-%m-%Y')
            newstr = newstr + '_' + d
        if time_stamp == True:
            #get the timestamp
            t = dt.strftime('%H-%M-%S')
            newstr = newstr + '_' + t
        
        return newstr