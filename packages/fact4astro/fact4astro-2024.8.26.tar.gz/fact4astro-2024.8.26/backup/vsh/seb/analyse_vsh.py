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

# Observations

# nom1, x1, y1, dx1, dy1, cor1, ns1, no1, epo1 = sc.readcatalog('CAT/cat-SIM1.txt')
# nom2, x2, y2, dx2, dy2, cor2, ns2, no2, epo2 = sc.readcatalog('CAT/cat-SIM2.txt')
nom1, x1, y1, dx1, dy1, cor1, ns1, no1, epo1 = sc.readcatalog('cat-SIM1.txt')
nom2, x2, y2, dx2, dy2, cor2, ns2, no2, epo2 = sc.readcatalog('cat-SIM2.txt')

# Max degree of the decomposition

lmax = 1

nsou = len(nom1)
npar = 2*lmax*(lmax+2)
lmaxmax = int(np.floor(np.sqrt(1+nsou))-1)
print(' ')
print(' N Sources      %8d' % nsou)
print(' N Observations %8d' % (2*nsou))
print(' L Max          %8d' % lmax)
print(' L Max Max      %8d' % lmaxmax)
print(' N Parameters   %8d' % npar)
print(' Resolution     %8d deg / %8d km' %
      (int(np.floor(360/lmax)), int(np.floor(360/lmax)*math.pi/180*6378)))
if npar > 2*nsou:
    print(' ')
    print(' L Max should be lower than %d' % lmaxmax)
    print(' ')
    sys.exit(0)

# The observation matrix

Y = np.zeros((2*nsou))
Y[0:2*nsou:2] = (x1-x2)*np.cos(y2*np.pi/180)*3600000
Y[1:2*nsou:2] = (y1-y2)*3600000
A = sv.vshmatrix(lmax, x2*np.pi/180, y2*np.pi/180)

# The variance-covariance and weight matrices

E = np.zeros((2, 2))
W = np.zeros((2*nsou, 2*nsou))  # This is big!
for i in range(0, nsou):
    E[0, 0] = dx1[i]**2+dx2[i]**2
    E[1, 1] = dy1[i]**2+dy2[i]**2
    E[0, 1] = dx1[i]*dy1[i]*cor1[i]+dx2[i]*dy2[i]*cor2[i]
    E[1, 0] = E[0, 1]
    tmp = pinv(E)
    W[2*i, 2*i] = tmp[0, 0]
    W[2*i+1, 2*i+1] = tmp[1, 1]
    W[2*i, 2*i+1] = tmp[0, 1]
    W[2*i+1, 2*i] = tmp[1, 0]

# Inversion and statistics of the residuals

U = pinv(np.dot(A.T, np.dot(W, A)))  # The normal matrix
X = np.dot(U, np.dot(A.T, np.dot(W, Y)))  # The estimated parameters
V = Y-np.dot(A, X)  # The residuals
dof = 2*nsou-npar-1
s2 = np.dot(V.T, np.dot(W, V))/dof  # The s**2 parameter
SX = np.sqrt(np.diag(U)).transpose()  # The standard errors on parameters
C = np.zeros((npar, npar))
for i in range(0, npar):
    for j in range(0, npar):
        C[i, j] = U[i, j]/np.sqrt(U[i, i]*U[j, j])
xf = V[0:2*nsou:2]
yf = V[1:2*nsou:2]
W = np.zeros((2*nsou))
for i in range(0, nsou):
    W[2*i] = np.sqrt(dx1[i]**2+dx2[i]**2)
    W[2*i+1] = np.sqrt(dy1[i]**2+dy2[i]**2)
sdep = sf.wstd(Y, W)
sfin = sf.wstd(V, W)
cdep = sf.wki2(Y, W)
cfin = sf.wki2(V, W)

# Hypothese nulle : la valeur des parametres est coherente avec le spectre
# d'une variable aleatoire de moyenne nulle et d'ecart-type sigma.
# I.e. sa valeur est due au hasard.

# sigma=np.std(Y)
# Z=np.abs(X)*np.sqrt(dof)/sigma  # equivalent de X mais centre et d'ecart-type 1
# pval=2*norm.cdf(-Z)
# seuil=95
# alpha=1-seuil/100
# Z0=norm.ppf(1-alpha/2)  # seuil theorique au risque alpha
# sval95=Z0*sigma/np.sqrt(dof)
# seuil=99.7
# alpha=1-seuil/100
# Z0=norm.ppf(1-alpha/2)  # seuil theorique au risque alpha
# sval99=Z0*sigma/np.sqrt(dof)

# Amplitudes and their significance

