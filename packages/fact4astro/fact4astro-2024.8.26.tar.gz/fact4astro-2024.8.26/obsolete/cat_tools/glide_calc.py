#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: glide_calc.py
"""
Created on Mon Mar 26 16:21:26 2018

@author: Neo(liuniu@smail.nju.edu.cn)

Some functions related to glide component calculation.

History
N.Liu, 20 Mar 2018:

"""

from astropy import units as u
from astropy.coordinates import SkyCoord
import matplotlib.pyplot as plt
import numpy as np
from numpy import cos, sin, pi
# My module
from .vsh_deg1_cor import vsh_deg01_fitting

__all__ = ["glide_gen", "glide_calc", "GA_glide_decomposed",
           "glide_field_gen"]


# -----------------------------  FUNCTIONS -----------------------------
def glide_gen(g=5.8, RAdeg=266.416667, DCdeg=-28.992222, err=None):
    '''Given apex and amplitude, calculate the glide vector.

    NOTE: inputs RAdeg/DCdeg should be given in degree.

    Parameters
    ----------
    g : float
        amplitude of glide vector, default value is 1.0.
    RAdeg/DCdeg : float
        direction of apex expressed in right ascension and declination
        given in degree. For Galactic center, they could be set as
        267.0/-29.0.
    err : array of float
        uncertainties of g, RAdeg and DCdeg given in rad/deg/deg,
        default value is None.

    Returns
    ----------
    [g1, g2, g3] : array of float
        glide vector
    errn : array of float
        vector of glide formal uncertainties
    '''

    # Degree -> radian
    RArad = np.deg2rad(RAdeg)
    DCrad = np.deg2rad(DCdeg)

    g1 = g * cos(RArad) * cos(DCrad)
    g2 = g * sin(RArad) * cos(DCrad)
    g3 = g * sin(DCrad)

    gvec = np.array([g1, g2, g3])

    if err is None:
        return gvec
    else:
        # Calculate the uncertainties.
        M = np.array([
            [cos(RArad) * cos(DCrad),
             -g * sin(RArad) * cos(DCrad),
             -g * cos(RArad) * sin(DCrad)],
            [sin(RArad) * cos(DCrad),
             g * cos(RArad) * cos(DCrad),
             -g * sin(RArad) * sin(DCrad)],
            [sin(DCrad),
             0,
             g * cos(DCrad)]])

        # degree -> radian
        err[1] = np.deg2rad(err[1])
        err[2] = np.deg2rad(err[2])

        errn = np.sqrt(np.dot(M**2, err**2))

        return gvec, errn


def glide_calc(gv, err_gv=None):
    '''Calculate the apex and amplitude for a given glide vector.

    Parameters
    ----------
    gv : array of float
        glide vector
    err_gv : array of float
        formal error of glide vector, default value is None

    Returns
    ----------
    g/err_g : amplitude and its uncertainty
    RAdeg/err_RA : right ascension and its uncertainty in degree
    DCdeg/err_DC : declination and its uncertainty in degree
    '''

    # Calculate the parameters.
    # Amplitude
    A = np.sqrt(np.sum(gv ** 2))

    # Right ascension
    RArad = np.arctan2(gv[1], gv[0])
    # arctan2 function result is always between -pi and pi.
    # However, RA should be between 0 and 2*pi.
    if RArad < 0:
        RArad += 2 * np.pi

    # Declination
    DCrad = np.arctan2(gv[2], np.sqrt(gv[0]**2 + gv[1]**2))

    # radian -> degree
    RAdeg = np.rad2deg(RArad)
    DCdeg = np.rad2deg(DCrad)

    if err_gv is None:
        return A, RAdeg, DCdeg
    else:
        # # Method 1)
        # M = np.array([
        #     [cos(RArad) * cos(DCrad),
        #      A * sin(RArad) * cos(DCrad),
        #      A * cos(RArad) * sin(DCrad)],
        #     [sin(RArad) * cos(DCrad),
        #      A * cos(RArad) * cos(DCrad),
        #      A * sin(RArad) * sin(DCrad)],
        #     [sin(DCrad),
        #      0,
        #      A * cos(DCrad)]])
        # M_1 = np.linalg.inv(M**2)
        # errn = np.sqrt(np.dot(M_1, err_gv**2))
        # errA, errRAr, errDCr = errn
        # However, the obtained error are always meaningless (minus
        # value inner the square operation).

        # #) Method 2)
        par_g = gv / A
        gxy2 = gv[0]**2 + gv[1]**2
        gxy = np.sqrt(gxy2)
        par_RA = np.array([-gv[1], gv[0], 0]) / gxy2
        par_DC = np.array([-gv[0] * gv[2],
                           -gv[1] * gv[2],
                           gxy2]) / A**2 / gxy
        errA = np.sqrt(np.dot(par_g**2, err_gv**2))
        errRAr = np.sqrt(np.dot(par_RA**2, err_gv**2))
        errDCr = np.sqrt(np.dot(par_DC**2, err_gv**2))

        # --------------- 20 Mar 2018 ----------------------------------
        # errA = np.sqrt(np.dot(err_gv, err_gv))
        # --------------- 20 Mar 2018 ----------------------------------

        # radian -> degree
        errRA = np.rad2deg(errRAr)
        errDC = np.rad2deg(errDCr)

        return A, RAdeg, DCdeg, errA, errRA, errDC


