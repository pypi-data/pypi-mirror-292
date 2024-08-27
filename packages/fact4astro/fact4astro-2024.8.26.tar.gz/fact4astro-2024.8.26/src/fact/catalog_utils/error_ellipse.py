#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: calc_error_ellipse_pmt.py
"""
Module to compute parameters of the error ellipse in astrometric measurements.

Created on Mon 22 Jan 2024 09:02:54 PM CST

Author: Neo (niu.liu@nju.edu.cn)

This module contains functions to compute the semi-major axis, semi-minor axis,
and position angle of the error ellipse based on input uncertainties and correlations.

"""

import numpy as np
from astropy.table import Column
from astropy import units as u


# -----------------------------  FUNCTIONS -----------------------------

def calculate_sig_pos_max(ra_err, dec_err, ra_dec_corr):
    """Calculate the semi-major axis of the dispersion ellipse."""
    sig_pos_max = np.sqrt(0.5 * (ra_err**2 + dec_err**2 +
                                 np.sqrt((ra_err**2 - dec_err**2)**2 +
                                         (2 * ra_err * dec_err * ra_dec_corr)**2)))
    return sig_pos_max


def calculate_overall_error(ra_err, dec_err, ra_dec_corr):
    """Calculate the overall formal uncertainty."""
    overall_err = np.sqrt(ra_err**2 + dec_err**2 + 2 *
                          ra_err * dec_err * ra_dec_corr)
    return overall_err


def calculate_single_error_ellipse(ra_err, dec_err, ra_dec_corr, anticw=False):
    """Calculate the overall formal uncertainty and error ellipse parameters for a single object."""
    cov = ra_dec_corr * ra_err * dec_err
    cov_mat = np.array([[ra_err**2, cov], [cov, dec_err**2]])

    eig_val, eig_vec = np.linalg.eig(cov_mat)

    if eig_val[0] > eig_val[1]:
        M2, m2 = eig_val[0], eig_val[1]
        vec_M = eig_vec[:, 0]
    else:
        M2, m2 = eig_val[1], eig_val[0]
        vec_M = eig_vec[:, 1]

    M, m = np.sqrt(M2), np.sqrt(m2)

    if vec_M[1] == 0:
        pa0 = 90 if vec_M[0] > 0 else -90
    else:
        pa0 = np.rad2deg(np.arctan(vec_M[0] / vec_M[1]))

    if anticw:
        pa = -pa0 if pa0 <= 0 else 180 - pa0
    else:
        pa = 180 + pa0 if pa0 <= 0 else pa0

    return M, m, pa


def calculate_single_error_ellipse_alternate(ra_err, dec_err, ra_dec_corr):
    """Calculate the error ellipse parameters using an alternative method."""
    a = ra_err
    b = dec_err
    r = ra_dec_corr
    rab = r * a * b

    theta = 0.5 * np.arctan2(2 * rab, (a**2 - b**2))

    sx = a**2 * np.cos(theta)**2 + b**2 * np.sin(theta)**2 + \
        2 * rab * np.sin(theta) * np.cos(theta)
    sy = a**2 * np.sin(theta)**2 + b**2 * np.cos(theta)**2 - \
        2 * rab * np.sin(theta) * np.cos(theta)
    eema = np.sqrt(np.maximum(sx, sy))
    eena = np.sqrt(np.minimum(sx, sy))

    theta0 = 360 + theta if theta < 0 else theta
    pa = (360 - (theta0 - 90)) % 360 if a >= b else 360 - theta0

    return eema, eena, pa


def calculate_position_angle(ra_err, dec_err, ra_dec_corr, anticw=False):
    """Calculate the position angle of the major axis of the error ellipse for a single object."""
    _, _, pa = calculate_single_error_ellipse(
        ra_err, dec_err, ra_dec_corr, anticw)
    return pa


def calculate_position_angles(ra_err, dec_err, ra_dec_corr, anticw=False):
    """Calculate the position angles for an array of objects."""
    pa = np.zeros_like(ra_err)
    for i in range(len(ra_err)):
        pa[i] = calculate_position_angle(
            ra_err[i], dec_err[i], ra_dec_corr[i], anticw)
    return pa


def calculate_ellipse_shape(M, m, pa, start_from_xaxis=False):
    """Calculate the (x, y) positions for an ellipse after rotation."""
    t = np.linspace(0, 2 * np.pi, 360)
    x = M * np.cos(t)
    y = m * np.sin(t)

    alpha = np.deg2rad(pa if start_from_xaxis else 90 - pa)

    x1 = x * np.cos(alpha) - y * np.sin(alpha)
    y1 = x * np.sin(alpha) + y * np.cos(alpha)

    return x1, y1


def calculate_error_ellipses(ra_err, dec_err, ra_dec_corr, anticw=False):
    """Calculate parameters of the error ellipse for a subset of objects."""
    if isinstance(ra_err, (np.ndarray, Column)):
        ra_err = np.asarray(ra_err)
        dec_err = np.asarray(dec_err)
        ra_dec_corr = np.asarray(ra_dec_corr)

        M = np.zeros_like(ra_err)
        m = np.zeros_like(dec_err)
        pa = np.zeros_like(ra_dec_corr)

        for i in range(len(M)):
            M[i], m[i], pa[i] = calculate_single_error_ellipse(
                ra_err[i], dec_err[i], ra_dec_corr[i], anticw
            )
    else:
        M, m, pa = calculate_single_error_ellipse(
            ra_err, dec_err, ra_dec_corr, anticw
        )

    return M, m, pa


def compute_error_ellipse_par(catalog, indexes):
    """Compute and add parameters of the error ellipse to an astropy Table."""
    pos_err_max, pos_err_min, pa = calculate_error_ellipses(
        catalog["ra_err"], catalog["dec_err"], catalog["ra_dec_corr"]
    )

    catalog.add_columns([
        Column(pos_err_max, name="pos_err_max", unit=u.mas),
        Column(pos_err_min, name="pos_err_min", unit=u.mas),
        Column(pa, name="eepa", unit=u.deg)
    ], indexes=indexes)

    return catalog


def calculate_covariance_matrix(data_tab, dra_err, ddec_err):
    """Calculate or retrieve the covariance matrix."""
    if "dra_ddec_cov" in data_tab.colnames:
        dra_ddec_cov = np.array(data_tab["dra_ddec_cov"])
    elif "dra_ddec_cor" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["dra_ddec_cor"])
        dra_ddec_cov = dra_ddc_cor * dra_err * ddec_err
    elif "pmra_pmdec_corr" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_corr"])
        dra_ddec_cov = dra_ddc_cor * dra_err * ddec_err
    elif "pmra_pmdec_cor" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_cor"])
        dra_ddec_cov = dra_ddc_cor * dra_err * ddec_err
    else:
        dra_ddec_cov = None
        print("Covariance matrix not specified, using diagonal covariance matrix.")

    return dra_ddec_cov


if __name__ == "__main__":
    pass

# --------------------------------- END --------------------------------
