def stand(a):
 import numpy as np
 aa=(a-np.mean(a))/np.std(a)
 return aa

def dof(a):
 import numpy as np
 a=(a-np.mean(a))/(np.std(a)*len(a))
 ac=np.correlate(a,a,"full")
 ac=ac[int(len(ac)/2):]
 ac=ac/ac[0]
 idx=np.where((np.diff(ac>1/np.exp(1))))[0]
 tmp=idx+(1/np.exp(1)-ac[idx])/(ac[idx+1]-ac[idx])
 tau=tmp[0]
 d=len(a)/tau
 return d
 
def corrarn(ax,am,cx,seuil):
 import numpy as np
 from scipy.stats import norm
 zx=0.5*np.log((1+cx)/(1-cx))  # transformation de Fisher
 alpha=1-seuil/100
 qz=norm.ppf(1-alpha/2)  # seul theorique au risque alpha
 dofm=dof(am)
 dofx=dof(ax)
 szm=1/np.sqrt(dofm-3)
 szx=1/np.sqrt(dofx-3)
 szx=np.sqrt(szx**2+szm**2)
 fzx=abs(zx/szx)  # nb de deviations standards
 z1=zx-qz*szx
 z2=zx+qz*szx
 dcx1=(np.exp(2*z1)-1)/(np.exp(2*z1)+1)
 dcx2=(np.exp(2*z2)-1)/(np.exp(2*z2)+1)
 return dcx1,dcx2,fzx
 
def corrar0(ax,am,cx,seuil):
 import numpy as np
 from scipy.stats import norm
 zx=0.5*np.log((1+cx)/(1-cx))  # transformation de Fisher
 alpha=1-seuil/100
 qz=norm.ppf(1-alpha/2)  # seul theorique au risque alpha
 sz=1/np.sqrt(len(ax)-3)
 fzx=abs(zx/sz)
 z1=zx-qz*sz
 z2=zx+qz*sz
 dcx1=(np.exp(2*z1)-1)/(np.exp(2*z1)+1)
 dcx2=(np.exp(2*z2)-1)/(np.exp(2*z2)+1)
 return dcx1,dcx2,fzx
 
def xcorr(x,y,formule):
 import numpy as np
 import scipy.stats as ss
 l=np.zeros((len(x)*2-1,1))
 c=np.zeros((len(x)*2-1,1))
 p=np.zeros((len(x)*2-1,1))
 for i in range(-len(x)+1,len(x)):
  xr=np.roll(x,i)
  l[i+len(x)-1]=i
  if formule==0:
   c[i+len(x)-1],p[i+len(x)-1]=ss.pearsonr(xr,y)
  else:
   c[i+len(x)-1],p[i+len(x)-1]=ss.spearmanr(xr,y)
  c[i+len(x)-1]=c[i+len(x)-1]*(len(x)-abs(i))/len(x)
 return c,p,l

def avp1(t,x,dx):
 import numpy as np
 te=t[2]-t[1]
 N=len(t)
 tau=[]
 sig=[]
 for j in range(1,int(N/2)):
  L=int(N/j)
  if j>1:
   s=np.zeros(L)
   ds=np.zeros(L)
   for i in range(1,L):
    idx=np.where((t>=t[(i-1)*j])&(t<=t[i*j]))
    s[i]=wmean(x[idx],dx[idx])
    ds[i]=wstd(x[idx],dx[idx])
  else:
   s=x
   ds=dx
  tau.append(float(j*te))
  aux=0
  p=0
  for i in range(0,L-1):
   aux=aux+(s[i+1]-s[i])**2/(ds[i+1]**2+ds[i]**2)
   p=p+1/(ds[i+1]**2+ds[i]**2)
  sig.append(float(aux/(2*p)))
 tau=np.array(tau)
 sig=np.array(sig)
 return tau,sig 

def avp2(t,x,dx):
 import numpy as np
 te=t[2]-t[1]
 N=len(t)
 tau=[]
 sig=[]
 for j in range(1,int(np.log(N)/np.log(2))):
  M=int(2**j)
  L=int(N/M)
  if M>1:
   s=np.zeros(L)
   ds=np.zeros(L)
   for i in range(1,L):
    idx=np.where((t>=t[(i-1)*M])&(t<=t[i*M]))
    s[i]=wmean(x[idx],dx[idx])
    ds[i]=wstd(x[idx],dx[idx])
  else:
   s=x
   ds=dx
  tau.append(float(M*te))
  aux=0
  p=0
  for i in range(0,L-1):
   aux=aux+(s[i+1]-s[i])**2/(ds[i+1]**2+ds[i]**2)
   p=p+1/(ds[i+1]**2+ds[i]**2)
  sig.append(float(aux/(2*p)))
 tau=np.array(tau)
 sig=np.array(sig)
 return tau,sig 

