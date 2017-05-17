#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : stack_cluster.py
Purpose : stack waveforms in similar distance range.
Creation Date : 09-05-2017
Last Modified : Wed 10 May 2017 11:12:43 AM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from subprocess import call
from os import listdir
import h5py
import obspy
import seispy

def main():
    st = read_data('/home/samhaug/work1/ScS_reverb_data/031011G_sac/az_350_370.pk')
    #st = read_data('/home/samhaug/work1/Multipath_sims/031011G_prem/clean_R.pk')
    range_dict = bin_traces(st)
    new_st = stack_traces(range_dict)
    seispy.plot.simple_section(new_st)
    for tr in new_st:
        tr.stats.sac['evdp'] = st[0].stats.sac['evdp']
    new_st.write('/home/samhaug/work1/ScS_reverb_data/031011G_sac/binned.pk',format='PICKLE')
    #new_st.write('/home/samhaug/work1/Multipath_sims/031011G_prem/binned.pk',format='PICKLE')

def read_data(data_path):
    print 'read_data'
    st = obspy.read(data_path)
    #st = seispy.filter.az_filter(st,(350,370))
    #st.integrate().normalize()
    #st.filter("highpass",freq=1./50,zerophase=True)
    #st = seispy.filter.gimp_filter(st)
    st.interpolate(50)
    for idx,tr in enumerate(st):
        st[idx] = seispy.data.phase_window(tr,['S'],window=(-300,200))
    return st

def bin_traces(st):
    a = []
    for tr in st:
        a.append(tr.stats.sac['gcarc'])
    a = np.unique(np.round(np.array(a)*2)/2)

    range_dict = {}
    for ii in a:
        range_dict[ii] = []
        for tr in st:
            gcarc = tr.stats.sac['gcarc']
            if np.round(gcarc*2)/2 == ii:
                range_dict[ii].append(tr.data)
    return range_dict

def stack_traces(range_dict):
    st = obspy.core.stream.Stream()
    for keys in range_dict:
        try:
            tr = obspy.core.trace.Trace()
            tr.stats.sampling_rate = 50
            tr.stats.sac = {}
            tr.stats.sac['gcarc'] = float(keys)
            tr.stats.sac['o'] = 0
            tr.data = np.mean(range_dict[keys],axis=0)
            st.append(tr)
        except ValueError:
            continue
    return st

main()



