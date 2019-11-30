#!/bin/bash
#SBATCH -A b1045                # Allocation
#SBATCH -p buyin                # Queue
#SBATCH -t 2:00:00             # Walltime/duration of the jo
#SBATCH --output=wget_sat.out
#SBATCH --job-name="pullTropomi"       # Name of job
#SBATCH --mem=1G

module purge all
module load /software/Modules/3.2.9/modulefiles/python/anaconda3.6

#Download satellite data

# URL directory location
dirToURL="/home/asm0384"

#log into nasa 
cd ~
touch .netrc
echo "machine urs.earthdata.nasa.gov login $USERNAME password $PW" >> .netrc
chmod 0600 .netrc

#create cookies to get into nasa
cd ~
touch .urs_cookies

#download list of links from url.txt
wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition -i $dirToURL/url.txt -P /projects/b1045/NO2/
