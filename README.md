# l2_to_l3_tropomi

Regrid TropOMI L2 Data
Stacy Montgomery, NOV 2018 - DEC 2020
stacy@earth.northwestern.edu

1. Pull satellite files using get)satellite.sh
2. Run part 1 to crop the satellite files into a more manageable domain -- necessary because part 2 will apply a function that will use a lot of memory, so you want to minimize the number of points you're applying. This also pulls only the data that is relevant, puts it in a format that part 2 will use.
3. Run part 2 on cropped netcdf files to create a csv output file with centers corresponding to the grid you input into it.