R = np.zeros((lmax))
T = np.zeros((lmax))
S = np.zeros((lmax))
ST = np.zeros((lmax))
SS = np.zeros((lmax))
WT = np.zeros((lmax))
WS = np.zeros((lmax))
ZT = np.zeros((lmax))
ZS = np.zeros((lmax))
k = 0
for l in range(1, lmax+1):
    sigmal0t = SX[k]
    sigmal0s = SX[k+1]
    T[l-1] = X[k]**2
    S[l-1] = X[k+1]**2
    ST[l-1] = SX[k]**2
    SS[l-1] = SX[k+1]**2
    WT[l-1] = X[k]**2/((sigmal0t**2)/2)
    WS[l-1] = X[k+1]**2/((sigmal0s**2)/2)
    k = k+2
    for m in range(1, l+1):
        T[l-1] = T[l-1]+X[k]**2+X[k+2]**2
        S[l-1] = S[l-1]+X[k+1]**2+X[k+3]**2
        ST[l-1] = ST[l-1]+SX[k]**2+SX[k+2]**2
        SS[l-1] = SS[l-1]+SX[k+1]**2+SX[k+3]**2
        WT[l-1] = WT[l-1]+(X[k]**2+X[k+2]**2)/((sigmal0t**2)/2)
        WS[l-1] = WS[l-1]+(X[k+1]**2+X[k+3]**2)/((sigmal0s**2)/2)
        k = k+4
    ZT[l-1] = np.sqrt((9*(2*l+1)/2))*((WT[l-1]/(2*l+1))**(1/3)-(1-2/(9*(2*l+1))))
    ZS[l-1] = np.sqrt((9*(2*l+1)/2))*((WS[l-1]/(2*l+1))**(1/3)-(1-2/(9*(2*l+1))))
    V = Y-np.dot(A[:, 0:k+4], X[0:k+4])
    R[l-1] = sf.wstd(V, W)
print(' S2 Scaling Parameter       %8.3f' % s2)
print(' Data     Stdev and Chi2    %8.3f    %8.2f' % (sdep, cdep))
print(' Residual Stdev and Chi2    %8.3f    %8.2f' % (sfin, cfin))
print(' ')
print('  l      Tl      +-       Z       Sl      +-       Z       R')
print('                                                     %7.3f' % sdep)
for l in range(1, lmax+1):
    print('%3d %7.3f %7.3f %7.2f  %7.3f %7.3f %7.2f %7.3f' %
          (l, T[l-1], ST[l-1], ZT[l-1], S[l-1], SS[l-1], ZS[l-1], R[l-1]))
print(' ')

# Rotation and glide

R1 = -np.sqrt(3/4/np.pi)*X[2]
R2 = np.sqrt(3/4/np.pi)*X[4]
R3 = np.sqrt(3/8/np.pi)*X[0]
SR1 = np.abs(np.sqrt(3/4/np.pi)*SX[2])
SR2 = np.abs(np.sqrt(3/4/np.pi)*SX[4])
SR3 = np.abs(np.sqrt(3/8/np.pi)*SX[0])
print('                     X       Y       Z    Ampli       RA      Dec')
print(' Rotation      %7.3f %7.3f %7.3f' % (R1, R2, R3))
print('       +-      %7.3f %7.3f %7.3f' % (SR1, SR2, SR3))
if lmax > 2:
    D1 = -np.sqrt(3/4/np.pi)*X[3]
    D2 = np.sqrt(3/4/np.pi)*X[5]
    D3 = np.sqrt(3/8/np.pi)*X[1]
    SD1 = np.abs(np.sqrt(3/4/np.pi)*SX[3])
    SD2 = np.abs(np.sqrt(3/4/np.pi)*SX[5])
    SD3 = np.abs(np.sqrt(3/8/np.pi)*SX[1])
    ad, xd, yd, dad, dxd, dyd = sc.amplidir(D1, D2, D3, SD1, SD2, SD3)
    print(' Glide         %7.3f %7.3f %7.3f %8.2f %8.1f %8.1f' % (D1, D2, D3, ad, xd, yd))
    print('       +-      %7.3f %7.3f %7.3f %8.2f %8.1f %8.1f' % (SD1, SD2, SD3, dad, dxd, dyd))
print(' ')

# Detailed amplitudes

#print(' ')
#print('         ---------- Toroidal ---------   ---------- Spheroidal -------')
#print('  l  m      Re      +-      Im      +-      Re      +-      Im      +-')
# k=0
# for l in range(1,lmax+1):
# m=0
# print('%3d%3d %7.3f %7.3f                 %7.3f %7.3f' % (l,m,X[k],SX[k],X[k+1],SX[k+1]))
# k=k+2
# for m in range(1,l+1):
#  print('%3d%3d %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f' % (l,m,X[k],SX[k],X[k+2],SX[k+2],X[k+1],SX[k+1],X[k+3],SX[k+3]))
#  k=k+4
#print(' ')
#print(' S2 Scaling Parameter       %8.3f' % s2)
#print(' 95pc Significance Level    %8.3f' % sval95)
#print(' 99pc Significance Level    %8.3f' % sval99)
#print(' Data     Stdev and Chi2    %8.3f    %8.2f' % (sdep,cdep))
#print(' Residual Stdev and Chi2    %8.3f    %8.2f' % (sfin,cfin))
#print(' ')

