#!/usr/bin/env python

# ---------------------------------------------------------------------
# Stacy Montgomery, NOV 2018 - DEC 2018
# This program takes in L2 TropOMI data and regrids the data to new domain.
# Must have: earth trig.py by Prof. Van der Lee to make grid
# 
# Known errors: you cannot switch between domains from part 1 and 2, the resulting grid gets messed up

# ---------------------------------------------------------------------
#                             USER INPUT
# ---------------------------------------------------------------------

# grid file
dir='/projects/b1045/jschnell/ForStacy/'
ll='latlon_ChicagoLADCO_d03.nc'


#grid file 
grid='/home/asm0384/RegridTropOMI/GRIDCRO2D_Chicago_LADCO_2018-08-01.nc'
grid=dir+ll

#Pixel size for L3 grid- in degrees 
cell_size_deg=.005

#Radius for averaging/smoothing kernel- in degrees & distance for threshold
distance_radius_in_degrees = .05

# Projection
domain = 'Chicago'
loncrn_min=-88; loncrn_max=-87; latcrn_min= 40; latcrn_max= 43

# Dates of Interest
startday=1; endday=31
startmonth=8; endmonth=8

tagdir = '~/tag/'

# data files and info
varname = 'nitrogendioxide_tropospheric_column'
varprecision = 'nitrogendioxide_tropospheric_column_precision'
fout_dir_l2_cut='/projects/b1045/NO2/l2_cut/'
fout_dir_l3='/projects/b1045/NO2/l3/'


# ---------------------- Libraries  -----------------------
from netCDF4 import Dataset as NetCDFFile; import matplotlib.pyplot as plt; import numpy as np;
import pandas as pd; import numpy.ma as ma; import time as timeit; import os; import math
from math import sin, cos, sqrt, atan2, radians

# ---------------------- User Defined Functions -----------------------

#Returns new lat/lon grid with given cell size around equator
def creategrid(min_lon, max_lon, min_lat, max_lat, cell_size_deg, mesh=False):
    min_lon = math.floor(min_lon)
    max_lon = math.ceil(max_lon)
    min_lat = math.floor(min_lat)
    max_lat = math.ceil(max_lat)
    lon_num = int((max_lon - min_lon)/cell_size_deg)
    lat_num = int((max_lat - min_lat)/cell_size_deg)
    grid_lons = np.zeros(lon_num) # fill with lon_min
    grid_lats = np.zeros(lat_num) # fill with lon_max
    grid_lons = grid_lons+(np.asarray(range(lon_num))*cell_size_deg)
    grid_lats = grid_lats+(np.asarray(range(lat_num))*cell_size_deg)
    grid_lons = grid_lons-np.mean(grid_lons)
    grid_lats = grid_lats-np.mean(grid_lats)
    #grid_lons, grid_lats = np.meshgrid(grid_lons, grid_lats)
    return grid_lons, grid_lats

# adapted from : http://kbkb-wx-python.blogspot.com/2016/08/find-nearest-latitude-and-longitude.html
def find_index(point_lon, point_lat, grid_lon, grid_lat, distance_radius_in_degrees):
# point_lon, point_lat = list of lat lon points --> lat_list, lon_list = [x1,x2][y1,y2]
# grid_lon, grid_lat = np.array of gridded lat lon --> grid_x= np.array([x1,x2,x3],[x4,x5,x6])
# distance_radius_in_degrees = how large of a difference between matching points
#'''''''''''''''''''''''''''''''''
# 
#for rr in range(1):
   xx=[];yy=[];distance=[]
   for i in range(len(point_lat)):
      abslat = np.abs(grid_lat-point_lat[i])
      abslon= np.abs(grid_lon-point_lon[i])
      c = np.maximum(abslon,abslat)
      #x, y = np.where(c == np.min(c))
      x, y = np.where(c < distance_radius_in_degrees)
      dist=[(deltas(grid_lat[x][t][y][t]*p, grid_lon[x][t][y][t]*p, point_lat[i]*p, point_lon[i]*p))/p for t in range(len(x))]      #add indices of nearest wrf point station
      xx.append(x) 
      yy.append(y)
      distance.append(dist)
   #return indices list
   return xx, yy, distance

# distance=[(deltas(grid_lat[x][t][y][t]*p, grid_lon[x][t][y][t]*p, point_lat[i][1]*p, point_lon[i]*p))/p for t in range(len(x))]
# lat/lon,lat/lon
#point_lon, point_lat, grid_lon, grid_lat= pswnlon, pswnlat,nxlon,nylat


# --------------------------------------------------------------------------------------------------
#                         !! Part 2: !!
#     With screened files, make new grid and set values to new grid
# --------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------
# Step 1: Download files that are screened to be in domain into dataframe for easy filtering
# ---------------------------------------------------------------------



#***************************************

#Get number of files in directory with L2 domain CSV files
onlyfiles = next(os.walk(fout_dir_l2_cut))[2]
onlyfiles=sorted(onlyfiles) # so that searching for dates are easier
numfiles=(len(onlyfiles))

# Days and months we're interested in:
datesofinterest=np.arange(startday,endday+1)
monthsofinterest=np.arange(startmonth,endmonth+1)

