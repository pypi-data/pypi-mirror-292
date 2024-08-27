#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: analysis_tools.py
"""
Created on Mon 26 Aug 2024 10:55:12 AM CST

@author: Neo(niu.liu@nju.edu.cn)
"""

import numpy as np
from scipy.special import gammaincc
from functools import reduce
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import Column, join

from .error_ellipse import calculate_error_ellipses
from .catalog_operations import determine_coordinate_system, extract_position_columns, determine_pm_coordinate_system, extract_pm_columns


def compute_weighted_mean(x, err=None):
    """Compute the weighted mean value."""
    if err is None:
        mean = np.mean(x)
    else:
        p = 1. / err
        mean = np.dot(x * p, p) / np.dot(p, p)
    return mean


def compute_wrms_adjusted(x, err=None):
    """Compute the (weighted) WRMS of x series after removing the bias."""
    if err is None:
        mean = np.mean(x)
        xn = x - mean
        wrms = np.sqrt(np.dot(xn, xn) / (x.size - 1))
    else:
        p = 1. / err
        mean = np.dot(x, p**2) / np.dot(p, p)
        xn = (x - mean) * p
        wrms = np.sqrt(np.dot(xn, xn) / np.dot(p, p))
    return wrms


def compute_wrms(x, err=None):
    """Compute the (weighted) WRMS of x series."""
    if err is None:
        wrms = np.sqrt(np.dot(x, x) / (x.size - 1))
    else:
        p = 1. / err
        wrms = np.sqrt(np.dot(x * p, x * p) / np.dot(p, p))
    return wrms


def compute_chi_squared(x, err, reduced=False, deg=0):
    """Compute the (reduced) Chi-squared."""
    wx = x / err
    chi2 = np.dot(wx, wx)
    if reduced:
        if deg:
            return chi2 / (x.size - deg)
        else:
            raise ValueError("The degree of freedom cannot be 0!")
    else:
        return chi2


def compute_chi_squared_2d(x, errx, y, erry, covxy=None, reduced=False, num_fdm=0):
    """Compute the 2-Dimensional (reduced) Chi-squared."""
    Qxy = np.zeros_like(x)
    if covxy is None:
        covxy = np.zeros_like(x)
    for i, (xi, errxi, yi, erryi, covxyi) in enumerate(zip(x, errx, y, erry, covxy)):
        wgt = np.linalg.inv(np.array([[errxi**2, covxyi],
                                      [covxyi, erryi**2]]))
        Xmat = np.array([xi, yi])
        Qxy[i] = reduce(np.dot, (Xmat, wgt, Xmat))
    if num_fdm == 0:
        num_fdm = 2 * x.size - 1
    if reduced:
        return np.sum(Qxy) / num_fdm
    else:
        return np.sum(Qxy)


def compute_goodness_of_fit(fdm_num, chi2):
    """Compute the goodness-of-fit."""
    Q = gammaincc(fdm_num / 2., chi2 / 2.)
    return Q


def smooth_by_dec(dec, sig_pos_max, interv_size=50):
    """Calculate the smoothed standard error as a function of declination.

    Parameters
    ----------
    dec : array_like of float
        Declination in degrees.
    sig_pos_max : array_like of float
        Positional uncertainty (ellipse major axis) in mas.
    interv_size : int, optional
        Number of sources in a subset, default is 50.

    Returns
    ----------
    med_dec : array of float
        Median declination of every subset.
    med_poserr : array of float
        Median positional uncertainty of every subset.
    """
    if len(dec) <= interv_size:
        raise ValueError(
            "Sample size is too small for the specified interval size.")

    # Sort the data according to the declination
    ind = np.argsort(dec)
    dec_sort = np.take(dec, ind)
    poserr_sort = np.take(sig_pos_max, ind)

    interv_num = len(dec_sort) - interv_size + 1
    med_dec = np.zeros(interv_num)
    med_poserr = np.zeros(interv_num)

    for i in range(interv_num):
        ind_b, ind_e = i, i + interv_size
        deci = dec_sort[ind_b: ind_e]
        pos_erri = poserr_sort[ind_b: ind_e]

        med_dec[i] = np.median(deci)
        med_poserr[i] = np.median(pos_erri)

    return med_dec, med_poserr


