# LIBRARIES
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date, datetime, timedelta
from dateutil.rrule import rrule, DAILY
import os, sys
import harp
import numpy


# we indicate the bbox of the download area
bbox= 'footprint:"Intersects(POLYGON((-100.87749481201168 46.672527623044175,-73.19744110107418 46.923069179052504,-74.42687988281246 32.14800174970084,-101.45393371582027 32.372132709886614,-100.87749481201168 46.672527623044175,-100.87749481201168 46.672527623044175)))"'

# sentinelhub access parameters
api = SentinelAPI('s5pguest', 's5pguest', 'https://s5phub.copernicus.eu/dhus')

def change_extension():
    # Change from zip to nc
    for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
      base_file, ext = os.path.splitext(filename)
      if ext == ".zip":
        os.rename(filename, base_file + ".nc")


def mosaic_scenes(nombre_nc, d):
    """
    Create the regridded products
    """
    # Search for 5P products
    file_names = []
    products = [] # array to hold the products
    print("Importing with HARP....")
    i = 0
    for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
      base_file, ext = os.path.splitext(filename)
      if ext == ".nc" and base_file.split('_')[0] == 'S5P':
        product_name = base_file + "_" + str(i)
        print(product_name)
        try:
            product_name = harp.import_product(base_file + ext,
                                                operations="latitude > -55 [degree_north]; latitude < 80 [degree_north];tropospheric_NO2_column_number_density_validity > 75;bin_spatial(501,39.5,0.01,651,-90.5,.01)",
                                                post_operations="bin();squash(time, (latitude,longitude))")
            print("Product " + base_file + ext + " imported")
            products.append(product_name)
        except:
            print ("Didn't import!")
        #
        i = i + 1
    try:
        print("Starting to execute HARP operations....")
        product_bin = harp.execute_operations(products, "", "bin()")
        print("Completed the regridding.")
        harp.export_product(product_bin, "out_8_"+str(d)+"_18.nc")
    except:
        print("HARP and/or regridding did not work!")
    # Delete files from directory
    for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
      base_file, ext = os.path.splitext(filename)
      if ext == ".nc" and base_file.split('_')[0] == 'S5P':
        os.remove(base_file + ext)


def download_data(group_days, api, bbox, i):
    #""Function for data download.
    #Keyword arguments:
    #group_days - the average of the defined group of days will be taken
    #access_parameters - credentials and url access to the image repository
    #bbox - image search area
    #""
    start_day = date(2018, 8, i) # start date
    end_day = date(2018, 8, i) # end date
    group_days = 1
    group_number = 1
    while start_day <= end_day:
        # a search will be carried out by area, date and product
        products = api.query(date = (start_day, start_day + timedelta(group_days)), producttype = 'L2__NO2___',platformname = 'Sentinel-5')
        # move forward the day
        start_day = start_day + timedelta(group_days)
        try:
            print("Downloading...")
            api.download_all(products)
            print("Changing extension....")
            change_extension()
            print('Regridding....')
            mosaic_scenes(group_days,i)
            group_number = group_number + 1
        except:
            print("Error in the download and / or execution of the process")

                        
# Start looping through days and execute the script
for i in range(1,32):
  # we call the function for data download
  download_data(1, api, bbox, i)
  print('-'*100)
  print("Done with day "+str(i))
  print('-'*100)

