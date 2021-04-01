!/usr/bin/env python

# ---------------------------------------------------------------------
# Stacy Montgomery, NOV 2018 - DEC 2018
# This program takes in L2 TropOMI data and crops it to the right domain.
# The output are cropped netCDF files that contain the centroid lat/lons, qa value, and no2 value.
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

# Projections -- this will be used in naming files later
domain = 'Chicago'
# grid file
grid='/home/asm0384/ChicagoStudy/inputs/grid/latlon_ChicagoLADCO_d03.nc'
lon,lat = np.array(Dataset(grid,'r')['lon']),np.array(Dataset(grid,'r')['lat'])
loncrn_min,loncrn_max= lon.min()-.75,lon.max()+.75
latcrn_min,latcrn_max = lat.min()-.75,lat.max()+.75

var='NO2'

#Directory to where L2 TropOMI files are stored
dir='/projects/b1045/TropOMI/'+var+'/summer/'
fout_dir_l2_cut='/projects/b1045/TropOMI/'+var+'/summer/l2_cut/'

#from netcdf file, what do you want
varname='nitrogendioxide_tropospheric_column'
varprecision='qa_value'
tagdir = '~/tag/'


filestartswith  = 'S5P_RPRO_L2__NO2' # 'S5P_OFFL_L2__O3'
# ------------------------- End User Input ----------------------------

# Functions
latbounds = [latcrn_min,latcrn_max]
lonbounds = [loncrn_min,loncrn_max] # degrees east ? 

def crop_nc(latbounds,lonbounds,nc,varname):
        lats = nc.groups['PRODUCT'].variables['latitude'][0]
        lons = nc.groups['PRODUCT'].variables['longitude'][0]
        # latitude lower and upper index
        lons_tf=np.logical_and(lons>loncrn_min,lons<loncrn_max)
        lats_tf=np.logical_and(lats>latcrn_min,lats<latcrn_max)
        # get intersection of 2 to make mask
        c=np.logical_and(lons_tf,lats_tf)
        return c
#Get number of files in directory
onlyfiles = next(os.walk(dir))[2]
#onlyfiles = [x for x in onlyfiles if x.startswith(filestartswith)]
onlyfiles=sorted(onlyfiles)# so that searching for dates are easier

# Loop through files and find the files within the given directory
for i in range(len(onlyfiles)):
# load in file
   filename=onlyfiles[i]
   nc = Dataset(dir+filename,'r')
   # get indices of the variable we're cropping
   c = crop_nc(latbounds,lonbounds,nc,varname)
   # check if this pulls anything
   v=nc.groups['PRODUCT'].variables[varname][0][c]
   vp=nc.groups['PRODUCT'].variables[varprecision][0][c]
   la=nc.groups['PRODUCT'].variables['latitude'][0][c]
   lo=nc.groups['PRODUCT'].variables['longitude'][0][c]
   dtype=[nc.groups['PRODUCT'].variables[varname].datatype,nc.groups['PRODUCT'].variables[varprecision].datatype, nc.groups['PRODUCT'].variables['longitude'].datatype,nc.groups['PRODUCT'].variables['latitude'].datatype]
   # if variable exists 
   if len(v)>0:
      # Make file out
      ncout = Dataset(filename.split('.nc')[0]+'_cut.nc','w')
      #Copy dimensions
      #for dname, the_dim in nc.groups['PRODUCT'].dimensions.items():
      #dname=[('scanline',v.shape[0]), ('ground_pixel',v.shape[0]),('time',1)]
      dname=[('scanline',v.shape[0]),('time',1)]
      var=[(varname,v,dtype[0]),(varprecision,vp,dtype[1]),('longitude',lo,dtype[2]),('latitude',la,dtype[3])]
      #ok
      for dd in dname:
        ncout.createDimension(dd[0], dd[1])
        # Copy cropped variables
      for v_name in var:
        #outVar = ncout.createVariable(v_name[0], v_name[2], (dname[2][0],dname[0][0],dname[1][0]))
        outVar = ncout.createVariable(v_name[0], v_name[2],(dname[1][0],dname[0][0]))
        outVar[:] = v_name[1].data # for some reason adding the : is important
      # close out
      ncout.close()
      print('Wrote out with '+filename)
   #close file move to next
   #print('Done with file #'+str(i))
   nc.close()