def smooth_by_time(t, x, tb=None, te=None, ts=0.1):
    """Smooth the series by time coordinate.

    Parameters
    ----------
    t : array_like of float
        Time coordinate of series.
    x : array_like of float
        Values of series.
    tb : float, optional
        Beginning time of the first bin.
    te : float, optional
        End time of the last bin.
    ts : float, optional
        Bin size. The default value is 0.1.

    Returns
    -------
    t_med : array of float
        Median time coordinate of the bin.
    med : array of float
        Smoothed median of original series.
    """
    if tb is None:
        tb = np.min(t)  # Beginning
    if te is None:
        te = np.max(t)  # End

    bin_num = int((te - tb) // ts) + 1
    med = np.zeros(bin_num)
    t_med = np.zeros(bin_num)

    for i in range(bin_num-1):
        t1i = tb + i * ts
        t2i = t1i + ts

        mask = (t1i <= t) & (t < t2i)
        if np.any(mask):  # Check if the bin has any data
            med[i] = np.median(x[mask])
            t_med[i] = np.median(t[mask])
        else:
            med[i] = np.nan
            t_med[i] = np.nan

    # Last element
    t1e = tb + (bin_num-1) * ts
    t2e = t1e + ts
    mask = (t1e <= t) & (t <= t2e)
    if np.any(mask):
        med[-1] = np.median(x[mask])
        t_med[-1] = np.median(t[mask])
    else:
        med[-1] = np.nan
        t_med[-1] = np.nan

    return t_med, med


def calculate_normalized_proper_motion(pmra, pmra_err, pmdec, pmdec_err, pm_ra_dec_cor):
    """
    Calculate the normalized proper motion.

    Parameters
    ----------
    pmra : float or array-like
        Proper motion in Right Ascension (including cos(Dec) factor).
    pmra_err : float or array-like
        Formal uncertainty of pmra.
    pmdec : float or array-like
        Proper motion in Declination.
    pmdec_err : float or array-like
        Formal uncertainty of pmdec.
    pm_ra_dec_cor : float or array-like
        Correlation coefficient between pmra and pmdec.

    Returns
    -------
    X : float or ndarray
        Normalized proper motion, unitless.
    """
    X_a = pmra / pmra_err
    X_d = pmdec / pmdec_err

    # Avoid singularities in the correlation coefficient
    pm_ra_dec_cor = np.clip(pm_ra_dec_cor, -0.99999, 0.99999)
    X2 = (X_a**2 + X_d**2 - 2 * pm_ra_dec_cor *
          X_a * X_d) / (1 - pm_ra_dec_cor**2)
    X = np.sqrt(X2)

    return X


def calculate_normalized_separation(dRA, dRA_err, dDec, dDec_err, C):
    """
    Calculate the normalized separation.

    Parameters
    ----------
    dRA : float or array-like
        Right Ascension difference in micro-arcseconds.
    dRA_err : float or array-like
        Formal uncertainty of dRA.
    dDec : float or array-like
        Declination difference in micro-arcseconds.
    dDec_err : float or array-like
        Formal uncertainty of dDec.
    C : float or array-like
        Correlation coefficient between dRA and dDec.

    Returns
    -------
    ang_sep : float or ndarray
        Angular separation in micro-arcseconds.
    X_a : float or ndarray
        Normalized RA coordinate difference, unitless.
    X_d : float or ndarray
        Normalized Dec coordinate difference, unitless.
    X : float or ndarray
        Normalized separation, unitless.
    """
    ang_sep = np.sqrt(dRA**2 + dDec**2)

    X_a = dRA / dRA_err
    X_d = dDec / dDec_err

    # Avoid singularities in the correlation coefficient
    C = np.clip(C, -0.99999, 0.99999)
    X = np.sqrt((X_a**2 + X_d**2 - 2 * C * X_a * X_d) / (1 - C**2))

    return ang_sep, X_a, X_d, X


def calculate_coordinate_offset(RA1, RA1_err, Dec1, Dec1_err, Cor1,
                                RA2, RA2_err, Dec2, Dec2_err, Cor2,
                                arccof=None):
    """
    Calculate the normalized separation between two sets of RA/Dec positions.

    Parameters
    ----------
    RA1, RA2 : float or array-like
        Right Ascension in degrees.
    Dec1, Dec2 : float or array-like
        Declination in degrees.
    RA1_err, RA2_err : float or array-like
        Formal uncertainty of RA1 * cos(Dec1) and RA2 * cos(Dec2), in mas.
    Dec1_err, Dec2_err : float or array-like
        Formal uncertainty of Dec1 and Dec2, in mas.
    Cor1, Cor2 : float or array-like
        Correlation coefficient between RA and Dec for the respective positions.
    arccof : float or array-like, optional
        Cosine of Declination for the first set of coordinates. If None, it is calculated.

    Returns
    -------
    dRA : float or ndarray
        RA offset in micro-arcseconds.
    dDec : float or ndarray
        Dec offset in micro-arcseconds.
    dRA_err : float or ndarray
        Combined RA uncertainty in micro-arcseconds.
    dDec_err : float or ndarray
        Combined Dec uncertainty in micro-arcseconds.
    cov : float or ndarray
        Combined covariance between RA and Dec.
    ang_sep : float or ndarray
        Angular separation in micro-arcseconds.
    X_a : float or ndarray
        Normalized RA separation, unitless.
    X_d : float or ndarray
        Normalized Dec separation, unitless.
    X : float or ndarray
        Normalized overall separation, unitless.
    """

    if arccof is None:
        arccof = np.cos(np.deg2rad(Dec1))

    # Calculate differences (deg -> micro-arcseconds)
    dRA = (RA1 - RA2) * 3.6e6 * arccof
    dRA_err = np.sqrt(RA1_err**2 + RA2_err**2)
    dDec = (Dec1 - Dec2) * 3.6e6
    dDec_err = np.sqrt(Dec1_err**2 + Dec2_err**2)

    # Correlation coefficient of combined errors
    cov = RA1_err * Dec1_err * Cor1 + RA2_err * Dec2_err * Cor2
    corf = cov / (dRA_err * dDec_err)

    # Calculate normalized separation
    ang_sep, X_a, X_d, X = calculate_normalized_separation(dRA, dRA_err,
                                                           dDec, dDec_err, corf)

    return dRA, dDec, dRA_err, dDec_err, cov, ang_sep, X_a, X_d, X


def calculate_positional_angle_basic(dra, ddec, anticw=False):
    """
    Calculate positional angles from positional offsets using basic trigonometry.

    Parameters
    ----------
    dra : ndarray
        Positional difference in Right Ascension (times cos(decl.)).
    ddec : ndarray
        Positional difference in Declination.
    anticw : bool, optional
        If True, calculate the angle anti-clockwise; otherwise, clockwise. Default is False.

    Returns
    -------
    Ax : ndarray
        Angle (in degrees) of positional offset vector towards the x-axis (anti-clockwise).
    Ay : ndarray
        Angle (in degrees) of positional offset vector towards the y-axis (anti-clockwise).
    """

    Ax = np.rad2deg(np.arctan2(ddec, dra))  # anti-clockwise
    Ay = np.rad2deg(np.arctan2(dra, ddec))  # anti-clockwise

    if anticw:
        # Anti-clockwise
        Ax = np.where(Ax < 0, 360 + Ax, Ax)
        Ay = np.where(Ay < 0, -Ay, 360 - Ay)
    else:
        # Clockwise
        Ax = np.where(Ax < 0, -Ax, 360 - Ax)
        Ay = np.where(Ay < 0, 360 + Ay, Ay)

    return Ax, Ay


def calculate_positional_angle_complex(dra, ddec, anticw=False):
    """
    Calculate positional angles from positional offsets using complex numbers.

    Parameters
    ----------
    dra : ndarray
        Positional difference in Right Ascension (times cos(decl.)).
    ddec : ndarray
        Positional difference in Declination.
    anticw : bool, optional
        If True, calculate the angle anti-clockwise; otherwise, clockwise. Default is False.

    Returns
    -------
    Ax : ndarray
        Angle (in degrees) of positional offset vector towards the x-axis (anti-clockwise).
    Ay : ndarray
        Angle (in degrees) of positional offset vector towards the y-axis (anti-clockwise).
    """

    if anticw:
        # Anti-clockwise
        zx = dra + 1j * ddec
        zy = ddec - 1j * dra
    else:
        # Clockwise
        zx = dra - 1j * ddec
        zy = ddec + 1j * dra

    Ax = np.angle(zx, deg=True)
    Ay = np.angle(zy, deg=True)

    Ax = np.where(Ax < 0, 360 + Ax, Ax)
    Ay = np.where(Ay < 0, 360 + Ay, Ay)

    return Ax, Ay


def calculate_positional_angle_astropy(dra, ddec):
    """
    Calculate positional angle from positional offset using Astropy's SkyCoord.

    Parameters
    ----------
    dra : ndarray
        Positional difference in Right Ascension (times cos(decl.)).
    ddec : ndarray
        Positional difference in Declination.

    Returns
    -------
    PA : ndarray
        Positional angle (in degrees) of the positional offset vector towards the y-axis (anti-clockwise).
    """

    cen = SkyCoord(0 * u.deg, 0 * u.deg, frame="icrs")
    oft = SkyCoord(dra * u.mas, ddec * u.mas, frame="icrs")

    pa = cen.position_angle(oft)
    pa = pa.to(u.deg)

    return pa.value


def calculate_positional_offset_errors(dra, ddec, dra_err, ddec_err, cov, rho, phi,
                                       eema1, eena1, eepa1, eema2, eena2, eepa2):
    """
    Calculate formal errors for arclength and orientation of the position offset vector.

    This function follows the methodology described in Petrov, Kovalev, Plavin (2020)
    (MNRAS 482, 3023-3031).

    Parameters
    ----------
    dra : float or ndarray
        Positional difference in Right Ascension (times cos(Dec)), in mas.
    ddec : float or ndarray
        Positional difference in Declination, in mas.
    dra_err : float or ndarray
        Uncertainty of dra, in mas.
    ddec_err : float or ndarray
        Uncertainty of ddec, in mas.
    cov : float or ndarray
        Covariance between dra and ddec.
    rho : float or ndarray
        Arclength of the positional offset vector, in mas.
    phi : float or ndarray
        Orientation angle of the positional offset vector, in degrees.
    eema1, eena1, eepa1 : float or ndarray
        Semi-major axis, semi-minor axis, and position angle of the first ellipse, in mas and degrees.
    eema2, eena2, eepa2 : float or ndarray
        Semi-major axis, semi-minor axis, and position angle of the second ellipse, in mas and degrees.

    Returns
    -------
    sigma_rho : float or ndarray
        Formal error in the arclength (rho), in mas.
    sigma_phi : float or ndarray
        Formal error in the orientation angle (phi), in degrees.
    """

    # Calculate the uncertainties of arc-length (rho)
    tan_ang1 = np.tan(np.deg2rad(eepa1 - phi))**2
    ratio1 = (eema1 / eena1)**2
    tan_ang2 = np.tan(np.deg2rad(eepa2 - phi))**2
    ratio2 = (eema2 / eena2)**2
    sigma_rho2 = ((1 + tan_ang1) / (1 + tan_ang1 * ratio1) * eema1**2 +
                  (1 + tan_ang2) / (1 + tan_ang2 * ratio2) * eema2**2)
    sigma_rho = np.sqrt(sigma_rho2)

    # Calculate the uncertainty of the positional angle (phi)
    term1 = (dra * ddec_err) ** 2
    term2 = (ddec * dra_err) ** 2
    term3 = 2 * dra * ddec * cov
    sigma_phi2 = (term1 + term2 - term3) / rho ** 4
    sigma_phi = np.sqrt(sigma_phi2)

    # Convert radian to degree
    sigma_phi = np.rad2deg(sigma_phi)

    return sigma_rho, sigma_phi


def calculate_positional_differences_values(com_sou, lon_str, lat_str, label1, label2, ref_err=True):
    """
    Calculate the positional differences and their associated errors.

    Parameters
    ----------
    com_sou : astropy.table.Table
        The combined source table.
    lon_str : str
        The longitude coordinate name.
    lat_str : str
        The latitude coordinate name.
    label1, label2 : str
        Labels to distinguish columns from the two catalogs.
    ref_err : bool, optional
        If True, considers the positional uncertainty in the reference catalog.

    Returns
    -------
    dra, ddec : ndarray
        Positional differences in longitude and latitude.
    dra_err, ddec_err : ndarray
        Errors associated with the positional differences.
    arc_fac : ndarray
        Cosine of the declination for the second catalog.
    """

    arc_fac = np.cos(com_sou[f"{lat_str}_{label2}"].to(u.rad).value)

    # Unit: degree
    dra = (com_sou[f"{lon_str}_{label1}"] -
           com_sou[f"{lon_str}_{label2}"]) * arc_fac
    ddec = (com_sou[f"{lat_str}_{label1}"] -
            com_sou[f"{lat_str}_{label2}"])
    if com_sou[f"{lon_str}_err_{label1}"].unit == u.mas:
        dra = dra * 3600e3
        ddec = ddec * 3600e3
    elif com_sou[f"{lon_str}_err_{label1}"].unit == u.uas:
        dra = dra * 3600e6
        ddec = ddec * 3600e6

    ra_err1 = com_sou[f"{lon_str}_err_{label1}"]
    dec_err1 = com_sou[f"{lat_str}_err_{label1}"]

    if ref_err:
        ra_err2 = com_sou[f"{lon_str}_err_{label2}"]
        dec_err2 = com_sou[f"{lat_str}_err_{label2}"]
    else:
        ra_err2 = np.zeros(len(com_sou))
        dec_err2 = np.zeros(len(com_sou))

    dra_err = np.sqrt(ra_err1**2 + ra_err2**2)
    ddec_err = np.sqrt(dec_err1**2 + dec_err2**2)

    return dra, ddec, dra_err, ddec_err


def compute_covariance_or_correlation(com_sou, lon_str, lat_str, label1, label2, dra_err, ddec_err, ref_err=True):
    """
    Compute the combined covariance or correlation for the positional errors.

    Parameters
    ----------
    com_sou : astropy.table.Table
        The combined source table.
    lon_str, lat_str : str
        The longitude and latitude coordinate names.
    label1, label2 : str
        Labels to distinguish columns from the two catalogs.
    dra_err, ddec_err : ndarray
        Errors associated with the positional differences.
    ref_err : bool, optional
        If True, considers the positional uncertainty in the reference catalog.

    Returns
    -------
    cov, corf : ndarray
        The combined covariance and correlation values.
    """
    cor_str1 = f"{lon_str}_{lat_str}_corr"
    cov_str = f"{lon_str}_{lat_str}_cov"

    if cor_str1 in com_sou.colnames:
        ra_dec_cor1 = com_sou[f"{cor_str1}_{label1}"]
        ra_dec_cor2 = com_sou[f"{cor_str1}_{label2}"] if ref_err else np.zeros(
            len(com_sou))
        ra_dec_cov1 = com_sou[f"{lon_str}_err_{label1}"] * \
            com_sou[f"{lat_str}_err_{label1}"] * ra_dec_cor1
        ra_dec_cov2 = com_sou[f"{lon_str}_err_{label2}"] * \
            com_sou[f"{lat_str}_err_{label2}"] * ra_dec_cor2
        cov = ra_dec_cov1 + ra_dec_cov2
        corf = cov / (dra_err * ddec_err)

        com_sou.remove_columns(
            [f"{cor_str1}_{label1}", f"{cor_str1}_{label2}"])

    elif cov_str in com_sou.colnames:
        ra_dec_cov1 = com_sou[f"{cov_str}_{label1}"]
        ra_dec_cov2 = com_sou[f"{cov_str}_{label2}"] if ref_err else np.zeros(
            len(com_sou))
        cov = ra_dec_cov1 + ra_dec_cov2
        corf = cov / (dra_err * ddec_err)

        com_sou.remove_columns([f"{cov_str}_{label1}", f"{cov_str}_{label2}"])

    else:
        cov = np.zeros(len(com_sou))
        corf = np.zeros(len(com_sou))

    return cov, corf


def calculate_separation_and_angle(com_sou, lon_str, lat_str, dra, ddec, dra_err, ddec_err, cov, corf, ref_err, label1, label2):
    """
    Calculate the normalized separation, positional angle, and related metrics.

    Parameters
    ----------
    com_sou : astropy.table.Table
        The combined source table.
    lon_str, lat_str : str
        The longitude and latitude coordinate names.
    dra, ddec : ndarray
        Positional differences in longitude and latitude.
    dra_err, ddec_err : ndarray
        Errors associated with the positional differences.
    cov, corf : ndarray
        The combined covariance and correlation values.

    Returns
    -------
    ang_sep, ang_sep_err, pa, pa_err, X_a, X_d, X : ndarray
        Calculated values for angular separation, its error, positional angle, its error,
        and the normalized separations.
    """
    ang_sep, X_a, X_d, X = calculate_normalized_separation(
        dra, dra_err, ddec, ddec_err, corf)
    pax, pay = calculate_positional_angle_complex(dra, ddec)
    pa = Column(pay, unit=u.deg)

    eema1, eena1, eepa1 = calculate_error_ellipses(
        com_sou[f"{lon_str}_err_{label1}"], com_sou[f"{lat_str}_err_{label1}"], com_sou[f"{lon_str}_{lat_str}_corr_{label1}"])
    eema2, eena2, eepa2 = calculate_error_ellipses(
        com_sou[f"{lon_str}_err_{label2}"], com_sou[f"{lat_str}_err_{label2}"], com_sou[f"{lon_str}_{lat_str}_corr_{label2}"]) if ref_err else (0, 1, 0)

    ang_sep_err, pa_err = calculate_positional_offset_errors(
        dra, ddec, dra_err, ddec_err, cov, ang_sep, pay, eema1, eena1, eepa1, eema2, eena2, eepa2)

    return ang_sep, ang_sep_err, pa, pa_err, X_a, X_d, X


def calculate_positional_differences(table1, table2, source_name="source_name",
                                     label=["1", "2"], ref_err=True):
    """
    Calculate the positional differences between two catalogs.

    Parameters
    ----------
    table1, table2 : astropy.table.Table
        Tables containing radio source positions.
    source_name : str, optional
        The name of the column that contains the source names. Default is "source_name".
    label : list of str, optional
        Labels to distinguish the columns from the two catalogs. Default is ["1", "2"].
    ref_err : bool, optional
        If True, considers the positional uncertainty in the reference catalog (table2)
        when computing the uncertainty of positional offset. Default is True.

    Returns
    -------
    com_sou : astropy.table.Table
        Table of positional differences and related calculations.
    """
    # Determine coordinate system
    lon_str, lat_str = determine_coordinate_system(table1)

    # Extract relevant columns
    table3 = extract_position_columns(
        table1, lon_str, lat_str, source_name)
    table4 = extract_position_columns(
        table2, lon_str, lat_str, source_name)

    # Cross-match by source name
    com_sou = join(table3, table4, keys=source_name, table_names=label)

    # Calculate positional differences
    dra, ddec, dra_err, ddec_err = calculate_positional_differences_values(
        com_sou, lon_str, lat_str, label[0], label[1], ref_err)

    # Compute covariance or correlation
    cov, corf = compute_covariance_or_correlation(
        com_sou, lon_str, lat_str, label[0], label[1], dra_err, ddec_err, ref_err)

    # Calculate separation, angle, and other metrics
    ang_sep, ang_sep_err, pa, pa_err, X_a, X_d, X = calculate_separation_and_angle(
        com_sou, lon_str, lat_str, dra, ddec, dra_err, ddec_err, cov, corf, ref_err, label[0], label[1])

    # Add these columns to the final table
    com_sou.add_columns([dra, ddec, dra_err, ddec_err, cov, ang_sep, ang_sep_err, pa, pa_err, X_a, X_d, X],
                        names=[f"d{lon_str}", f"d{lat_str}", f"d{lon_str}_err", f"d{lat_str}_err",
                               f"d{lon_str}_d{lat_str}_cov", "ang_sep", "ang_sep_err", "pa", "pa_err",
                               f"nor_{lon_str}", f"nor_{lat_str}", "nor_sep"])
    com_sou[f"d{lon_str}"].unit = com_sou[f"{lon_str}_err_{label[0]}"].unit
    com_sou[f"d{lat_str}"].unit = com_sou[f"{lon_str}_err_{label[0]}"].unit
    com_sou["ang_sep"].unit = com_sou[f"{lon_str}_err_{label[0]}"].unit
    com_sou["ang_sep_err"].unit = com_sou[f"{lon_str}_err_{label[0]}"].unit
    com_sou["pa_err"].unit = u.deg
    com_sou[f"nor_{lon_str}"].unit = None
    com_sou[f"nor_{lat_str}"].unit = None
    com_sou["nor_sep"].unit = None

    # Remove unnecessary columns and rename others
    com_sou.remove_columns([f"{lon_str}_{label[0]}", f"{lat_str}_{label[0]}"])
    com_sou.rename_column(f"{lon_str}_{label[1]}", lon_str)
    com_sou.rename_column(f"{lat_str}_{label[1]}", lat_str)

    return com_sou


def calculate_pm_differences(com_sou, pmlon_str, pmlat_str, label1, label2, ref_err=True):
    """
    Calculate the proper motion differences and their associated errors.

    Parameters
    ----------
    com_sou : astropy.table.Table
        The combined source table.
    pmlon_str : str
        The proper motion longitude coordinate name.
    pmlat_str : str
        The proper motion latitude coordinate name.
    label1, label2 : str
        Labels to distinguish columns from the two catalogs.
    ref_err : bool, optional
        If True, considers the positional uncertainty in the reference catalog.

    Returns
    -------
    dra, ddec : ndarray
        Proper motion differences in longitude and latitude.
    dra_err, ddec_err : ndarray
        Errors associated with the proper motion differences.
    """
    dra = com_sou[f"{pmlon_str}_{label1}"] - com_sou[f"{pmlon_str}_{label2}"]
    ddec = com_sou[f"{pmlat_str}_{label1}"] - com_sou[f"{pmlat_str}_{label2}"]

    ra_err1 = com_sou[f"{pmlon_str}_err_{label1}"]
    dec_err1 = com_sou[f"{pmlat_str}_err_{label1}"]

    if ref_err:
        ra_err2 = com_sou[f"{pmlon_str}_err_{label2}"]
        dec_err2 = com_sou[f"{pmlat_str}_err_{label2}"]
    else:
        ra_err2 = np.zeros(len(com_sou))
        dec_err2 = np.zeros(len(com_sou))

    dra_err = np.sqrt(ra_err1**2 + ra_err2**2)
    ddec_err = np.sqrt(dec_err1**2 + dec_err2**2)

    return dra, ddec, dra_err, ddec_err


def calculate_proper_motion_differences(table1, table2, source_name="source_name",
                                        label=["1", "2"], ref_err=True):
    """
    Calculate proper motion differences between two catalogs.

    Parameters
    ----------
    table1, table2 : astropy.table.Table
        Tables containing radio source positions.
    source_name : str, optional
        The name of the column that contains the source names. Default is "source_name".
    label : list of str, optional
        Labels to distinguish the columns from the two catalogs. Default is ["1", "2"].
    ref_err : bool, optional
        If True, considers the positional uncertainty in the reference catalog (table2)
        when computing the uncertainty of positional offset. Default is True.

    Returns
    -------
    com_sou : astropy.table.Table
        Table of proper motion differences and related calculations.
    """
    # Determine proper motion coordinate system
    lon_str, lat_str, pmlon_str, pmlat_str = determine_pm_coordinate_system(
        table1)

    # Extract relevant columns
    table3 = extract_pm_columns(
        table1, pmlon_str, pmlat_str, lon_str, lat_str, source_name, label[0], ref_err)
    table4 = extract_pm_columns(
        table2, pmlon_str, pmlat_str, lon_str, lat_str, source_name, label[1], ref_err)

    # Cross-match by source name
    com_sou = join(table3, table4, keys=source_name, table_names=label)

    # Calculate proper motion differences
    dra, ddec, dra_err, ddec_err = calculate_pm_differences(
        com_sou, pmlon_str, pmlat_str, label[0], label[1], ref_err)

    # Compute covariance or correlation
    cov, corf = compute_covariance_or_correlation(
        com_sou, pmlon_str, pmlat_str, label[0], label[1], dra_err, ddec_err, ref_err)

    # Calculate separation, angle, and other metrics
    pm_sep, pm_sep_err, pa, pa_err, X_a, X_d, X = calculate_separation_and_angle(
        com_sou, pmlon_str, pmlat_str, dra, ddec, dra_err, ddec_err, cov, corf, ref_err, label[0], label[1])

    # Add these columns to the final table
    com_sou.add_columns([dra, ddec, dra_err, ddec_err, cov, pm_sep, pm_sep_err, pa, pa_err, X_a, X_d, X],
                        names=[f"d{pmlon_str}", f"d{pmlat_str}", f"d{pmlon_str}_err", f"d{pmlat_str}_err",
                               f"d{pmlon_str}_d{pmlat_str}_cov", "pm_sep", "pm_sep_err", "pm_pa", "pm_pa_err",
                               f"nor_pm_{pmlon_str}", f"nor_pm_{pmlat_str}", "nor_pm_sep"])

    com_sou["pm_sep"].unit = com_sou[f"{pmlon_str}_err_{label[0]}"].unit
    com_sou["pm_sep_err"].unit = com_sou[f"{pmlon_str}_err_{label[0]}"].unit
    com_sou["pm_pa_err"].unit = u.deg
    com_sou[f"nor_pm_{pmlon_str}"].unit = None
    com_sou[f"nor_pm_{pmlat_str}"].unit = None
    com_sou["nor_pm_sep"].unit = None

    # Remove unnecessary columns and rename others
    com_sou.remove_columns(
        [f"{pmlon_str}_{label[0]}", f"{pmlat_str}_{label[0]}"])
    com_sou.rename_column(f"{pmlon_str}_{label[1]}", pmlon_str)
    com_sou.rename_column(f"{pmlat_str}_{label[1]}", pmlat_str)

    return com_sou
