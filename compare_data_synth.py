#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : compare_data_synth.py
Purpose : align data and synthetic
Creation Date : 08-05-2017
Last Modified : Mon 08 May 2017 04:41:17 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import pylab as p
from subprocess import call
from os import listdir
import h5py
import obspy
import seispy

def main():
    std = read_pickle('/home/samhaug/work1/Multipath_data/020213E_sac/13_25_original.pk')
    std.filter('lowpass',freq=1/2.,zerophase=True)
    std.normalize()
    sts = read_pickle('/home/samhaug/work1/Multipath_sims/020213_triplication/13_25.pk')
    std.sort(['station'])
    sts.sort(['station'])
    print len(std),len(sts)
    for idx,tr in enumerate(std):
        plot_compare(tr,sts[idx])

def read_pickle(file_path):
    st = obspy.read(file_path)
    st.interpolate(50)
    st.integrate()
    for idx,tr in enumerate(st):
        st[idx] = seispy.data.phase_window(tr,['S'],window=(-100,100),model='prem')
    st.normalize()
    return st

def plot_compare(trdata,trsynth):
    print trdata.stats.station,trsynth.stats.station
    fig,ax = plt.subplots(figsize=(10,5))
    t = np.linspace(-100,100,num=trdata.stats.npts)
    plt.plot(t,trdata.data,label='data',color='k')
    plt.plot(t,trsynth.data,label='sim',color='r')
    dragh = DragHandler(trdata)
    plt.show()
    return trdata.stats.station,dragh.shift

class DragHandler(object):
    """ A simple class to handle Drag n Drop.

    This is a simple example, which works for Text objects only.
    """
    def __init__(self, tr) :
        figure = p.gcf()
        # simple attibute to store the dragged text object
        self.shift = 0
        self.dragged = None
        self.srate = tr.stats.sampling_rate

        # Connect events and callbacks
        figure.canvas.mpl_connect("pick_event", self.on_pick_event)
        figure.canvas.mpl_connect("button_release_event", self.on_release_event)

    def on_pick_event(self, event):
        #print type(event.artist.get_label())

        if event.artist.get_label() == 'sim':
            self.dragged = event.artist
            self.xdata = event.artist.get_data()[0]
            self.ydata = event.artist.get_data()[1]
            self.pick_pos = event.mouseevent.xdata
        return True

    def on_release_event(self, event):

        newx = event.xdata
        try:
            newy = np.roll(self.ydata,int((newx-self.pick_pos)*(self.srate)))
            self.dragged.set_data(self.xdata,newy)
            self.dragged = None
            p.draw()
            self.shift = (newx-self.pick_pos)*self.srate
            return True
        except (AttributeError,TypeError):
            return True

main()