def GA_glide_decomposed(gv, err_gv):
    """Given a glide vector, get the GA component and non-GA component.


    'G' stands for amplitude while 'g' for vector

    Parameters
    ----------
    gv : array of float
        glide vector
    err_gv : array of float
        formal error of glide vector

    Returns
    ----------
    G_GA/err_GA : amplitude and its uncertainty of GA component
    g_NonGA : non-GA glide component
    """

    GA_hat = glide_gen(1.0, 266.4, -28.9)

    # GA component
    G_GA = np.dot(gv, GA_hat)
    errG_GA = np.dot(err_gv, GA_hat)

    # non-GA component
    g_NonGA = gv - G_GA * GA_hat
    err_NonGA = err_gv - errG_GA * GA_hat
    [G_NonGA, RA_NonGA, DC_NonGA,
     errG_NonGA, errRA_NonGA, errDC_NonGA] = glide_calc(g_NonGA, err_NonGA)

    return [G_GA, errG_GA, G_NonGA, RA_NonGA, DC_NonGA,
            errG_NonGA, errRA_NonGA, errDC_NonGA]


def glide_field_gen(ra=None, dec=None, g=None):
    """Generate a dipolar field.

    Parameters
    ----------
    ra/dec: array-like
        coordinates in degrees
    g: 3-D array
        glide vector

    Return
    ------
    dra/ddec: array-like
        dipolar component along right ascension and declination directions

    """

    if ra is None:
        ra_in_rad = np.linspace(0, 2 * pi, 100)
    else:
        ra_in_rad = np.deg2rad(ra)

    if dec is None:
        dec_in_rad = np.linspace(-pi, pi, 100)
    else:
        dec_in_rad = np.deg2rad(dec)

    if g is None:
        g = glide_gen()

    # Calculate the glide field
    g1, g2, g3 = g
    dra = [- g1 * sin(ra_in_rad) + g2 * cos(ra_in_rad)][0]
    ddec = [- g1 * cos(ra_in_rad) * sin(dec_in_rad) -
            g2 * sin(ra_in_rad) * sin(dec_in_rad) + g3 * cos(dec_in_rad)][0]

    return dra, ddec


def glide_plot(gv, output=None, fig_title=None):
    """Plot fot glide field.

    Parameters
    ----------
    gv : array of float
        glide vector
    output : string
        Full name of the output file
    fig_title : string
        Title of the figure

    Returns
    ----------
    None
    """

    ra = np.linspace(0, 360, 20) * u.deg
    dec = (np.linspace(-90, 90, 20)) * u.deg
    c = SkyCoord(ra=ra, dec=dec, frame='icrs')

    ra_rad = c.ra.wrap_at(180 * u.deg).radian
    dec_rad = c.dec.radian

    # Glide field
    X, Y = np.meshgrid(ra_rad, dec_rad)
    U, V = glide_field_gen(gv, X, Y)

    # GC position
    c1_gal = SkyCoord(l=0 * u.deg, b=0 * u.deg, frame="galactic")
    c1_icrs = c1_gal.icrs
    ra_gc_rad = c1_icrs.ra.wrap_at(180 * u.deg).radian
    dec_gc_rad = c1_icrs.dec.radian

    # Anti-GC position
    c2_gal = SkyCoord(l=180 * u.deg, b=0 * u.deg, frame="galactic")
    c2_icrs = c2_gal.icrs
    ra_agc_rad = c2_icrs.ra.wrap_at(180 * u.deg).radian
    dec_agc_rad = c2_icrs.dec.radian

    # Plot
    plt.figure(figsize=(8, 4.2))
    plt.subplot(111, projection="aitoff")

    Q = plt.quiver(X, Y, U, V, units='xy', scale=100.0)
    qk = plt.quiverkey(Q, 0.90, 0.90, 50, r'$50 \mu as$', labelpos='E',
                       coordinates='figure')

    # Show the position of GC and anti-GC
    plt.plot(ra_gc_rad, dec_gc_rad, 'r+')
    plt.plot(ra_agc_rad, dec_agc_rad, 'r+')
    plt.text(ra_gc_rad, dec_gc_rad, "GC", color="r")
    # plt.text(ra_gc_rad, dec_gc_rad, "Anti-GC")

    if not fig_title is None:
        plt.title(fig_title, y=1.08)

    plt.grid(True)
    plt.subplots_adjust(top=0.95, bottom=0.05)

    if output is None:
        plt.show()
    else:
        plt.savefig(output)


