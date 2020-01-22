
# module to do a few trigonometric things on a spherical earth,
# by Suzan vd lee
from math import pi, sin, cos, asin, acos, atan2
p = pi/180.

# equator through length of USA:
equatorlat = 40.
equatorlon = -100.
ola = (90.-equatorlat)*p
olo = (equatorlon + 180.)*p
oazi = 0.

# do not make changes below this line.
# ------------------------------------------------------

# function to rotate geographic coordinates on a spherical earth:
# mode 0, rotate from conventional to new
# mode 1, rotate from new to conventional
#
# input coordinates need to be in radians (tetain = latitude, fiin = longitude)
# output coordinates need to also be in radians
#
# Need to be defined in main program:
#      ola,olo,oazi
# lat and lon of new north pole and geographic azimuth of the new 0 meridian.
# Also: trig functions from math module need to be imported in main program, as follows:
# from math import sin, cos, asin, acos, atan2
# p = pi/180.
def rotate(mode,tetain,fiin):
      if mode == 0:
         ang1 = olo; ang2 = oazi
      elif mode == 1:
         ang2 = olo; ang1 = oazi
      else:
        tetaout = tetain 
        fiout = fiin
        mode = -1
        return

      ct = cos(tetain)
      st = sin(tetain)
      cf = cos(fiin)
      sf = sin(fiin)
      ca = cos(ola)
      sa = sin(ola)
      co = cos(ang1)
      so = sin(ang1)
      sum = ct*ca*(cf*co + sf*so) + st*sa
      if sum > 1.:
         print("WARNING, rotate: sum > 1 for ", tetain,fiin)
         sum= 1.
      tetaout = asin(sum) 
      fdiff = fiin - ang1
      sfo = sin(fdiff)
      cfo = cos(fdiff)
      teller = ct*sfo
      rnoemer = st*ca - ct*sa*cfo
      azimuth = atan2(teller,rnoemer)
      fiout = ang2 - azimuth
      return tetaout, fiout

def deltas(teta1,fi1,teta2,fi2):
   term1  = sin(teta1)*sin(teta2)
   factor2  = cos(teta1)*cos(teta2)
   factor1 = cos(fi1 - fi2)
   term2 = factor1*factor2
   som = term1 + term2
   delta = acos(som)
   return delta

def azimuths(teta1,fi1,teta2,fi2):
   factor1 = cos(teta2)
   factor2 = sin(teta1)
   factor3 = cos(fi2-fi1)
   term1 = sin(teta2)*cos(teta1)
   term2 = factor1*factor2*factor3
   teller = factor1*sin(fi2-fi1)
   rnoemer = term1 - term2
   azimuth = atan2(teller,rnoemer)
   return azimuth

def fi2(fi1,teta1,azimuth,delta):
   term1 = cos(delta)*sin(fi1)*cos(teta1)
   factor2 = sin(delta)*cos(azimuth)*sin(teta1)
   term2 = factor2*sin(fi1)
   factor3 = sin(delta)*sin(azimuth)
   term3 = factor3*cos(fi1)
   teller = term1 - term2 + term3
   term1 = cos(delta)*cos(fi1)*cos(teta1)
   term2 = factor2*cos(fi1)
   term3 = factor3*sin(fi1)
   rnoemer = term1 - term2 - term3
   return atan2(teller,rnoemer)

def teta2(teta1,azimuth,delta):
   term1 = cos(delta)*sin(teta1)
   term2 = sin(delta)*cos(azimuth)*cos(teta1)
   som = term1 + term2
   return asin(som)


def deltaz(teta1,fi1,teta2,fi2):
# lat (teta) and lon (fi) in radians!
# returned delta (distance) and azimuth are also in radians!
   if teta1 > 0.5*pi or teta1 < -0.5*pi:
      print('error, non-existent latitude '), teta1
      quit()
   if teta2 > 0.5*pi or teta2 < -0.5*pi:
      print('error, non-existent latitude ',teta2)
      quit()
   delta = deltas(teta1,fi1,teta2,fi2)
   azimuth = azimuths(teta1,fi1,teta2,fi2)
   return delta, azimuth

def azdelt(teta1,fi1,delta,azimuth):
# all input and output in radians!
   if teta1 > 0.5*pi or teta1 < -0.5*pi:
      print('error, non-existent latitude ', teta1)
      quit()
   if delta < 0.:
      print('error, non-existent delta ',delta)
      quit()
   f = fi2(fi1,teta1,azimuth,delta)
   t = teta2(teta1,azimuth,delta)
   return t, f
