#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: galactic_aberration.py
"""
Created on Mon 26 Aug 2024 04:53:46 PM CST

@author: Neo(niu.liu@nju.edu.cn)
"""


import numpy as np

from .analysis_tools import calculate_normalized_proper_motion

__all__ = ["calculate_glide_vector", "generate_glide_field"]


def calculate_glide_vector(g=5.8, RAdeg=266.416667, DCdeg=-28.992222, err=None):
    """
    Given apex and amplitude, calculate the glide vector.

    NOTE: inputs RAdeg/DCdeg should be given in degrees.

    Parameters
    ----------
    g : float, optional
        Amplitude of the glide vector, default value is 5.8.
    RAdeg : float, optional
        Right ascension of the apex in degrees, default is 266.416667 (Galactic center).
    DCdeg : float, optional
        Declination of the apex in degrees, default is -28.992222 (Galactic center).
    err : array of float, optional
        Uncertainties of g, RAdeg, and DCdeg, given in units of rad/deg/deg.

    Returns
    -------
    gvec : array of float
        Glide vector components [g1, g2, g3].
    errn : array of float, optional
        Formal uncertainties of the glide vector components, returned only if `err` is provided.
    """

    # Convert degrees to radians
    RArad = np.deg2rad(RAdeg)
    DCrad = np.deg2rad(DCdeg)

    # Calculate the glide vector components
    g1 = g * np.cos(RArad) * np.cos(DCrad)
    g2 = g * np.sin(RArad) * np.cos(DCrad)
    g3 = g * np.sin(DCrad)

    gvec = np.array([g1, g2, g3])

    if err is None:
        return gvec
    else:
        # Calculate the uncertainties in the glide vector components
        M = np.array([
            [np.cos(RArad) * np.cos(DCrad),
             -g * np.sin(RArad) * np.cos(DCrad),
             -g * np.cos(RArad) * np.sin(DCrad)],
            [np.sin(RArad) * np.cos(DCrad),
             g * np.cos(RArad) * np.cos(DCrad),
             -g * np.sin(RArad) * np.sin(DCrad)],
            [np.sin(DCrad),
             0,
             g * np.cos(DCrad)]])

        # Convert errors from degrees to radians where necessary
        err[1] = np.deg2rad(err[1])
        err[2] = np.deg2rad(err[2])

        # Calculate the uncertainties in the glide vector
        errn = np.sqrt(np.dot(M**2, err**2))

        return gvec, errn


def generate_glide_field(gv, ra, dec):
    """
    Generate a field at (ra, dec) for the glide scale.

    Parameters
    ----------
    gv : array of float
        Glide vector [g1, g2, g3].
    ra : array of float
        Right ascension in radians.
    dec : array of float
        Declination in radians.

    Returns
    -------
    g_dra : array of float
        RA offset induced by glide.
    g_ddec : array of float
        Dec. offset induced by glide.
    """
    g1, g2, g3 = gv
    g_dra = -g1 * np.sin(ra) + g2 * np.cos(ra)
    g_ddec = -g1 * np.cos(ra) * np.sin(dec) - g2 * \
        np.sin(ra) * np.sin(dec) + g3 * np.cos(dec)

    return g_dra, g_ddec


def calculate_glide_parameters(gv, err_gv=None):
    """
    Calculate the apex and amplitude for a given glide vector.

    Parameters
    ----------
    gv : array of float
        Glide vector components [g1, g2, g3].
    err_gv : array of float, optional
        Formal errors of glide vector components, default is None.

    Returns
    -------
    A : float
        Amplitude of the glide vector.
    RAdeg : float
        Right ascension of the apex in degrees.
    DCdeg : float
        Declination of the apex in degrees.
    errA : float, optional
        Uncertainty in the amplitude, returned only if `err_gv` is provided.
    errRA : float, optional
        Uncertainty in the right ascension, returned only if `err_gv` is provided.
    errDC : float, optional
        Uncertainty in the declination, returned only if `err_gv` is provided.
    """

    # Calculate the amplitude (magnitude) of the glide vector
    A = np.sqrt(np.sum(gv ** 2))

    # Calculate the right ascension (RA) in radians
    RArad = np.arctan2(gv[1], gv[0])
    if RArad < 0:
        RArad += 2 * np.pi  # Ensure RA is between 0 and 2*pi

    # Calculate the declination (Dec) in radians
    DCrad = np.arctan2(gv[2], np.sqrt(gv[0]**2 + gv[1]**2))

    # Convert RA and Dec from radians to degrees
    RAdeg = np.rad2deg(RArad)
    DCdeg = np.rad2deg(DCrad)

    if err_gv is None:
        return A, RAdeg, DCdeg
    else:
        # Calculate partial derivatives for error propagation
        par_g = gv / A
        gxy2 = gv[0]**2 + gv[1]**2
        gxy = np.sqrt(gxy2)
        par_RA = np.array([-gv[1], gv[0], 0]) / gxy2
        par_DC = np.array([-gv[0] * gv[2],
                           -gv[1] * gv[2],
                           gxy2]) / A**2 / gxy

        # Calculate uncertainties using error propagation
        errA = np.sqrt(np.dot(par_g**2, err_gv**2))
        errRAr = np.sqrt(np.dot(par_RA**2, err_gv**2))
        errDCr = np.sqrt(np.dot(par_DC**2, err_gv**2))

        # Convert RA and Dec uncertainties from radians to degrees
        errRA = np.rad2deg(errRAr)
        errDC = np.rad2deg(errDCr)

        return A, RAdeg, DCdeg, errA, errRA, errDC