#data frame with all data
megaframe= pd.DataFrame()

# Loop through files and find the files within the given directory
for i in range(numfiles):
    filename=onlyfiles[i]
    ymd=filename.split('_made_')
    ymd=ymd[0]
    year,month,date=ymd.split("-")
    #Check to see if the file is the date you are looking for
    if int(date) in datesofinterest and int(month) in monthsofinterest:
        alldata = pd.read_csv(fout_dir_l2_cut+filename)
        megaframe=pd.concat([megaframe,alldata],ignore_index=True)


# Some data is randomly saved as a string, so we need to filter that out
stringq='--'
count=0
badpoints=[]
for point in megaframe[varname]:
     if type(point)==type(stringq):
         badpoints.append(count)
     count=count+1

megaframe=megaframe.drop(megaframe.index[badpoints])

# Get rid of negative and missing values-- commented out because it might bias data
# megaframe[varname]=megaframe[varname].mask(megaframe[varname]<0)
megaframe[varname]=megaframe[varname].mask(megaframe[varname]>9.969210e+35)

# ---------------------------------------------------------------------
# Step 2: Make new grid and set values to new grid
# The weighting for the pixels are linear with wx=(r-d)/a
# where d=distance(new_lat,new_lon,original_lat,original_lon), 
# r=preset radius, a is a constant to make sum(wx)=1
# ---------------------------------------------------------------------

# $$$ most relevant for Cassia $$$ #

from earthtrig import * #will use rotate function

# Create arrays out of the dataframes to index search faster
pswnlat=np.array(megaframe['lats']).reshape(len(megaframe['lats']),1)
pswnlon=np.array(megaframe['lons']).reshape(len(megaframe['lons']),1)
pswnno2=np.array(megaframe[varname]).reshape(len(megaframe[varname]),1)

# pull
gridnc = NetCDFFile(grid,'r')
nxlon,nylat= gridnc['lon'][:], gridnc['lat'][:]
ny = len(nylat[0]); nx=len(nxlon)

# get nearest indices of grid for each datapoint 
from earthtrig import * 
#point_lon, point_lat, grid_lon, grid_lat= pswnlon, pswnlat,nxlon,nylat
xx,yy,distance= find_index(pswnlon, pswnlat,nxlon,nylat, distance_radius_in_degrees)

# drop data that doesnt match the grid
mask=pd.DataFrame(xx)[0].notna()
pswnlat, pswnlon, pswnno2 = np.array(pd.DataFrame(pswnlat)[mask]), np.array(pd.DataFrame(pswnlon)[mask]),np.array(pd.DataFrame(pswnno2)[mask])

#mask xx yy dist .. can't do dataframe because will fill up missing points with na
xx_drop,yy_drop,dist_drop=[],[],[]
for i in range(len(mask)):
   if mask[i]==True:
       xx_drop.append(xx[i])
       yy_drop.append(yy[i])
       dist_drop.append(distance[i])

# make temp grid that mimics netcdf grid size
gridno2 =[]; griddistance=[]
for x in range(nx):
   gridno2.append([[] for y in range(ny)])
   griddistance.append([[] for y in range(ny)])

# reset counts
i,j=0,0

# fill grid
for i in range(len(xx_drop)): 
   for j in range(len(xx_drop[i])):
      gridno2[int(xx_drop[i][j])][int(yy_drop[i][j])].append(pswnno2[i][0])
      griddistance[int(xx_drop[i][j])][int(yy_drop[i][j])].append(dist_drop[i][0])

i,j=0,0
#now average grid points given distances, will result in final grid average
# MUST UPDaTE-- currently just an average
for i in range(len(gridno2)):
   for j in range(len(gridno2[0])):
      gridno2[i][j]= np.nanmean(gridno2[i][j])

# $$$ most relevant for Cassia $$$ #

# ---------------------------------------------------------------------
# Make figure 
# ---------------------------------------------------------------------

# make fig object
fig, axs = plt.subplots(subplot_kw={'projection': crs_new},figsize=(6, 6))

data=pd.DataFrame(gridno2)

#set levels for plot
vmin,vmax= data.min().min(),data.max().max()
levels = np.linspace(vmin, vmax, 20)

# get rid of values outside the levels we are contouring to
data[pd.DataFrame(data)>vmax]=vmax


#plot the gridded data by using contourf
cs=plt.contourf(nxlons,nylats,data,cmap= "inferno", transform=crs_new, levels=levels)

# set axes extents from shapefile
yl=41.65;yu=42.3
xu=-87.47;xl=-88.3
axs.set_extent([xl,xu,yl,yu],crs= crs_new)

#add colorbar and label
cbar=plt.colorbar(cs,boundaries=np.arange(vmin,11))
#cbar.ax.set_ylabel('100 * ' +ncfile[0][var].units)
cbar.set_ticks(np.arange(vmin, vmax, 10))

# add state lines
import cartopy.feature as cfeature
states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',facecolor='none')

axs.add_feature(cfeature.STATES, edgecolor='black')

#plt.pcolor(nxlon,nylat,gridno2)

plt.show()
