
# ---------------------------------------------------------------------
# Stacy Montgomery, NOV 2018 - DEC 2018
# This program takes the cropped l2 files and regrids the data to new domain.
# Uses an RBF function to smooth the data to CMAQ grid.
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
import scipy.interpolate as interpolate

# Projections -- this will be used in naming files later
domain = 'Chicago'

# File of grid
grid='/home/asm0384/ChicagoStudy/inputs/grid/latlon_ChicagoLADCO_d03.nc'
lon,lat = np.array(Dataset(grid,'r')['lon']),np.array(Dataset(grid,'r')['lat'])

var='NO2'

#Directory to where L2 TropOMI files are stored
dir='/projects/b1045/TropOMI/'+var+'/summer/l2_cut/'

#from netcdf file, what do you want
varname='nitrogendioxide_tropospheric_column'
varprecision='qa_value'
tagdir = '~/tag/'
filestartswith  = 'S5P_OFFL_L2__NO2____' # 'S5P_OFFL_L2__O3'
dates=['201808'+str(i).zfill(2) for i in range(1,32)]


# pull files from directory
onlyfiles = next(os.walk(dir))[2]
onlyfiles=sorted(onlyfiles)# so th

fstart=[filestartswith+dates[i] for i in range(len(dates))]
fnames=[]

for f in onlyfiles:
        for fs in fstart:
                if f.startswith(fs): fnames.append(f)

#WEIRD HACKY SORRY
fnames=onlyfiles

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
      points=[[clon[x],clat[x]] for x in range(len(clat))]
      points=np.asarray(points)
      if i == 0: pll = pd.DataFrame([clon,clat,d]).T
      else: pll = pll.append(pd.DataFrame([clon,clat,d]).T)
   # Now grid
   # Move on to next file,
      nc.close()

      
 # double check the location of these points
pll = pll[pll[0]>lon.min()+0.1]
pll = pll[pll[0]<lon.max()+0.1]

pll = pll[pll[1]>lat.min()+0.1]
pll = pll[pll[1]<lat.max()+0.2]

pll=pll[pll[2]>0]

pll.reset_index(inplace=True)

# create lat/lon pairs to make no2 points
points=[[pll[0][x],pll[1][x]] for x in range(len(pll))]

# apply RBF function to the points to create gridded data
f = interpolate.Rbf(pll[0], pll[1], pll[2], function='linear',smooth=1)
grid=f(lon,lat)

# put grid to csv out
grid = pd.DataFrame(grid)
grid.to_csv('~/rbdinterp_linear_smooth_201808_pt2.csv')