# Figures

# Plot of amplitudes

# plt.plot(range(1,lmax+1),P,'o')
# plt.fill_between([0.5,lmax+0.5],[0,0],[sval99,sval99],color='r',alpha=0.2)
#plt.xlabel('VSH Degree')
# plt.xlim((0.5,lmax+0.5))
# plt.grid(True,which='both')
# plt.xticks(np.arange(1,lmax+1))
# plt.show()
# plt.savefig('plot-vsh-ampli-l.png')
# plt.close()

# Plot of details amplitudes

# k=0
# j=1
# jmax=sum(range(2,lmax+2))
# plt.errorbar(-1,X[1],yerr=SX[1]*3,fmt='ro')
# plt.errorbar(-1,X[1],yerr=SX[1]*3,fmt='go')
# plt.errorbar(-1,X[1],yerr=SX[1]*3,fmt='bo')
# plt.errorbar(-1,X[1],yerr=SX[1]*3,fmt='mo')
# lab=[]
# for l in range(1,lmax+1):
# m=0
# lab.append(str(l)+','+str(m))
# plt.errorbar(j,X[k],yerr=SX[k]*3,fmt='ro')
# plt.errorbar(j,X[k+1],yerr=SX[k+1]*3,fmt='bo')
# j=j+1
# k=k+2
# for m in range(1,l+1):
#  lab.append(str(l)+','+str(m))
#  plt.errorbar(j,X[k],yerr=SX[k]*3,fmt='ro')
#  plt.errorbar(j,X[k+2],yerr=SX[k+2]*3,fmt='go')
#  plt.errorbar(j,X[k+1],yerr=SX[k+1]*3,fmt='bo')
#  plt.errorbar(j,X[k+3],yerr=SX[k+3]*3,fmt='mo')
#  j=j+1
#  k=k+4
#plt.legend(['Toroidal Real','Toroidal Imag','Spheroidal Real','Spheroidal Imag'])
# plt.fill_between([0.5,jmax+0.5],[-sval99,-sval99],[sval99,sval99],color='r',alpha=0.2)
#plt.xlabel('VSH Degree and Order')
# plt.xlim((0.5,jmax+0.5))
# plt.grid(True,which='both')
# plt.xticks(np.arange(1,jmax+1),lab,rotation=30)
# plt.show()
# plt.savefig('plot-vsh-ampli-lm.png')
# plt.close()

# Plot of correlations

# plt.matshow(np.absolute(C),cmap=plt.cm.jet)
# plt.colorbar()
# plt.show()
# plt.savefig('plot-vsh-correl.png')
# plt.close()

# Plot of spheres

# x=np.arange(-180,179,10)
# y=np.arange(-89,89,5)
# xm,ym=np.meshgrid(x,y)
# xmlin=np.reshape(xm,(len(x)*len(y),1))*np.pi/180
# ymlin=np.reshape(ym,(len(x)*len(y),1))*np.pi/180
# A=sv.vshmatrix(lmax,xmlin,ymlin)
# k=0
# for l in range(1,lmax+1):
# m=0
# V=A[:,k]*X[k]
# sv.vshhammer(xmlin,ymlin,V,'l='+str(l)+', m='+str(m)+', Toroidal Real','plot-vsh-harm-'+str(l)+str(m)+'TR.png')
# V=A[:,k+1]*X[k+1]
# sv.vshhammer(xmlin,ymlin,V,'l='+str(l)+', m='+str(m)+', Spheroidal Real','plot-vsh-harm-'+str(l)+str(m)+'SR.png')
# k=k+2
# for m in range(1,l+1):
#  V=A[:,k]*X[k]
#  sv.vshhammer(xmlin,ymlin,V,'l='+str(l)+', m='+str(m)+', Toroidal Real','plot-vsh-harm-'+str(l)+str(m)+'TR.png')
#  V=A[:,k+1]*X[k+1]
#  sv.vshhammer(xmlin,ymlin,V,'l='+str(l)+', m='+str(m)+', Spheroidal Real','plot-vsh-harm-'+str(l)+str(m)+'SR.png')
#  V=A[:,k+2]*X[k+2]
#  sv.vshhammer(xmlin,ymlin,V,'l='+str(l)+', m='+str(m)+', Toroidal Imag','plot-vsh-harm-'+str(l)+str(m)+'TI.png')
#  V=A[:,k+3]*X[k+3]
#  sv.vshhammer(xmlin,ymlin,V,'l='+str(l)+', m='+str(m)+', Spheroidal Imag','plot-vsh-harm-'+str(l)+str(m)+'SI.png')
#  k=k+4
