#!/usr/bin/env python
import numpy as np
import scipy.interpolate
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import argrelextrema

'''
This script will set up a coincentric slab with radial and lateral
bounds.
'''

def read_PREM():
    '''
    '''
    PREM = np.loadtxt('PREM_1s.csv',delimiter=',')

    rad =  PREM[:,0]
    rho =  PREM[:,2]
    vs  =  PREM[:,5]
    vp  =  PREM[:,3]

    fine_rad = np.linspace(rad.min(),rad.max(),1000)

    f_rho = scipy.interpolate.interp1d(rad,rho)
    f_vs = scipy.interpolate.interp1d(rad,vs)
    f_vp = scipy.interpolate.interp1d(rad,vp)

    int_rho = f_rho(fine_rad)
    int_vp = f_vp(fine_rad)
    int_vs = f_vs(fine_rad)

    return fine_rad,int_rho,int_vs,int_vp

def make_bounds(radmin,radmax,colatmin,colatmax):
    '''
    Makes bounds for cylindrical symmetry
    '''
    rad_domain = np.arange(radmin,radmax,1.)
    colat_domain = np.arange(colatmin,colatmax,1)

    colat_array,rad_array = np.meshgrid(colat_domain,rad_domain)

    return colat_array,rad_array

def assign_velocity(colat_array,rad_array,dvp,dvs,drho,**kwargs):
    '''
    Enter perturbations in percent values.

    dvp = 4 means 4% vp increase with respect to PREM

    '''
    rad,rho,vs,vp = read_PREM()

    vp_array = np.zeros(rad_array.shape)
    vs_array = np.zeros(rad_array.shape)
    rho_array = np.zeros(rad_array.shape)

    for ii in range(rad_array.shape[0]):
        idx = np.abs(rad-rad_array[ii][0]).argmin()
        vp_array[ii,:] = vp[idx]*(1+dvp/100.)*1000
        vs_array[ii,:] = vs[idx]*(1+dvs/100.)*1000
        rho_array[ii,:] = rho[idx]*(1+drho/100.)*1000

    return vp_array,vs_array,rho_array

def write_output(colat_array,rad_array,vp_array,vs_array,rho_array,**kwargs):
    '''
    write files for AxiSEM to read.
    '''
    name = kwargs.get('name','slab.sph')
    slant = kwargs.get('slant',True)

    rad,rho,vs,vp = read_PREM()

    b_idx = np.abs(rad-3480.).argmin()
    t_idx = np.abs(rad-6371.).argmin()

    print 'Beginning output_datafiles'

    rad = np.reshape(rad_array,(rad_array.size,1))
    theta = np.reshape(colat_array,(rad_array.size,1))
    rho = np.reshape(rho_array,(rad_array.size,1))
    vp = np.reshape(vp_array,(rad_array.size,1))
    vs = np.reshape(vs_array,(rad_array.size,1))

    with open(name,'w') as f_handle:
        f_handle.write(str(rad.size)+'\n')
        np.savetxt(f_handle,np.hstack((rad,theta,vp,vs,rho)),delimiter='   ',fmt='%1.3f')


clat_1,rad_1 = make_bounds(5171,5371,10,20)
vp_array_1,vs_array_1,rho_array_1 = assign_velocity(clat_1,rad_1,0,10,0)

write_output(clat_1,rad_1,vp_array_1,vs_array_1,rho_array_1,name='200km_10_20_s10.sph')
#plt.imshow(np.vstack((vp_array_1,vp_array_2)),aspect='auto',interpolation='none')
#plt.show()





