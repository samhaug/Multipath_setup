#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : az_split.py
Purpose : split data up into multiple azimuth bins for easy viewing
Creation Date : 24-05-2017
Last Modified : Wed 24 May 2017 09:54:16 AM EDT
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
from sys import argv

def main():
    st = read_stream()
    az_bins = [(320,330),(330,340),(340,350),(350,360),(360,370)]
    for ii in az_bins:
        copy_write(st,ii)

def read_stream():
    st = obspy.read('*BXR*')
    st.normalize()
    for tr in st:
        if tr.stats.sac['az'] < 250:
            tr.stats.sac['az'] += 360
    return st

def copy_write(st,az_bin):
    st1 = st.copy()
    st1 = seispy.filter.az_filter(st1,az_bin)
    st1.write('az_{}_{}.pk'.format(az_bin[0],az_bin[1]),format='PICKLE')

main()