def rotation_from_ga(cat):
    """Rotation of the celestial frame induced by the Galactic aberration (GA).

    Parameter
    --------
    cat: astropy.table.Table object
        contain at least "ra" and "dec" column

    Returns
    --------
    rot: np.array of (3,)
        rotational angles around three axis
    sig: np.array of (3,)
        formal error of the rotation
    cov: np.array of (3,3)
        covariance matrix
    """

    radeg = np.array(cat["ra"])
    decdeg = np.array(cat["dec"])

    rarad = np.deg2rad(radeg)
    decrad = np.deg2rad(decdeg)

    # GA constant (Liu et al. 2012)
    raGC = 266.4
    decGC = -28.4
    # ICRF3 adopted value=
    gmod = 5.8

    # Generate a dipolar field
    gvec = glide_gen(gmod, raGC, decGC)
    pmra, pmdec = glide_field_gen(radeg, decdeg, gvec)

    # Fit the rotation
    rot, sig, cov, _, _, _ = vsh_deg01_fitting(pmra, pmdec, rarad, decrad,
                                               elim_flag=None,
                                               fit_type="rotation")

    return rot, sig, cov


def test_code(flag):
    '''Used for verified the code.
    '''

    if flag == 1:
        # print(glide_calc(np.array([1.2, 2.4, 7.5]),
        # np.array([0.6, 0.8, 1.0])))

        # Verify the result of Table 1 in Titov et al.(2011) (A&A 529, A91)
        print('\nTo verify the result of Table 1 in Titov et al.(2011):')
        # Result in the paper
        dip = np.array([[-0.7, -5.9, -2.2],
                        [-1.9, -7.1, -3.5],
                        [-1.6, -6.0, -2.9],
                        [-3.4, -6.2, -3.8],
                        [+4.2, -4.6, +1.4]])
        derr = np.array([[0.8, 0.9, 1.0],
                         [1.0, 1.1, 1.2],
                         [0.9, 1.0, 1.1],
                         [1.0, 1.2, 1.2],
                         [1.3, 1.3, 1.7]])
        par = np.array([[6.4, 263, -20],
                        [8.1, 255, -25],
                        [6.9, 255, -25],
                        [8.0, 241, -28],
                        [6.4, 312, 13]])
        perr = np.array([[1.5, 11, 12],
                         [1.9, 11, 11],
                         [1.7, 11, 11],
                         [2.0, 12, 12],
                         [2.5, 16, 21]])
        for (dipi, derri, pari, perri) in zip(dip, derr, par, perr):
            print('Result in paper: ', pari, perri)
            print('Result of my calculation:', glide_calc(dipi, derri))
            print('For g:', np.sqrt(np.dot(derri, derri)))

        # Verify the result of Table 1 in Liu et al.(2012) (A&A 548, A50)
        print('\nTo verify the result of Table 1 in Liu et al.(2012):')
        # Result in the paper
        dip = np.array([[+1.07, -0.20, +0.18],
                        [+0.22, -0.03, +0.04],
                        [+0.01, -0.14, +0.28],
                        [+0.89, -0.08, +0.04]])
        derr = np.array([[0.08, 0.08, 0.09],
                         [0.05, 0.05, 0.05],
                         [0.07, 0.07, 0.07],
                         [0.02, 0.02, 0.02]])
        par = np.array([[1.10],
                        [0.22],
                        [0.31],
                        [0.89]])
        perr = np.array([[0.14],
                         [0.09],
                         [0.12],
                         [0.03]])
        for (dipi, derri, pari, perri) in zip(dip, derr, par, perr):
            print('Result in paper: ', pari, perri)
            print('Result of my calculation:', glide_calc(dipi, derri))
            print('For g:', np.sqrt(np.dot(derri, derri)))

        # Verify the result of Table 1 in Titov et al.(2013) (A&A 559, A95)
        print('\nTo verify the result of Table 1 in Titov et al.(2013):')
        # Result in the paper
        dip = np.array([[-0.4, -5.7, -2.8],
                        [+0.7, -6.2, -3.3],
                        [+0.7, -6.2, -3.3]])
        derr = np.array([[0.7, 0.8, 0.9],
                         [0.8, 0.9, 1.0],
                         [0.9, 1.0, 1.0]])
        par = np.array([[6.4, 266, -26],
                        [7.1, 277, -28],
                        [7.1, 277, -28]])
        perr = np.array([[1.1, 7, 7],
                         [1.3, 7, 7],
                         [1.4, 9, 8]])
        for (dipi, derri, pari, perri) in zip(dip, derr, par, perr):
            print('Result in paper: ', pari, perri)
            print('Result of my calculation:', glide_calc(dipi, derri))
            print('For g:', np.sqrt(np.dot(derri, derri)))

        # Verify the result of Table 1 in Titov et al.(2018) (A&A 610, A36)
        print('\nTo verify the result of Table 1 in Titov et al.(2018):')
        # Result in the paper
        dip = np.array([[-0.7, -5.9, -2.2],
                        [-2.6, -5.1, -1.1],
                        [-0.4, -5.7, -2.8],
                        [-0.3, -5.4, -1.1],
                        [+0.2, -3.3, -4.9]])
        derr = np.array([[0.8, 0.9, 1.0],
                         [0.3, 0.3, 0.4],
                         [0.7, 0.8, 0.9],
                         [0.3, 0.3, 0.5],
                         [0.8, 0.8, 1.0]])
        par = np.array([[6.4, 263, -20],
                        [5.8, 243, -11],
                        [6.4, 266, -26],
                        [5.6, 267, -11],
                        [5.9, 273, -56]])
        perr = np.array([[1.5, 11, 12],
                         [0.4, 4, 4],
                         [1.1, 7, 7],
                         [0.4, 3, 3],
                         [1.0, 13, 9]])
        for (dipi, derri, pari, perri) in zip(dip, derr, par, perr):
            print('Result in paper: ', pari, perri)
            print('Result of my calculation:', glide_calc(dipi, derri))
            print('For g:', np.sqrt(np.dot(derri, derri)))

        # Verify the result in David Mayer(draft)
        print('\nTo verify the result of Table 1 in draft of David Mayer:')
        # Result in the paper
        dip = np.array([[+2., +26., +32.],
                        [+5., +25., +44.],
                        [+1., +2., +21.],
                        [+3., -8., +27.],
                        [-2., +5., +6.],
                        [-3., -8., +19.]])
        derr = np.array([[15., 16., 14.],
                         [15., 16., 14.],
                         [15., 16., 14.],
                         [15., 16., 14.],
                         [15., 16., 13.],
                         [15., 16., 14.]])
        par = np.array([[42, 85, +51],
                        [51, 78, +60],
                        [21, 77, +83],
                        [29, 291, +73],
                        [8, 108, +53],
                        [21, 250, +65]])
        perr = np.array([[15, 33, 19],
                         [15, 35, 16],
                         [14, 350, 41],
                         [14, 102, 32],
                         [14, 175, 107],
                         [13, 104, 43]])
        for (dipi, derri, pari, perri) in zip(dip, derr, par, perr):
            print('Result in paper: ', pari, perri)
            print('Result of my calculation:', glide_calc(dipi, derri))
            print('For g:', np.sqrt(np.dot(derri, derri)))

    elif flag == 2:
        g, RA, DC = 5.4, 256.0, -30
        err_g, err_RA, err_DC = 0.6, 4.0, 5.0
        print('Input: ', g, RA, DC, err_g, err_RA, err_DC)
        print('Radian for angles', np.deg2rad(err_RA), np.deg2rad(err_DC))
        gv, err_gv = glide_gen(g, RA, DC,
                               np.array([err_g, err_RA, err_DC]))
        g1, RA1, DC1, err_g1, err_RA1, err_DC1 = glide_calc(gv, err_gv)
        print('Output: ', g1, RA1, DC1, err_g1, err_RA1, err_DC1)


# --------------------------------- MAIN --------------------------------
if __name__ == '__main__':
    test_code(1)
# --------------------------------- END --------------------------------