def decompose_glide_vector(gv, err_gv):
    """
    Decompose a glide vector into its Galactic Aberration (GA) component and non-GA component.

    'G' stands for amplitude, while 'g' stands for vector.

    Parameters
    ----------
    gv : array of float
        Glide vector components [g1, g2, g3].
    err_gv : array of float
        Formal errors of the glide vector components.

    Returns
    -------
    G_GA : float
        Amplitude of the GA component.
    errG_GA : float
        Uncertainty in the amplitude of the GA component.
    G_NonGA : float
        Amplitude of the non-GA component.
    RA_NonGA : float
        Right ascension of the non-GA component in degrees.
    DC_NonGA : float
        Declination of the non-GA component in degrees.
    errG_NonGA : float
        Uncertainty in the amplitude of the non-GA component.
    errRA_NonGA : float
        Uncertainty in the right ascension of the non-GA component in degrees.
    errDC_NonGA : float
        Uncertainty in the declination of the non-GA component in degrees.
    """

    # Calculate the unit vector for the GA direction
    GA_hat = calculate_glide_vector(1.0, 266.4, -28.9)

    # GA component
    G_GA = np.dot(gv, GA_hat)
    errG_GA = np.dot(err_gv, GA_hat)

    # Non-GA component
    g_NonGA = gv - G_GA * GA_hat
    err_NonGA = err_gv - errG_GA * GA_hat

    # Calculate the amplitude and direction of the non-GA component
    G_NonGA, RA_NonGA, DC_NonGA, errG_NonGA, errRA_NonGA, errDC_NonGA = calculate_glide_parameters(
        g_NonGA, err_NonGA)

    return G_GA, errG_GA, G_NonGA, RA_NonGA, DC_NonGA, errG_NonGA, errRA_NonGA, errDC_NonGA


def calculate_rotation_from_ga(cat):
    """
    Calculate the rotation of the celestial frame induced by Galactic aberration (GA).

    Parameters
    ----------
    cat : astropy.table.Table
        The catalog of celestial objects, which must contain at least "ra" and "dec" columns.

    Returns
    -------
    rot : np.array of shape (3,)
        Rotational angles around the three axes in microarcseconds.
    sig : np.array of shape (3,)
        Formal errors of the rotation angles in microarcseconds.
    cov : np.array of shape (3, 3)
        Covariance matrix of the rotational angles.
    """

    # Check if the required columns are present in the catalog
    if "ra" not in cat.colnames or "dec" not in cat.colnames:
        raise ValueError("Input catalog must contain 'ra' and 'dec' columns.")

    # Extract RA and Dec from the catalog
    radeg = np.array(cat["ra"])
    decdeg = np.array(cat["dec"])

    rarad = np.deg2rad(radeg)
    decrad = np.deg2rad(decdeg)

    # Galactic Aberration constants (Liu et al. 2012)
    raGC = 266.4  # Right ascension of the Galactic center in degrees
    decGC = -28.4  # Declination of the Galactic center in degrees
    gmod = 5.8  # Magnitude of the GA vector in microarcseconds

    # Generate the glide vector and field
    gvec = calculate_glide_vector(gmod, raGC, decGC)
    pmra, pmdec = generate_glide_field(gvec, rarad, decrad)

    # Fit the rotation to the dipolar field
    rot, sig, cov, _, _, _ = vsh_deg01_fitting(pmra, pmdec, rarad, decrad,
                                               elim_flag=None,
                                               fit_type="rotation")

    return rot, sig, cov


def correct_gaia_pm_for_ga(gaia_sou, gv=None, table="edr3"):
    """
    Correct the Galactic aberration effect in Gaia EDR3 proper motions.

    This function is particularly suited for AGNs and other objects with similar characteristics.

    Parameters
    ----------
    gaia_sou : astropy.table.Table
        AGN table in Gaia, also applicable to other tables with similar column names to Gaia.
    gv : array-like, optional
        GA-induced glide vector. If None, the default vector from the Gaia EDR3 paper is used.
    table : str, optional
        Specifies the Gaia data release. Default is "edr3".

    Returns
    -------
    gaia_sou : astropy.table.Table
        The input table with an added column "nor_pm_cor" for the normalized proper motion correction.
    """

    if gv is None:
        if table == "edr3":
            # GA-induced glide vector, from Gaia EDR3 paper, Table 2
            # (gx, gy, gz) = (-0.07, -4.30, -2.64) +/- (0.41, 0.35, 0.36) µas/yr
            gv = np.array([-0.07, -4.30, -2.64]) * 1.e-3  # Convert to mas/yr

    # Generate the GA correction field
    pmra0, pmdec0 = generate_glide_field(gv, np.deg2rad(
        gaia_sou["ra"]), np.deg2rad(gaia_sou["dec"]))

    # Calculate the corrected normalized proper motion
    nor_pm_cor = calculate_normalized_proper_motion(gaia_sou["pmra"] - pmra0, gaia_sou["pmra_err"],
                                                    gaia_sou["pmdec"] -
                                                    pmdec0, gaia_sou["pmdec_err"],
                                                    gaia_sou["pmra_pmdec_corr"])

    # Add the corrected proper motion to the table
    gaia_sou.add_column(nor_pm_cor, name="nor_pm_cor")

    return gaia_sou


# --------------------------------- MAIN --------------------------------
if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
