#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : manually_align_delete.py
Purpose : delete and align by hand.
Creation Date : 04-05-2017
Last Modified : Mon 08 May 2017 01:32:52 PM EDT
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
from obspy.taup import TauPyModel
model = TauPyModel(model='prem')

def main():
    st = obspy.read('/home/samhaug/work1/Multipath_data/020213E_sac/13_25.pk')
    st = st[::4]
    seispy.mapplot.plot(st)
    st = seispy.data.align_on_phase(st,phase=['S'],min=False)
    st.interpolate(40)
    st.normalize()
    simple_section(st,a_list=['S'],section_type='dist')
    dragh = DragHandler(st)
    plt.show()
    for tr in st:
        stat = tr.stats.station
        try:
            if stat in dragh.station:
                i = dragh.station.index(stat)
                tr.data = np.roll(tr.data,int(dragh.shift[i]*tr.stats.sampling_rate))
            else:
                continue
        except IndexError:
            continue
    st.write('/home/samhaug/work1/Multipath_data/020213E_sac/13_25_align.pk',format='PICKLE')

def simple_section(st,**kwargs):
    '''
    Simpler section plotter for obspy stream object
    '''
    a_list = kwargs.get('a_list',True)
    fig = kwargs.get('fig',None)
    ax = kwargs.get('ax',None)
    color = kwargs.get('color','k')
    save = kwargs.get('save',False)
    picker = kwargs.get('picker',False)

    sec_type = kwargs.get('section_type','az')
    if sec_type == 'az':
        for tr in st:
            tr.stats.azimuth = tr.stats.sac['az']
        st.sort(['azimuth'])
    st = st[::-1]


    if fig == None and ax == None:
        fig,ax = plt.subplots(figsize=(10,15))
        ax.axvline(0)
    else:
        print('using outside figure')

    def plot(tr,o,ax):
        e = tr.stats.npts/tr.stats.sampling_rate
        t = np.linspace(o,o+e,num=tr.stats.npts)
        if sec_type == 'az':
            XX = tr.stats.sac['az']
        elif sec_type == 'dist':
            XX = tr.stats.sac['gcarc']
        else:
            XX = (tr.stats.sac['gcarc']*np.sin(np.radians(sec_type))+
                 tr.stats.sac['az']*np.cos(np.radians(sec_type)))

        ax.plot(t,tr.data+(1.4*XX),alpha=0.5,
                color=color,label=tr.stats.station,
                picker=10)

    if a_list == True:
        for tr in st:
            plot(tr,0,ax)

    elif type(a_list) == list:
        if len(a_list) != 1:
            print('Must have phase identifier string of len = 1')
            return
        else:
            for tr in st:
                evdp = tr.stats.sac['evdp']
                gcarc = tr.stats.sac['gcarc']
                P = model.get_travel_times(distance_in_degree=gcarc,
                    source_depth_in_km=evdp,
                    phase_list = a_list)
                P_time = P[0].time
                plot(tr,-1*(P_time+tr.stats.sac['o']),ax)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Epicentral Distance (deg)')
    ax.set_title(st[0].stats.network)

    if picker == True:
        remove_list = []
        def on_pick(event):
            artist = event.artist
            artist.set_c('white')
            artist.set_alpha(0.0)
            remove_list.append(artist.get_label())
            fig.canvas.draw()
        fig.canvas.mpl_connect('pick_event', on_pick)
        plt.show()
        for tr in st:
            if tr.stats.network+'.'+tr.stats.station in remove_list:
                st.remove(tr)

class DragHandler(object):
    """ A simple class to handle Drag n Drop.

    This is a simple example, which works for Text objects only.
    """
    def __init__(self, st, figure=None) :
        if figure is None : figure = p.gcf()
        # simple attibute to store the dragged text object
        self.dragged = None
        self.station = []
        self.shift = []
        self.srate = st[0].stats.sampling_rate

        # Connect events and callbacks
        figure.canvas.mpl_connect("pick_event", self.on_pick_event)
        figure.canvas.mpl_connect("button_release_event", self.on_release_event)

    def on_pick_event(self, event):
        #print type(event.artist.get_label())

        if type(event.artist.get_label()) == unicode:
            self.dragged = event.artist
            self.xdata = event.artist.get_data()[0]
            self.ydata = event.artist.get_data()[1]
            self.pick_pos = event.mouseevent.xdata
            self.station.append(event.artist.get_label())
        return True

    def on_release_event(self, event):

        newx = event.xdata
        try:
            newy = np.roll(self.ydata,int((newx-self.pick_pos)*(self.srate)))
            self.dragged.set_data(self.xdata,newy)
            self.dragged = None
            p.draw()
            self.shift.append(newx-self.pick_pos)
            return True
        except (AttributeError,TypeError):
            return True


main()




