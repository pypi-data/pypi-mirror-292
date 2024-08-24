def vshhammer(xm, ym, V, titre, nomfig):
    import matplotlib.pyplot as plt
    # from mpl_toolkits.basemap import Basemap
    import numpy as np
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection='mollweide', facecolor='LightCyan')
    ax.quiver(xm, ym, V[0:len(V):2]*np.pi/180, V[1:len(V):2]*np.pi /
              180, angles='xy', scale=0.1, width=0.001, headwidth=10)
    ax.set_xticklabels(['10h', '8h', '6h', '4h', '2h', '0h',
                        '22h', '20h', '18h', '16h', '14h'])
    ax.grid(True, which='both')
    plt.title(titre)
    # plt.show()
    plt.savefig(nomfig)
    plt.close()


def vshlm2k(lmax, l0, m0):
    import numpy as np
    k = 1
    for l in range(1, lmax+1):
        m = 0
        k = k+1
        if l == l0 and m == m0:
            k0 = k
        k = k+1
        if l == l0 and m == m0:
            k0 = k
        for m in range(1, l+1):
            k = k+1
            if l == l0 and m == m0:
                k0 = k
            k = k+1
            if l == l0 and m == m0:
                k0 = k
            k = k+1
            if l == l0 and m == m0:
                k0 = k
            k = k+1
            if l == l0 and m == m0:
                k0 = k
    return(k0)


def vshplm(lmax, x):
    import numpy as np
    P = np.zeros((lmax+1, lmax+1))
    D = np.zeros((lmax+1, lmax+1))
    if lmax == 0:
        P = 1
        D = 0
    else:
        P[0, 0] = 1
        for m in range(0, lmax):
            P[m+1, m+1] = (2*m+1)*np.sqrt(1-x**2)*P[m, m]
        for m in range(0, lmax):
            P[m+1, m] = (2*m+1)*x*P[m, m]
        for m in range(0, lmax-1):
            for l in range(m+2, lmax+1):
                P[l, m] = (1/(l-m))*((2*l-1)*x*P[l-1, m]-(l-1+m)*P[l-2, m])
        for l in range(1, lmax+1):
            for m in range(0, l+1):
                D[l, m] = -(l*x/(1-x**2))*P[l, m]+((l+m)/(1-x**2))*P[l-1, m]
    return(P, D)


def vshmatrix(lmax, alpha, delta):
    import math
    import numpy as np
    N = len(alpha)
    A = np.zeros((2*N, 2*lmax*(lmax+2)))
    for i in range(0, N):
        P, D = vshplm(lmax, np.sin(delta[i]))
        k = 0
        for l in range(1, lmax+1):
            m = 0
            coef = np.sqrt((2*l+1)/(4*np.pi))
            PL0 = P[l, 0]
            DPL0DDELTA = D[l, 0]
            YL0 = coef*PL0
            DYL0DDELTA = coef*DPL0DDELTA
            DYL0DALPHA = 0
            # T10 = (1/np.sqrt(l*(l+1)))*DYL0DDELTA
            # Missing transformation coefficient from (Plm, dPlm) -> (Alm, Blm)
            T10 = (1/np.sqrt(l*(l+1)))*DYL0DDELTA*np.cos(delta[i])
            S10 = -T10
            A[2*i, k] = T10
            A[2*i+1, k+1] = S10
            k = k+2
            for m in range(1, l+1):
                coef = (-1)**m*np.sqrt((2*l+1)/(4*np.pi) *
                                       math.factorial(l-m)/math.factorial(l+m))
                PLM = P[l, m]
                DPLMDDELTA = D[l, m]
                YLM = coef*PLM * \
                    np.complex(np.cos(m*alpha[i]), np.sin(m*alpha[i]))
                DYLMDDELTA = coef*DPLMDDELTA * \
                    np.complex(np.cos(m*alpha[i]), np.sin(m*alpha[i]))
                DYLMDALPHA = np.complex(0, 1)*m*YLM
                # T1 = (1/np.sqrt(l*(l+1)))*DYLMDDELTA
                # T2 = -(1/np.sqrt(l*(l+1)))*DYLMDALPHA/np.cos(delta[i])
                # Missing transformation coefficient from (Plm, dPlm) -> (Alm, Blm)
                T1 = (1/np.sqrt(l*(l+1)))*DYLMDDELTA*np.cos(delta[i])
                T2 = -(1/np.sqrt(l*(l+1)))*DYLMDALPHA*m/np.cos(delta[i])
                S1 = -T2
                S2 = T1
                # mes parametres sont dans l'ordre tR, sR, tI, sI
                A[2*i, k] = 2*np.real(T1)
                A[2*i, k+1] = 2*np.real(S1)
                A[2*i, k+2] = -2*np.imag(T1)
                A[2*i, k+3] = 2*np.imag(S1)
                A[2*i+1, k] = 2*np.real(T2)
                A[2*i+1, k+1] = 2*np.real(S2)
                A[2*i+1, k+2] = -2*np.imag(T2)
                A[2*i+1, k+3] = 2*np.imag(S2)
                k = k+4
    return(A)
