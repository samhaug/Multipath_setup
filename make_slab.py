#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : make_slab.py
Purpose : make 3D slab input file
Creation Date : 17-05-2017
Last Modified : Thu 18 May 2017 01:30:42 PM EDT
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
    points = area_select()
    depth_points = set_depth(points,5371,100)
    plot_3d(depth_points)
    write_perturb(depth_points,0,3,0)

def write_perturb(depth_points,dvp,dvs,drho):
    fname = '{}_{}_{}vp_{}vs_{}rho.txt'.format(int(depth_points[:,-1].min()),
                                               int(depth_points[:,-1].max()),
                                               dvp,dvs,drho)
    dvp = np.transpose([dvp*np.ones(depth_points.shape[0])])
    dvs = np.transpose([dvs*np.ones(depth_points.shape[0])])
    drho = np.transpose([drho*np.ones(depth_points.shape[0])])
    full_hetero = np.hstack((depth_points,dvs,dvp,drho))
    with open(fname,'w') as f:
        f.write('! #lon(deg), lat(deg), depth(km), dVs(%), dVp(%), drho(%)\n')
        np.savetxt(f,full_hetero,fmt='%.3f')

def plot_3d(depth_points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(depth_points[::10,0],depth_points[::10,1],depth_points[::10,2])
    plt.show()

def set_depth(points,radmin,thickness):
    depth_points = []
    depth_interp = np.arange(radmin,radmin+thickness+10,10)
    for ii in points:
        for jj in depth_interp:
            depth_points.append([ii[0],ii[1],jj])
    return np.array(depth_points)

def area_select(**kwargs):
    fig = plt.figure(figsize=(20,20))
    m = Basemap(width=12000000,height=9000000,projection='lcc',
            resolution='c',lat_1=15.,lat_2=25,lat_0=20,lon_0=117.)
    m.drawcoastlines()
    ax = plt.gca()
    line, = ax.plot([0], [0])  # empty line
    linebuilder = LineBuilder(line)
    plt.show()
    lonpt, latpt = m(linebuilder.xs,linebuilder.ys,inverse=True)
    a = zip(lonpt,latpt)
    b = Polygon(a[1::])
    fig,ax = plt.subplots()
    ymin,ymax = np.min(latpt),np.max(latpt)
    xmin,xmax = np.min(lonpt),np.max(lonpt)
    xx,yy = np.meshgrid(np.linspace(xmin,xmax,num=70),np.linspace(ymin,ymax,num=70))
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
    plt.tight_layout()
    plt.show()
    return points

class LineBuilder(object):
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        if event.inaxes!=self.line.axes: return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()

main()
