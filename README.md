# l2_to_l3_tropomi

Regrid TropOMI L2 Data to CMAQ grid

Stacy Montgomery, Aug. 2021

stacy@earth.northwestern.edu

1. Using the get_sat.py script, you can download and regrid to your domain using HARP.
2. Using harp_to_cmaq.py, you can readjust the grid from degree spacing to CMAQ grid.


Libraries needed: harp, numpy, netCDF4, scipy (for calcs), matplotlib (for vis)
