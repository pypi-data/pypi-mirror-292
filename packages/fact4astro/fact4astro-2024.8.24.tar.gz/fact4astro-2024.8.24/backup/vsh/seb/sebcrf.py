def meanepoch(epo, no):
    import numpy as np
    mep = sum(epo/no)/sum(1/no)
    mep = 2000-(51544.5-mep)/365.25
    return(mep)


def usn4plot(x1, y1, dx1, dy1, x2, y2, dx2, dy2, titre):
    import numpy as np
    import matplotlib.pyplot as plt
    import sebform as sf
    x = x1/15
    y = y1
    dx = (x2-x1)*np.cos(y1*np.pi/180)*3600000
    dy = (y2-y1)*3600000
    rx = sf.wstd(dx, np.sqrt(dx1**2+dx2**2))
    ry = sf.wstd(dy, np.sqrt(dy1**2+dy2**2))
    cx = sf.wki2(dx, np.sqrt(dx1**2+dx2**2))
    cy = sf.wki2(dy, np.sqrt(dy1**2+dy2**2))
    plt.subplot(2, 2, 1)
    plt.scatter(x, dx, s=0.5)
    plt.xlim((0, 24))
    plt.xticks(np.arange(0, 30, 6))
    plt.ylim((-1, 1))
# plt.grid(True,which='both')
    plt.ylabel('Rel. RA cos Dec (mas)')
    #plt.text(6, 0.6,'rms = %6.3f mas' % rx)
    #plt.text(6,-0.6,'chi2 = %5.2f' % cx)
    plt.subplot(2, 2, 2)
    plt.scatter(y, dx, s=0.5)
    plt.xlim((-90, 90))
    plt.xticks(np.arange(-90, 120, 30))
    plt.ylim((-1, 1))
# plt.grid(True,which='both')
    plt.subplot(2, 2, 3)
    plt.scatter(x, dy, s=0.5)
    plt.xlim((0, 24))
    plt.xticks(np.arange(0, 30, 6))
    plt.ylim((-1, 1))
# plt.grid(True,which='both')
    plt.xlabel('RA (hr)')
    plt.ylabel('Rel. Dec (mas)')
    #plt.text(6, 0.6,'rms = %6.3f mas' % ry)
    #plt.text(6,-0.6,'chi2 = %5.2f' % cy)
    plt.subplot(2, 2, 4)
    plt.scatter(y, dy, s=0.5)
    plt.xlim((-90, 90))
    plt.xticks(np.arange(-90, 120, 30))
    plt.ylim((-1, 1))
# plt.grid(True,which='both')
    plt.xlabel('Dec (deg)')
    plt.suptitle(titre)


