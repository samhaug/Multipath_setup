#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : make_slab.py
Purpose : make 3D slab input file
Creation Date : 17-05-2017
Last Modified : Wed 17 May 2017 06:26:31 PM EDT
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
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from descartes import PolygonPatch

def main():
    fig = plt.figure()
    m = Basemap(width=12000000,height=9000000,projection='lcc',
            resolution='c',lat_1=45.,lat_2=55,lat_0=50,lon_0=-107.)
    m.drawcoastlines()
    ax = plt.gca()
    line, = ax.plot([0], [0])  # empty line
    linebuilder = LineBuilder(line)
    plt.show()
    lonpt, latpt = m(linebuilder.xs,linebuilder.ys,inverse=True)
    a = zip(lonpt,latpt)

    b = Polygon(a[2::])
    ymin,ymax = np.min(latpt),np.max(latpt)
    xmin,xmax = np.min(lonpt),np.max(lonpt)
    xx,yy = np.meshgrid(np.linspace(xmin,xmax,num=50),np.linspace(ymin,ymax,num=50))
    xx = xx.reshape(xx.size)
    yy = yy.reshape(yy.size)
    points = []
    for idx,ii in enumerate(xx):
        if b.contains(Point([xx[idx],yy[idx]])):
            points.append([xx[idx],yy[idx]])
        else:
            continue

    points = np.array(points)
    fig,ax = plt.subplots()
    ax.scatter(points[:,0],points[:,1])
    plt.show()

class LineBuilder(object):
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        print('click', event)
        if event.inaxes!=self.line.axes: return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()

main()
