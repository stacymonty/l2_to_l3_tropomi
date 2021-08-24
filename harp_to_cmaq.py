# LIBRARIES
import numpy as np
from netCDF4 import Dataset
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

# Original data (e.g. measurements)
data = Dataset("3.nc")
z = np.array(data['tropospheric_NO2_column_number_density'][0])

# get the center location of the pixels
x,y = np.array(data['longitude_bounds'][0]).mean(axis=1),np.array(data['latitude_bounds'][0]).mean(axis=1)

# transofrm list of coordinates into grid form
xx,yy = np.meshgrid(x,y)

# get rid of missing values
no2 = z[~np.isnan(z)]
xx,yy = xx[~np.isnan(z)],yy[~np.isnan(z)]

# destination dataset
ll = Dataset("latlon.nc")
lat,lon = np.array(ll['lat']),np.array(ll['lon'])

# interpolate to cmaq grid
zi = griddata((xx.ravel(),yy.ravel()),no2.ravel(),(lon,lat),method='linear')