def plotconciserep(fichier, c1, c2, c3):
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as ptc
    x = []
    dx = []
    for line in open(fichier):
        if 'TPAR' in line:
            p = line.split()
            x.append(float(p[3]))
            dx.append(float(p[5]))
    x = np.array(x)
    dx = np.array(dx)
    axes = plt.gca()
    for i in range(0, 3):
        axes.add_artist(ptc.Rectangle((i-0.1, x[i]-dx[i]), 0.2, 2*dx[i], color='blue', zorder=2))
        plt.plot([i-0.1, i-0.1], [x[i]-dx[i], x[i]+dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
        plt.plot([i+0.1, i+0.1], [x[i]-dx[i], x[i]+dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
        plt.plot([i-0.1, i+0.1], [x[i]-dx[i], x[i]-dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
        plt.plot([i-0.1, i+0.1], [x[i]+dx[i], x[i]+dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
    for i in range(3, 6):
        axes.add_artist(ptc.Rectangle((i-0.1, x[i]-dx[i]), 0.2, 2*dx[i], color='skyblue', zorder=2))
        plt.plot([i-0.1, i-0.1], [x[i]-dx[i], x[i]+dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
        plt.plot([i+0.1, i+0.1], [x[i]-dx[i], x[i]+dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
        plt.plot([i-0.1, i+0.1], [x[i]-dx[i], x[i]-dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
        plt.plot([i-0.1, i+0.1], [x[i]+dx[i], x[i]+dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
    for i in range(6, 16):
        axes.add_artist(ptc.Rectangle((i-0.1, x[i]-dx[i]), 0.2, 2*dx[i], color='cyan', zorder=2))
        plt.plot([i-0.1, i-0.1], [x[i]-dx[i], x[i]+dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
        plt.plot([i+0.1, i+0.1], [x[i]-dx[i], x[i]+dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
        plt.plot([i-0.1, i+0.1], [x[i]-dx[i], x[i]-dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
        plt.plot([i-0.1, i+0.1], [x[i]+dx[i], x[i]+dx[i]],
                 'k', linewidth=0.5, color='black', zorder=3)
    plt.rc('axes', axisbelow=True)
    plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], ['$R_1$', '$R_2$', '$R_3$', '$D_1$', '$D_2$', '$D_3$',
                                                                            '$E_{20}$', '$M_{20}$', '$E_{21}^R$', '$E_{21}^I$', '$M_{21}^R$', '$M_{21}^I$', '$E_{22}^R$', '$E_{22}^I$', '$M_{22}^R$', '$M_{22}^I$'])
    plt.ylabel('$\mu$as')
    plt.xlim(-0.5, 15.5)
    plt.axhline(0, color='black', linewidth=0.5)
# plt.grid()


def plotconciserep2(fichier, c1):
    import numpy as np
    import matplotlib.pyplot as plt
    x = []
    dx = []
    for line in open(fichier):
        if 'TPAR' in line:
            p = line.split()
            x.append(float(p[3]))
            dx.append(float(p[5]))
    x = np.array(x)
    dx = np.array(dx)
    for i in range(0, 16):
        plt.plot([i, i], [x[i]-dx[i], x[i]+dx[i]], c1, linewidth=6)
    plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], ['$R_1$', '$R_2$', '$R_3$', '$D_1$', '$D_2$', '$D_3$',
                                                                            '$E_{20}$', '$M_{20}$', '$E_{21}^R$', '$E_{21}^I$', '$M_{21}^R$', '$M_{21}^I$', '$E_{22}^R$', '$E_{22}^I$', '$M_{22}^R$', '$M_{22}^I$'])
    plt.ylabel('$\mu$as')
    plt.axhline(0, color='black')
    plt.xlim(-0.5, 15.5)
    plt.grid()


def plotrovecxy(x, y, c1, c2):
    import numpy as np
    import matplotlib.pyplot as plt
    plt.plot([0], [0], '.', color=c1)
    plt.plot([x], [y], '.', color=c2)


def plotrovecra(majr, minr, par, majo, mino, pao, rad, pad, c1, c2):
    import numpy as np
    import matplotlib.pyplot as plt
    a = np.arange(0, 360, 1)
    xr = np.zeros((len(a)))
    yr = np.zeros((len(a)))
    xo = np.zeros((len(a)))
    yo = np.zeros((len(a)))
    for i in range(0, len(a)):
        xr[i] = majr*np.cos(a[i]*np.pi/180)
        yr[i] = minr*np.sin(a[i]*np.pi/180)
        xo[i] = majo*np.cos(a[i]*np.pi/180)
        yo[i] = mino*np.sin(a[i]*np.pi/180)
    c = np.cos(par)
    s = np.sin(par)
    xrr = xr*c-yr*s
    yrr = xr*s+yr*c
    c = np.cos(pao)
    s = np.sin(pao)
    xor = xo*c-yo*s
    yor = xo*s+yo*c
    xr = xrr
    yr = yrr
    xo = xor
    yo = yor
    xo = xo+rad*np.cos(pad*np.pi/180)  # pad is counterclockwise from delta=0 to right
    yo = yo+rad*np.sin(pad*np.pi/180)
    plt.plot([0], [0], '.', color=c1)
    plt.plot([rad*np.cos(pad*np.pi/180)], [rad*np.sin(pad*np.pi/180)], '.', color=c2)
    plt.plot(xr, yr, c1)
    plt.plot(xo, yo, c2)


def ellip(majo, mino, pao, rad, pad):
    import numpy as np
    a = np.arange(0, 360, 1)
    xo = np.zeros((len(a)))
    yo = np.zeros((len(a)))
    for i in range(0, len(a)):
        xo[i] = majo*np.cos(a[i]*np.pi/180)
        yo[i] = mino*np.sin(a[i]*np.pi/180)
    c = np.cos(pao*np.pi/180)
    s = np.sin(pao*np.pi/180)
    xor = xo*c-yo*s
    yor = xo*s+yo*c
    xo = xor
    yo = yor
    xo = xo+rad*np.cos(pad*np.pi/180)  # pad is counterclockwise from delta=0 to right
    yo = yo+rad*np.sin(pad*np.pi/180)
    return(xo, yo)


def amplidir(d1, d2, d3, dd1, dd2, dd3):
    import math
    import numpy as np
    ad = np.sqrt(d1**2+d2**2+d3**2)
    dad = (dd1*np.absolute(d1)+dd2*np.absolute(d2)+dd3*np.absolute(d3))/ad
    xd = np.arctan2(d2, d1)
    if xd < 0:
        xd = xd+2*math.pi
    yd = np.arctan2(d2*d3, (d1**2+d2**2)*np.sin(xd))
    if yd > math.pi/2:
        yd = yd-math.pi
    if yd < -math.pi/2:
        yd = yd+math.pi
    yd = yd*180/math.pi
    dxd = np.sqrt(((dd1*d2)**2+(dd2*d1)**2)/(d1**2+d2**2)**2)*180/math.pi
    dyd = np.sqrt((dd1**2*d1**2*d3**2+dd2**2*d1**2*d2**2)
                  / ((d1**2+d2**2)*(d1**2+d2**2+d3**2)**2)
                  + dd3**2*(d1**2+d2**2)/(d1**2+d2**2+d3**2)**2)*180/math.pi
    xd = xd*180/math.pi
    return ad, xd, yd, dad, dxd, dyd


def concisedef(col, labcat, cat, chemin, ref):
    import numpy as np
    import matplotlib.pyplot as plt
    for ncat in range(0, len(cat)):
        x = []
        dx = []
        for line in open(chemin+'/par-'+cat[ncat]+'-'+ref+'.txt'):
            if 'TPAR' in line:
                p = line.split()
                x.append(float(p[3]))
                dx.append(float(p[5]))
        x = np.array(x)
        dx = np.array(dx)
        for i in range(6, 16):
            plt.plot([i-6+float(ncat)/10, i-6+float(ncat)/10],
                     [x[i]-dx[i], x[i]+dx[i]], col[ncat], linewidth=6)
    plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], ['$E_{20}$', '$M_{20}$', '$E_{21}^R$', '$E_{21}^I$',
                                                '$M_{21}^R$', '$M_{21}^I$', '$E_{22}^R$', '$E_{22}^I$', '$M_{22}^R$', '$M_{22}^I$'])
    plt.ylabel('$\mu$as')
    plt.axhline(0, color='black')
    plt.xlim(-0.5, 10)
    plt.grid()


def conciserot(col, labcat, cat, chemin, ref):
    import numpy as np
    import matplotlib.pyplot as plt
    for ncat in range(0, len(cat)):
        x = []
        dx = []
        for line in open(chemin+'/par-'+cat[ncat]+'-'+ref+'.txt'):
            if 'TPAR' in line:
                p = line.split()
                x.append(float(p[3]))
                dx.append(float(p[5]))
        x = np.array(x)
        dx = np.array(dx)
        for i in range(0, 6):
            plt.plot([i+float(ncat)/10, i+float(ncat)/10],
                     [x[i]-dx[i], x[i]+dx[i]], col[ncat], linewidth=6)
    plt.xticks([0, 1, 2, 3, 4, 5], ['$R_1$', '$R_2$', '$R_3$', '$D_1$', '$D_2$', '$D_3$'])
    plt.ylabel('$\mu$as')
    plt.axhline(0, color='black')
    plt.xlim(-0.5, 6)
    plt.grid()


def readlist(fichier):
    import numpy as np
    fid = open(fichier, 'r')
    lines = fid.readlines()
    noms = []
    for line in lines:
        p = line.split()
        noms.append(str(p[0]))
    fid.close()
    noms = np.array(noms)
    return noms


def readeop(eop):
    import numpy as np
    f = open(eop, 'r')
    lines = f.readlines()
    tk = []
    xk = []
    yk = []
    uk = []
    Xk = []
    Yk = []
    dxk = []
    dyk = []
    duk = []
    dXk = []
    dYk = []
    for line in lines:
        p = line.split()
        tk.append(float(p[0]))
        xk.append(float(p[1]))
        yk.append(float(p[2]))
        uk.append(float(p[3]))
        Xk.append(float(p[4]))
        Yk.append(float(p[5]))
        dxk.append(float(p[6]))
        dyk.append(float(p[7]))
        duk.append(float(p[8]))
        dXk.append(float(p[9]))
        dYk.append(float(p[10]))
    f.close()
    tk = np.array(tk)
    xk = np.array(xk)
    yk = np.array(yk)
    uk = np.array(uk)
    Xk = np.array(Xk)
    Yk = np.array(Yk)
    dxk = np.array(dxk)
    dyk = np.array(dyk)
    duk = np.array(duk)
    dXk = np.array(dXk)
    dYk = np.array(dYk)
    return(tk, xk, yk, uk, Xk, Yk, dxk, dyk, duk, dXk, dYk)


def readcatalog(catalogue):
    import math
    import numpy as np
    fid = open(catalogue, 'r')
    lines = fid.readlines()
    nom1 = []
    x1 = []
    y1 = []
    dx1 = []
    dy1 = []
    cor1 = []
    ns1 = []
    no1 = []
    epo1 = []
    for line in lines:
        p = line.split()
        nom1.append(str(p[0]))
        x1.append((float(p[1])+float(p[2])/60+float(p[3])/3600)*15)
        y1.append((float(p[6])+float(p[7])/60+float(p[8])/3600)*float(p[5]))
        dx1.append(float(p[4])*15*1e3)
        dy1.append(float(p[9])*1e3)
        cor1.append(float(p[10]))
        ns1.append(int(p[11]))
        no1.append(int(p[12]))
        epo1.append(float(p[13]))
    fid.close()
    nom1 = np.array(nom1)
    x1 = np.array(x1)
    y1 = np.array(y1)
    dx1 = np.array(dx1)
    dy1 = np.array(dy1)
    cor1 = np.array(cor1)
    ns1 = np.array(ns1)
    no1 = np.array(no1)
    epo1 = np.array(epo1)
    dx1 = dx1*np.cos(y1*(math.pi/180))
    for i in range(0, len(nom1)):
        if cor1[i] > 1:
            cor1[i] = 0.9999
        if cor1[i] < -1:
            cor1[i] = -0.9999
    return(nom1, x1, y1, dx1, dy1, cor1, ns1, no1, epo1)


def eema(dx3, dy3, cor3):
    import math
    import numpy as np
    a = dx3
    b = dy3
    r = cor3
    rab = r*a*b
    theta = 0.5*np.arctan2(2*rab, (a**2-b**2))
    sx = a**2*np.cos(theta)**2+b**2*np.sin(theta)**2+2*rab*np.sin(theta)*np.cos(theta)  # semi-
    sy = a**2*np.sin(theta)**2+b**2*np.cos(theta)**2-2*rab*np.sin(theta)*np.cos(theta)  # semi-
    eema3 = np.sqrt(np.maximum(sx, sy))
    eena3 = np.sqrt(np.minimum(sx, sy))
    theta[(theta < 0)] = theta[(theta < 0)]+math.pi
    theta[(theta > math.pi)] = theta[(theta > math.pi)]-math.pi
    return(eema3, eena3, theta)


def haricot(x, y, dx, dy):
    import math
    import numpy as np
    import sebform as sf
    phi = np.arange(0, 180, 1)
    n = len(phi)
    sxf = np.zeros(n)
    for i in range(0, n):
        xf = x*np.cos(phi[i]*math.pi/180)+y*np.sin(phi[i]*math.pi/180)
        dxf = np.absolute(dx*np.cos(phi[i]*math.pi/180))+np.absolute(dy*np.sin(phi[i]*math.pi/180))
        sxf[i] = sf.wstd(xf, dxf)
    rx = sxf*np.cos(phi*math.pi/180)
    ry = sxf*np.sin(phi*math.pi/180)
    return phi, rx, ry


def plotevd(y1, eema1, theta1, y2, eema2, theta2, titre, legende):
    import sebform as sf
    import numpy as np
    import matplotlib.pyplot as plt
    plt.subplot(2, 1, 1)
    plt.semilogy(y1, sf.smooth(y1, eema1, 15, 1)*1000, 'o',
                 y2, sf.smooth(y2, eema2, 15, 1)*1000, '^')
    plt.ylabel('EEMA (microas)')
    plt.legend(legende)
    plt.grid(True, which='both')
    plt.xlim((-90, 90))
    plt.xticks(np.arange(-90, 120, 30))
    plt.title(titre)
    plt.subplot(2, 1, 2)
    plt.plot(y1, sf.smooth(y1, theta1, 15, 1), 'o', y2, sf.smooth(y2, theta2, 15, 1), '^')
    plt.xlabel('Declination (\xb0)')
    plt.ylabel('EERA (\xb0)')
    plt.grid(True, which='both')
    plt.xlim((-90, 90))
    plt.xticks(np.arange(-90, 120, 30))
    plt.ylim((0, 180))
    plt.yticks(np.arange(0, 210, 30))


def ploterrdel(no1, dx1, dy1, titre):
    import matplotlib.pyplot as plt
    plt.loglog(no1, dx1, 'o', no1, dy1, '^')
    plt.plot([1, 1e5], [1e2, 1e-3], 'r', lw=2)
    plt.xlabel('No Delays')
    plt.ylabel('Error (mas)')
    plt.legend(['RA cos Dec', 'Dec'])
    plt.grid(True, which='both')
    plt.title(titre)
    plt.xlim((1, 1e6))
    plt.ylim((1e-3, 1e3))


def plotskymap(x1, y1, titre):
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    x = np.remainder(x1+360, 360)
    x[x > 180] = x[x > 180]-360
    x = -x*(math.pi/180)
    y = y1*(math.pi/180)
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection='mollweide', facecolor='LightCyan')
    ciel = ax.scatter(x, y, marker='.')
# ax.set_xticklabels(['14h','16h','18h','20h','22h','0h','2h','4h','6h','8h','10h'])
    ax.set_xticklabels(['10h', '8h', '6h', '4h', '2h', '0h', '22h', '20h', '18h', '16h', '14h'])
    ax.grid(True, which='both')
    plt.title(titre)


def plotskycdt(x1, y1, e, lmin, lmax, cmapuser, titre, label):
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    x = np.remainder(x1+360, 360)
    x[x > 180] = x[x > 180]-360
    x = -x*(math.pi/180)
    y = y1*(math.pi/180)
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection='mollweide')
    fig.subplots_adjust(left=0.04, bottom=0, top=1, right=1)
    if (lmin == lmax):
        ciel = ax.scatter(x, y, c=e, marker='.', cmap=cmapuser)
    else:
        ciel = ax.scatter(x, y, c=e, marker='.', cmap=cmapuser, vmin=lmin, vmax=lmax)
# ax.scatter(x,y,facecolors='none',edgecolors='k')
# ax.set_xticklabels(['14h','16h','18h','20h','22h','0h','2h','4h','6h','8h','10h'])
    ax.set_xticklabels(['10h', '8h', '6h', '4h', '2h', '0h', '22h', '20h', '18h', '16h', '14h'])
    ax.grid(True, which='both')
    cbar = fig.colorbar(ciel, shrink=0.7)
    cbar.set_label(label, rotation=270, labelpad=20, y=0.5)
    plt.title(titre, y=1.04)


def plotskydef(x1, y1, x2, y2, titre):
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection='mollweide', facecolor='LightCyan')
    x = np.remainder(x1+360, 360)
    x[x > 180] = x[x > 180]-360
    x = -x*(math.pi/180)
    y = y1*(math.pi/180)
    ciel = ax.scatter(x, y, marker='o', color='orange')
    x = np.remainder(x2+360, 360)
    x[x > 180] = x[x > 180]-360
    x = -x*(math.pi/180)
    y = y2*(math.pi/180)
    ciel = ax.scatter(x, y, marker='.')
    x = np.remainder(x1+360, 360)
    x[x > 180] = x[x > 180]-360
    x = -x*(math.pi/180)
    y = y1*(math.pi/180)
    ciel = ax.scatter(x, y, marker='o', color='orange')
# ax.set_xticklabels(['14h','16h','18h','20h','22h','0h','2h','4h','6h','8h','10h'])
    ax.set_xticklabels(['10h', '8h', '6h', '4h', '2h', '0h', '22h', '20h', '18h', '16h', '14h'])
    ax.grid(True, which='both')
    plt.legend(['Defining'])
    plt.title(titre)


def plotskymag(x1, y1, e, lmin, lmax, cmapuser, titre, label):
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    x = np.remainder(x1+360, 360)
    x[x > 180] = x[x > 180]-360
    x = -x*(math.pi/180)
    y = y1*(math.pi/180)
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection='mollweide', facecolor='LightCyan')
    fig.subplots_adjust(left=0.04, bottom=0, top=1, right=1)
    if (lmin == lmax):
        ciel = ax.scatter(x, y, c=e, marker='.', cmap=cmapuser)
    else:
        ciel = ax.scatter(x, y, c=e, marker='.', cmap=cmapuser, vmin=lmin, vmax=lmax)
# ax.set_xticklabels(['14h','16h','18h','20h','22h','0h','2h','4h','6h','8h','10h'])
    ax.set_xticklabels(['10h', '8h', '6h', '4h', '2h', '0h', '22h', '20h', '18h', '16h', '14h'])
# ax.set_xticklabels([])
# ax.set_yticklabels([])
    ax.grid(True, which='both')
    cbar = fig.colorbar(ciel, shrink=0.7)
    cbar.set_label(label, rotation=270, labelpad=20, y=0.5)
    plt.title(titre, y=1.04)


def ploterrhist(dx, dy, titre):
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    plt.hist(dx, bins=2**(np.arange(1/10, 10, 0.2))/100, histtype='stepfilled', color='b')
    plt.hist(dy, bins=2**(np.arange(1/10, 10, 0.2))/100,
             histtype='stepfilled', color='r', alpha=0.5)
    plt.xlabel('Error (mas)')
    plt.ylabel('No. Sources')
    plt.legend(['RA cos Dec', 'Dec'])
    plt.grid(True, which='both')
    plt.title(titre)
    plt.xscale('log')
# plt.yscale('log',nonposy='clip')


def plotangsep(rad, titre):
    import numpy as np
    import matplotlib.pyplot as plt
    plt.hist(rad, bins=2**(np.arange(1/10, 16, 0.2))/100, edgecolor='grey')
    plt.xlabel('Angular Separation (mas)')
    plt.ylabel('No. Sources')
    plt.grid(True, which='both')
    plt.title(titre)
    plt.xscale('log')
    # plt.yscale('log',nonposy='clip')


def plotnorsep(sep, titre):
    import numpy as np
    import matplotlib.pyplot as plt
    plt.hist(sep, bins=2**(np.arange(0.1, 15, 0.4))/100, edgecolor='grey')
    plt.xlabel('Normalized Separation')
    plt.ylabel('No. Sources')
    plt.grid(True, which='both')
    plt.title(titre)
    plt.xscale('log')
    # plt.yscale('log',nonposy='clip')


def plotangnor(sep, rad, titre):
    import matplotlib.pyplot as plt
    plt.loglog(sep, rad, '.')
    plt.xlabel('Normalized Separation X')
    plt.ylabel('Angular Separation (mas)')
    plt.grid(True, which='both')
    plt.xlim(1e-3, 5e2)
    plt.ylim(1e-3, 5e2)
    plt.title(titre)


def plotposang(rpa, titre):
    import matplotlib.pyplot as plt
    import numpy as np
    posang = rpa
    plt.hist(posang, bins=12, edgecolor='grey')
    plt.xlabel('Angle ($^\circ$)')
    plt.ylabel('No. Sources')
    plt.grid(True, which='both', axis='y')
    plt.title(titre)
    plt.xticks(np.arange(0, 390, 30))
    plt.xlim(0, 360)


def plottransfo16(X, DX, paramnom, titre):
    import numpy as np
    import matplotlib.pyplot as plt
    paramtic = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    plt.bar(paramtic, X, yerr=DX)  # Plot transfo parameters as a bar plot
    plt.xticks(paramtic, paramnom, rotation='vertical')
    plt.ylabel('$\mu$as')
    plt.title(titre)
    plt.grid(True, which='both')


def plotcorr16(C, paramnom, titre):
    import numpy as np
    import matplotlib.pyplot as plt
    paramtic = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    plt.imshow(np.absolute(C), interpolation='none')  # Plot the correlation matrix
    plt.xticks(paramtic, paramnom, rotation='vertical')
    plt.yticks(paramtic, paramnom)
    plt.title(titre)
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.gca().xaxis.tick_bottom()


def normsep(x3, y3, dx3, dy3, cor3, x4, y4, dx4, dy4, cor4):
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    m2d = 1/3600000  # mas to degree
    x34 = (x3-x4)*np.cos(y4*math.pi/180)/m2d
    y34 = (y3-y4)/m2d
    dx34 = np.sqrt(dx3**2+dx4**2)
    dy34 = np.sqrt(dy3**2+dy4**2)
    rad = np.sqrt(x34**2+y34**2)
    rpa = np.arctan2(x34, y34)
    drad = np.sqrt(x34**2*dx34**2+y34**2*dy34**2)/rad
    drpa = np.sqrt(y34**2*dx34**2+x34**2*dy34**2)/rad**2
    rpa = rpa*(180/math.pi)
    rpa[(rpa < 0)] = rpa[(rpa < 0)]+360
    rpa[(rpa > 360)] = rpa[(rpa > 360)]-360
    drpa = drpa*(180/math.pi)
    drpa[(drpa < 0)] = drpa[(drpa < 0)]+360
    drpa[(drpa > 360)] = drpa[(drpa > 360)]-360
    Xx = x34/dx34
    Xy = y34/dy34
    # Separations normalisees
    rss = rad/drad
    tmp = (dx3*dy3*cor3+dx4*dy4*cor4)/np.sqrt((dx3**2+dx4**2)*(dy3**2+dy4**2))
    sep = np.sqrt(np.absolute((Xx**2+Xy**2-2*Xx*Xy*tmp)/(1-tmp**2)))
    return x34, y34, dx34, dy34, rad, drad, rpa, drpa, rss, sep
