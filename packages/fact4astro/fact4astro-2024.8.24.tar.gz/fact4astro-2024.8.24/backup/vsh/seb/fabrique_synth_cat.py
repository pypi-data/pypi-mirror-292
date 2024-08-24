import math
import sys
import numpy as np
import datetime
import sebform as sf
import sebcrf as sc
import sebvsh as sv
from numpy.linalg import pinv
from scipy.stats import norm
import matplotlib.pyplot as plt
import string
import random

def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
 return ''.join(random.choice(chars) for _ in range(size))
 
# Observations

nlon=20
nlat=10
nsou=nlon*nlat;
dlon=359/nlon
dlat=179/nlat
x1=np.zeros((nsou,1))
y1=np.zeros((nsou,1))
dx1=np.ones((nsou,1))
dy1=np.ones((nsou,1))
x2=np.zeros((nsou,1))
y2=np.zeros((nsou,1))
dx2=np.ones((nsou,1))
dy2=np.ones((nsou,1))
cor1=np.zeros((nsou,1))
cor2=np.zeros((nsou,1))
nom=['00000000']*nsou
k=0
for i in range(0,nlon):
 for j in range(0,nlat):
  x1[k]=i*dlon
  x2[k]=x1[k]
  y1[k]=-90+(j+1)*dlat
  y2[k]=y1[k]
  dx1[k]=0.00001/np.cos(y1[k]*math.pi/180)
  dy1[k]=0.00001
  dx2[k]=dx1[k]
  dy2[k]=dy1[k]
  nom[k]=id_generator()
  k=k+1

nses=1000
nobs=10000
mjd=51544.5
fid0=open('../../CAT/cat-SIM1.txt','w')
for i in range(0,nsou):
    x=x1[i]/15
    y=y1[i]
    dx=dx1[i]/15
    dy=dy1[i]
    cxy=cor1[i]
    ihr=int(np.floor(x))
    x=(x-ihr)*60
    ihm=int(np.floor(x))
    x=(x-ihm)*60
    dhs=x
    idr=int(np.floor(y))
    y=(y-idr)*60
    idm=int(np.floor(y))
    y=(y-idm)*60
    dds=y
    if idr<0:
     signe='-1'
     idr=-idr
    else:
     signe='+1'
    fid0.write('%8s %2d %2d %11.8f %11.8f %2s %2d %2d %10.7f %10.7f %6.3f %7d %7d %9.1f\n' % (nom[i],ihr,ihm,dhs,dx,signe,idr,idm,dds,dy,cxy,nses,nobs,mjd))
fid0.close()

R1=0  # mas
R2=0
R3=1
R1=R1/3600000
R2=R2/3600000
R3=R3/3600000
for i in range(0,nsou):
 cosalpha=np.cos(x2[i]*math.pi/180)
 cosdelta=np.cos(y2[i]*math.pi/180)
 sinalpha=np.sin(x2[i]*math.pi/180)
 sindelta=np.sin(y2[i]*math.pi/180)
 deltax=-R1*cosalpha*sindelta-R1*sinalpha*sindelta+R3*cosdelta
 deltay=R1*sinalpha-R2*cosalpha
 x2[i]=x2[i]+deltax/cosdelta
 y2[i]=y2[i]+deltay

fid0=open('../../CAT/cat-SIM2.txt','w')
for i in range(0,nsou):
    x=x2[i]/15
    y=y2[i]
    dx=dx2[i]/15
    dy=dy2[i]
    cxy=cor2[i]
    ihr=int(np.floor(x))
    x=(x-ihr)*60
    ihm=int(np.floor(x))
    x=(x-ihm)*60
    dhs=x
    idr=int(np.floor(y))
    y=(y-idr)*60
    idm=int(np.floor(y))
    y=(y-idm)*60
    dds=y
    if idr<0:
     signe='-1'
     idr=-idr
    else:
     signe='+1'
    fid0.write('%8s %2d %2d %11.8f %11.8f %2s %2d %2d %10.7f %10.7f %6.3f %7d %7d %9.1f\n' % (nom[i],ihr,ihm,dhs,dx,signe,idr,idm,dds,dy,cxy,nses,nobs,mjd))
fid0.close()
