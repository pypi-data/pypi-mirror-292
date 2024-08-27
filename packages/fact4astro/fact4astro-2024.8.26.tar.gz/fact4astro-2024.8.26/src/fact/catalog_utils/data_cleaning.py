#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: data_cleaning.py
"""
Created on Mon 26 Aug 2024 08:29:20 PM CST

@author: Neo(niu.liu@nju.edu.cn)
"""

import numpy as np

from .analysis_tools import calculate_normalized_separation
from .vsh_utils import calculate_residuals


# ------------------ FUNCTION --------------------------------
def eliminate_outliers_nsigma(y1r, y2r, y1_err=None, y2_err=None, n=3.0, wgt_flag=False):
    """Eliminate outliers using n-sigma criteria.

    Parameters
    ----------
    y1r : array of float
        Residuals of RA.
    y2r : array of float
        Residuals of Dec.
    y1_err : array of float, optional
        Formal uncertainties of y1r, required if wgt_flag is True.
    y2_err : array of float, optional
        Formal uncertainties of y2r, required if wgt_flag is True.
    n : float, optional
        The threshold for outlier elimination, defined in terms of standard deviations.
        Default is 3.0.
    wgt_flag : bool, optional
        If True, use weighted RMS (wrms) instead of unweighted RMS (rms).
        Default is False.

    Returns
    ----------
    ind_good : array of bool
        Boolean array where True indicates a good observation.
    """

    if wgt_flag:
        if y1_err is None or y2_err is None:
            raise ValueError(
                "y1_err and y2_err must be provided when wgt_flag is True.")

        # Weighted RMS
        std1 = np.sqrt(np.sum(y1r**2 / y1_err**2) / np.sum(y1_err**-2))
        std2 = np.sqrt(np.sum(y2r**2 / y2_err**2) / np.sum(y2_err**-2))
    else:
        # Unweighted RMS
        std1 = np.sqrt(np.sum(y1r**2) / (y1r.size - 1))
        std2 = np.sqrt(np.sum(y2r**2) / (y2r.size - 1))

    # Determine good observations based on the n-sigma criterion
    mask1 = np.abs(y1r) <= n * std1
    mask2 = np.abs(y2r) <= n * std2
    ind_good = mask1 & mask2

    return ind_good


# ----------------------------------------------------
def eliminate_by_angular_separation(angsep, pho_max=10.0e3):
    """An outlier elimination based on optical-radio angular separation.

    Parameters
    ----------
    angsep : array of float
        angular separation, in micro-as
    pho_max : float
        accepted maximum angular separation, default 10.0 mas

    Returns
    ----------
    ind_good : array of int
        index of good observations
    """

    ind_good = angsep <= pho_max

    return ind_good


# ----------------------------------------------------
def eliminate_by_normalized_separation(X, X_max=10.0):
    """An outlier elimination based on the normalized optical-radio separation.

    Parameters
    ----------
    X : array of float
        normalized separations, unit-less.
    X_max : float
        accepted maximum X, default 10.0

    Returns
    ----------
    ind_good : array of int
        index of good observations
    """

    ind_good = X <= X_max

    return ind_good


# ----------------------------------------------------
def filter_good_observations(dRA, dDE, e_dRA, e_dDE, cov, RA, DE, ind_good):
    """Find the good observations based on index.

    Parameters
    ----------
    dRA/dDE : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    e_dRA/e_dDE : array of float
        formal uncertainty of dRA(*cos(DE))/dDE in uas
    cov : array of float
        covariance between dRA and dDE in uas^2
    RA/DE : array of float
        Right ascension/Declination in radian
    ind_good : array of int
        index of good observations

    Returns
    ----------
    dRAn/dDEn : array of float
        R.A.(*cos(Dec.))/Dec. differences for good observations in uas
    e_dRAn/e_dDEn : array of float
        formal uncertainty of dRA(*cos(DE))/dDE good observations in uas
    covn : array of float
        covariance between dRA and dDE good observations in uas^2
    RAn/DEn : array of float
        Right ascension/Declination good observations in radian
    """

    dRAn = dRA[ind_good]
    dDEn = dDE[ind_good]
    e_dRAn = e_dRA[ind_good]
    e_dDEn = e_dDE[ind_good]
    RAn = RA[ind_good]
    DEn = DE[ind_good]

    if cov is None:
        covn = None
    else:
        covn = cov[ind_good]

    return dRAn, dDEn, e_dRAn, e_dDEn, covn, RAn, DEn


def eliminate_outliers_by_sigma(dra, ddec, dra_err, ddec_err, ra, dec, cov, fit_type, l_max, sigma_threshold, log_file):
    """Eliminate outliers using sigma-clipping."""
    params, uncertainties, correlation_matrix = solve_vsh(
        dra, ddec, dra_err, ddec_err, ra, dec, cov, fit_type, l_max)

    num1, num2 = 1, 0
    while num1 != num2:
        num1 = num2
        rra, rdec = calculate_residuals(
            dra, ddec, ra, dec, params, fit_type, l_max)
        good_indices = eliminate_outliers_nsigma(rra, rdec, sigma_threshold)
        num2 = dra.size - good_indices.size

        dra_n, ddec_n, dra_err_n, ddec_err_n, cov_n, ra_n, dec_n = filter_good_observations(
            dra, ddec, dra_err, ddec_err, cov, ra, dec, good_indices)

        if log_file is not None:
            print("# Number of samples: %d" % (dra.size - num2), file=log_file)

    return dra_n, ddec_n, dra_err_n, ddec_err_n, cov_n, ra_n, dec_n, good_indices


def eliminate_outliers_by_criteria(dra, ddec, dra_err, ddec_err, ra, dec, cov, ang_sep, X, elimination_criteria, threshold, fit_type, l_max, log_file):
    """Eliminate outliers based on angular or normalized separation."""
    if ang_sep is None:
        ang_sep, X_a, X_d, X = calculate_normalized_separation(
            dra, ddec, dra_err, ddec_err, cov)

    if elimination_criteria == "angsep":
        good_indices = eliminate_by_normalized_separation(ang_sep, threshold)
    elif elimination_criteria == "norsep":
        good_indices = eliminate_by_normalized_separation(
            X, threshold)
    elif elimination_criteria == "nor_ang":
        good_indices_nor = eliminate_by_normalized_separation(
            X, threshold)
        good_indices_ang = eliminate_by_normalized_separation(
            ang_sep, threshold)
        good_indices = good_indices_nor & good_indices_ang
    else:
        raise ValueError(
            "Invalid elimination_criteria: must be 'sigma', 'angsep', 'norsep', or 'nor_ang'")

    # Find all good observations
    dra_n, ddec_n, dra_err_n, ddec_err_n, cov_n, ra_n, dec_n = filter_good_observations(
        dra, ddec, dra_err, ddec_err, cov, ra, dec, good_indices)

    if log_file is not None:
        print("# Number of samples: %d" % dra_n.size, file=log_file)

    return dra_n, ddec_n, dra_err_n, ddec_err_n, cov_n, ra_n, dec_n, good_indices
