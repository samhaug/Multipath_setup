#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : multipath_detect.py
Purpose : multipath detector similar to Sun and Helmberger
Creation Date : 22-05-2017
Last Modified : Mon 22 May 2017 07:44:06 PM EDT
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
import scipy

def main():
    st_syn = obspy.read('/home/samhaug/work1/Multipath_sims/PROC_031011G/*sac*')
    st_syn.interpolate(30)
    for tr in st_syn:
        tr.stats.location = tr.stats.sac['gcarc']
    st_syn.sort(['location'])
    gf = seispy.data.phase_mask(st_syn[0],phase=['S'],window_len=13)
    wave = gf.copy()
    wave.data = np.roll(gf.data+np.roll(gf.data,int(6*gf.stats.sampling_rate)),int(0*gf.stats.sampling_rate))
    fit_multipath(wave,gf)

def read_waveforms(st_path):
    st = obspy.read(st_path)
    for idx,tr in st:
        #tr.stats.sac['o'] = obspy.UTCDateTime('2011-03-10 17:08:37')-tr.stats.starttime
        st[idx] = seispy.data.phase_window(tr,phase=['S'],window=(-20,20))
    return st

def fit_multipath(wave,gf):
    gf_sr = gf.stats.sampling_rate

    def misfit(x):
        trial = np.roll(gf.data+np.roll(gf.data,int(np.exp(x[0])*gf_sr)),int(x[1]*gf_sr))
        return np.sum((trial-wave)**2)

    sol = scipy.optimize.fmin(misfit,[6.3,0.3])
    print sol
    final = np.roll(gf.data+np.roll(gf.data,int(sol[0]*gf_sr)),int(sol[1]*gf_sr))

    plt.plot(final)
    plt.plot(wave.data)
    plt.show()

def mcmc_fit_multipath(wave,gf):
    wave_sr = wave.stats.sampling_rate
    gf_sr = gf.stats.sampling_rate
    LR_array = np.linspace(0,30,num=100)
    shift_array = np.linspace(-20,20,num=100)
    misfit = np.zeros((len(LR_array),len(shift_array)))
    for idx,ii in enumerate(LR_array):
        for ijx,jj in enumerate(shift_array):
            trial = np.roll(gf.data,int(jj*gf_sr))+np.roll(gf.data,int((ii+jj)*gf_sr))
            misfit[idx,ijx] = np.sum((wave.data-trial)**2)
    print np.min(misfit,axis=(1,0))
    return misfit

main()