def avp3(t,x,dx):
 import numpy as np
 te=t[2]-t[1]
 N=len(t)
 tau=[]
 sig=[]
 for j in range(0,int(np.log(N)/np.log(2))-1):
  M=int(2**j)
  L=int(N/M)
  if M>1:
   s=np.zeros(L)
   ds=np.zeros(L)
   for i in range(1,L):
    idx=np.where((t>=t[(i-1)*M])&(t<=t[i*M]))
    s[i]=wmean(x[idx],dx[idx])
    ds[i]=wstd(x[idx],dx[idx])
  else:
   s=x
   ds=dx
  tau.append(float(M*te))
  s1=s[1:-2:2]
  s2=s[2:-1:2]
  ss=s2-s1
  ds1=ds[1:-2:2]
  ds2=ds[2:-1:2]
  dss=ds2+ds1
  aux=0
  p=0
  for i in range(0,len(ss)-1):
   aux=aux+(ss[i+1]-ss[i])**2/(dss[i+1]**2+dss[i]**2)
   p=p+1/(dss[i+1]**2+dss[i]**2)
  sig.append(float(aux/(2*p)))
 tau=np.array(tau)
 sig=np.array(sig)
 return tau,sig 

def wmean(x,dx):
 import numpy as np
 if np.size(x)>0:
  w=1/dx**2
  return sum(x*w)/sum(w)
 else:
  return 0

def wvar(x,dx):
 import numpy as np
 if np.size(x)>0:
  w=1/dx**2
  m=wmean(x,dx)
  b=(x-m)**2
  return sum(b*w)/sum(w)
 else:
  return 0

def wstd(x,dx):
 import numpy as np
 if np.size(x)>0:
  return np.sqrt(wvar(x,dx))
 else:
  return 0
    
def wki2(x,dx):
 import numpy as np
 if np.size(x)>0:
  w=1/dx**2
  m=wmean(x,dx)
  b=(x-m)**2
  return sum(b*w)/np.size(x)
 else:
  return 0
     
def wslope(t,x,dx):
 import numpy as np
 n=np.size(t)
 if n<2:
  a=0;
  da=0;
 else:
  Y=np.zeros((n))
  W=np.zeros((n,n))
  A=np.zeros((n,2))
  U=np.zeros((2,2))
  X=np.zeros((2))
  Y[0:n]=x
  for i in range(0,n):
   W[i,i]=1/dx[i]**2
  A=np.vstack((t,np.ones((n)))).T
  U=np.linalg.pinv(np.dot(A.T,np.dot(W,A)))  # The normal matrix
  X=np.dot(U,np.dot(A.T,np.dot(W,Y)))  # The estimated parameters
  V=Y-np.dot(A,X)  # The residuals
  s2=np.dot(V.T,np.dot(W,V))/(n)  # The s**2 parameter
  if n>3:
   s2=np.dot(V.T,np.dot(W,V))/(n-3)  # The s**2 parameter
  DX=np.sqrt(np.diag(U)*s2)  # The standard errors on parameters
  a=X[0]
  b=X[1]
  da=DX[0]
  db=DX[1]
 return a,da
    
def dewslope(t,x,dx):
 import numpy as np
 n=len(t)
 Y=np.zeros((n))
 W=np.zeros((n,n))
 A=np.zeros((n,2))
 U=np.zeros((2,2))
 X=np.zeros((2))
 Y[0:n]=x
 for i in range(0,n):
  W[i,i]=1/dx[i]**2
 A=np.vstack((t,np.ones((len(t))))).T
 U=np.linalg.pinv(np.dot(A.T,np.dot(W,A)))  # The normal matrix
 X=np.dot(U,np.dot(A.T,np.dot(W,Y)))  # The estimated parameters
 a=X[0]
 b=X[1]
 xs=x-(a*t+b)
 return xs
    
def deslope(t,x):
 import numpy as np
 n=len(t)
 Y=np.zeros((n))
 A=np.zeros((n,2))
 U=np.zeros((2,2))
 X=np.zeros((2))
 Y[0:n]=x
 A=np.vstack((t,np.ones((len(t))))).T
 U=np.linalg.pinv(np.dot(A.T,A))  # The normal matrix
 X=np.dot(U,np.dot(A.T,Y))  # The estimated parameters
 a=X[0]
 b=X[1]
 xs=x-(a*t+b)
 return xs
    
def mjd2dc(mjd):
 import numpy as np
 dc=np.zeros((len(mjd)))
 for i in range(0,len(mjd)):
  dc[i]=2000-(51544.5-mjd[i])/365.25
 return dc
    
def dc2mjd(dc):
 import numpy as np
 mjd=np.zeros((len(dc)))
 for i in range(0,len(dc)):
  mjd[i]=51544.5-(2000-dc[i])*365.25
 return mjd
    
def smooth(t,x,dt,m):
 import numpy as np
 y=np.zeros((len(t),1))
 if m==0:
  for i in range(0,len(t)):
   y[i]=np.mean(x[(t>t[i]-dt/2)&(t<t[i]+dt/2)])
 else:
  for i in range(0,len(t)):
   y[i]=np.median(x[(t>t[i]-dt/2)&(t<t[i]+dt/2)])
 y=np.squeeze(y);
 return y

def wsmooth(t,x,dx,dt):
 import numpy as np
 y=np.zeros((len(t),1))
 dy=np.zeros((len(t),1))
 for i in range(0,len(t)):
  idx=np.where((t>t[i]-dt/2)&(t<t[i]+dt/2))[0]
  y[i]=wmean(x[idx],dx[idx])
  dy[i]=wstd(x[idx],dx[idx])
 y=np.squeeze(y);
 dy=np.squeeze(dy);  
 return(y,dy)
