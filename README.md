# l2_to_l3_tropomi

========================
Regrid TropOMI L2 Data
Stacy Montgomery, NOV 2018 - DEC 2018
stacy@earth.northwestern.edu
========================


These are a collection of scripts that takes L2 TROPOMI DATA from NASA GES-DISC and creates a uniform gridded product with the purpose of plotting and doing further processing.  These scripts run on python3 or later.
The scripts to do the processing are called:
regrid_tropomi_part1.py
regrid_tropomi_part2.py
regrid_tropomi_part3.py
earthtrig.py **
(**make sure this script is within your current directory which you are running the code from, or update the code to put the directory to earthtrig.py)

Data must be stored in 3 unique, accessible directories: one for the unprocessed netCDF TropOMI data (L2_TropOMI_data), one for cut L2 TropOMI data(L2_Cut_swaths), and a final folder for L3 processed data (L3_Final_Grid). Each script must be set up within the user input section to set variables. 

To run these scripts, update the input and output directories for each script, then type into your terminal < python regrid_tropomi_part1.py >. Part 3 can only be set up after running part 2 because it requires the output filename of part 2.

----------------
Required Modules
----------------
To run these codes, include the latest releases of the following python modules:

netCDF4
<https://github.com/Unidata/netcdf4-python>

mpl_toolkits.basemap
<https://matplotlib.org/basemap/users/installing.html>

pandas
<https://pandas.pydata.org/getpandas.html>

numpy
<https://www.scipy.org/scipylib/download.html>

os
<https://docs.python.org/3/library/os.html>

earth trig.py by Prof. Van der Lee

additional modules that should be included with python:
math,time

----------------
Acquiring TropOMI data
----------------

To get this data, you must setup an Earthdata account <https://urs.earthdata.nasa.gov/>. Install wget on your machine if necessary. A version of wget 1.18 complied with gnuTLS 3.3.3 or OpenSSL 1.0.2 or LibreSSL 2.0.2 or later is recommended.

Data can be accessed from this link <https://disc.gsfc.nasa.gov/datasets/S5P_L2__AER_AI_V1/summary?keywords=tropomi>. Days may be subset from that link. Save the following links into a textfile in your home directory in a file labelled url.txt. If you do not work from your home directory the following code will not work.

Execute the following code from your home directory in the terminal:

cd ~ or cd $HOME
touch .netrc
echo "machine urs.earthdata.nasa.gov login <uid> password <password>" >> .netrc 
chmod 0600 .netrc 
cd ~ or cd $HOME
touch .urs_cookies.
wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition -i <url.txt>

=======================
Running the scripts
=======================
~~~~~~~~~~~~~~~~~~~~~~~~
regrid_tropomi_part1.py
~~~~~~~~~~~~~~~~~~~~~~~~
This code screens satellite netCDF files and writes out ungridded files in a user specified domain into a user-specified directory.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
regrid_tropomi_part2.py & earthtrig.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
After part 1 is run, part 2 takes the screened files, makes a new grid, and sets the satellite data to new grid using a linear weight by distance. This step writes out gridded data in csv files to a directory. Part 2 also imports earthtrig.py from the directory you are running the code in.

~~~~~~~~~~~~~~~~~~~~~~~~
regrid_tropomi_part3.py
~~~~~~~~~~~~~~~~~~~~~~~~
After part 2 is run, part 3 takes the gridded files and plots these values. Part 3 only plots one l3 file at a time and you must specify which L3 file you want to plot.

