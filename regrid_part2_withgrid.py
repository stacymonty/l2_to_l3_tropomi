#!/usr/bin/env python

# ---------------------------------------------------------------------
# Stacy Montgomery, NOV 2018 - DEC 2018
# This program takes the cropped l2 files and regrids the data to new domain.
# Theres the griddata way -- which causes striping, smoothing function sucks
# then RBF way which requires submission to super computer (or something that allows ~16GB of memory)
# but it's smoother
# ---------------------------------------------------------------------
#                             USER INPUT
# ---------------------------------------------------------------------
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import netCDF4
import math
from scipy.interpolate import griddata

# Projections -- this will be used in naming files later
domain = 'Chicago'
# grid file
grid='/home/asm0384/ChicagoStudy/inputs/grid/latlon_ChicagoLADCO_d03.nc'
lon,lat = np.array(Dataset(grid,'r')['lon']),np.array(Dataset(grid,'r')['lat'])

var='NO2'

#Directory to where L2 TropOMI files are stored
dir='/projects/b1045/TropOMI/'+var+'/l2_cut/'

#from netcdf file, what do you want
varname='nitrogendioxide_tropospheric_column'
varprecision='qa_value'
tagdir = '~/tag/'

dates=['201901'+str(i).zfill(2) for i in range(1,32)]

filestartswith  = 'S5P_OFFL_L2__NO2____' # 'S5P_OFFL_L2__O3'


# pull grid stuff
#Get number of files in directory
onlyfiles = next(os.walk(dir))[2]
#onlyfiles = [x for x in onlyfiles if x.startswith(filestartswith)]
onlyfiles=sorted(onlyfiles)# so th

fstart=[filestartswith+dates[i] for i in range(len(dates))]
fnames=[]

for f in onlyfiles: 
	for fs in fstart: 
		if f.startswith(fs): fnames.append(f)


# pll -- will be all the points across time and their locations
# intemed_grid -- will be each data already linearly interpolated using girddata
pll = []
intermed_grid=[]

for i in range(len(fnames)):
   #if i !=0 and i !=3 and i !=8 and i !=11:
# load in file
      filename=fnames[i]
      nc = Dataset(dir+fnames[i],'r')
   #nc = Dataset(fnames[i],'r')
   #match the lat lons to the grid
      clat,clon,d,qa=np.array(nc['latitude']).ravel(),np.array(nc['longitude']).ravel(),np.array(nc[varname]).ravel(),np.array(nc[varprecision]).ravel()
      d[d>10000]=float("nan") # since the mask isn't working sometimes -- sometimes values are actually the huge float, other times they're masked!
      np.ma.set_fill_value(d,float("nan"))
   # filter with qa value
      thresh=qa>.5
      clat,clon,d,qa_cut = clat[thresh],clon[thresh],d[thresh],qa[thresh]
      if len(d) > 0:
         points=[[clon[x],clat[x]] for x in range(len(clat))]
         points=np.asarray(points)
         if i == 0: pll = pd.DataFrame([clon,clat,d]).T
         else: pll = pll.append(pd.DataFrame([clon,clat,d]).T)
      # try linear grid
         try: intermed_grid.append(griddata(points,d,(lon,lat),method='linear',fill_value=float("nan")))
         except: print('nevermind')
      # Move on to next file,
      nc.close()
   

intermed_grid=np.asarray(intermed_grid)

# do some data cleaning for intermed grid
nans = [np.count_nonzero(~np.isnan(intermed_grid[i])) for i in range(len(intermed_grid))]
cut = []

for nan in nans:
   if nan < len(lon.ravel())*0.7:
      cut.append(False)
   else:
      cut.append(True)

intermed_grid[cut].mean(axis=0)

# do sum data cleaning  for pll 
# -- pll has ALL of the lon/lat points in the onth
pll = pll[pll[0]>lon.min()+0.1]
pll = pll[pll[0]<lon.max()+0.1]
pll = pll[pll[1]>lat.min()+0.1]
pll = pll[pll[1]<lat.max()+0.2]
pll=pll[pll[2]>0]

pll.reset_index(inplace=True)

# zip lat lon together
points=[[pll[0][x],pll[1][x]] for x in range(len(pll))]

#original way:
# causes striping because of values...
#griddata(list(zip(pll[0],pll[1])),pll[2].tolist(),(lon,lat),method='linear',fill_value=float("nan"))

# create RBF function given points
# allows for smoothing, but need to submit to supercomputer
f = interpolate.Rbf(pll[0], pll[1], pll[2], function='linear')

# apply to lat lon
grid=f(lon,lat)
grid = pd.DataFrame(grid)
grid.to_csv('~/rbdinterp.csv')


# This code is for griddata stuff
#--------------------------------------------

# intermed_grid=np.asarray(intermed_grid)
# week = np.nanmean(intermed_grid,axis=0)
# plt.figure(figsize=(8,10))
# plt.pcolormesh(lon,lat,week)
# plt.title('Avg for ' + dates[0]+'-'+dates[-1])

# plt.tight_layout()
# #plt.show()

# # Sanity check: how do these all look individually
# fig,axs = plt.subplots(4,3,figsize=(8,10))
# axs=axs.ravel()
# for i in range(len(intermed_grid)):
#    ax=axs[i]
#    ax.set_title('Day %i'%(i))
#    ax.pcolormesh(lon,lat,intermed_grid[i])

# plt.tight_layout()
# plt.show()

# ncout = Dataset(filestartswith+dates[0]+'_'+dates[-1]+'.nc','w')
# dname=[('x',lon.shape[0]),('y',lat.shape[1]),('time',1)]
# var=[(varname,week,d.dtype),('longitude',lon,d.dtype),('latitude',lat,d.dtype)]


# for dd in dname:
#       	ncout.createDimension(dd[0], dd[1])
#       	# Copy cropped variables

# for v_name in var:
#       	outVar = ncout.createVariable(v_name[0], v_name[2], (dname[0][0],dname[1][0]))
#       	outVar[:] = v_name[1].data # for some reason adding the : is important
#       # Comprehension check: plt.scatter(ncout['longitude'][0],ncout['latitude'][0],c=ncout[varname][0])
#       # close out


# ncout.close()

# print('Wrote out with '+filename)

# #import scipy.ndimage
# #zlat,zlon,zd=scipy.ndimage.zoom(clat,3),scipy.ndimage.zoom(clon,3),scipy.ndimage.zoom(d,3)

# ncout = Dataset('chi_mask.nc','w')
# dname=[('x',lon.shape[0]),('y',lat.shape[1]),('time',1)]
# var=[('mask',mask*1,(mask*1).dtype),('longitude',lon,lat.dtype),('latitude',lat,lat.dtype)]
