#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: calc_error_ellipse_pmt.py
"""
Created on Mon 22 Jan 2024 09:02:54 PM CST

@author: Neo(niu.liu@nju.edu.cn)

This module contains functions to compute parameters of the error ellipse

"""

import numpy as np
import astropy
from astropy.table import Column
from astropy import units as u


__all__ = ["error_ellipse_calc"]


# -----------------------------  FUNCTIONS -----------------------------
def error_ellipse_calc_for_single(ra_err, dec_err, ra_dec_corr, anticw=False):
    """Calculate the ovrall formal uncertainty.

    ovrall formal uncertainty = sqrt(RA_err^2+Dec_err^2+C*RA_err*Dec_err)

    Parameters
    ----------
    ra_err/dec_err : formal uncertainty of RA/Dec, usually in micro-as
    ra_dec_corr : correlation coeffient between RA and Dec, unitless.

    Returns
    ----------
    M : semi-major axis of the error ellipse
    m : semi-minor axis of the error ellipse
    pa : the position angle of the major axis of the error ellipse
    """

    cov = ra_dec_corr * ra_err * dec_err
    cov_mat = np.array([[ra_err**2, cov], [cov, dec_err**2]])

    eig_val, eig_vec = np.linalg.eig(cov_mat)

    if eig_val[0] > eig_val[1]:
        M2 = eig_val[0]
        m2 = eig_val[1]
        vec_M = eig_vec[:, 0]
    else:
        M2 = eig_val[1]
        m2 = eig_val[0]
        vec_M = eig_vec[:, 1]

    M, m = np.sqrt(M2), np.sqrt(m2)

    # Calculate the position angle counted anti-colockwise from the declination axis
    if vec_M[1] == 0:
        if vec_M[0] > 0:
            pa0 = 90
        else:
            pa0 = -90
    else:
        pa0 = np.rad2deg(np.arctan(vec_M[0]/vec_M[1]))

    if anticw:
        if pa0 <= 0:
            pa = -pa0
        else:
            pa = 180 - pa0
    else:
        if pa0 <= 0:
            pa = 180 + pa0
        else:
            pa = pa0

    return M, m, pa


def error_ellipse_calc(ra_err, dec_err, ra_dec_corr, anticw=False):
    """Calculate Parameters of error ellipse for a subset of objects

    Parameters
    ----------
    ra_err/dec_err : 1-d array
        formal uncertainty of RA/Dec
    ra_dec_corr : 1-d array
        correlation coeffient between RA and Dec, unitless.

    Returns
    ----------
    M: 1-d array
        semi-major axis of the error ellipse
    m: 1-d array
        semi-minor axis of the error ellipse
    pa: 1-d array
        the position angle of the major axis of the error ellipse
    """

    if type(ra_err) == np.ndarray:
        # Here I just check the type of ra_err and assume that ra_err, dec_err, and
        # ra_dec_corr belongs to the same data type and has the same shape.
        M = np.zeros_like(ra_err)
        m = np.zeros_like(dec_err)
        pa = np.zeros_like(ra_dec_corr)
        for i in range(len(M)):
            M[i], m[i], pa[i] = error_ellipse_calc_for_single(
                ra_err[i], dec_err[i], ra_dec_corr[i], anticw)

    elif type(ra_err) in [astropy.table.column.Column, astropy.table.column.MaskedColumn]:
        # Or Pandas type?
        # astropy.table -> np.ndarray
        ra_err = np.array(ra_err)
        dec_err = np.array(dec_err)
        ra_dec_corr = np.array(ra_dec_corr)

        M = np.zeros_like(ra_err)
        m = np.zeros_like(dec_err)
        pa = np.zeros_like(ra_dec_corr)

        for i in range(len(M)):
            M[i], m[i], pa[i] = error_ellipse_calc_for_single(
                ra_err[i], dec_err[i], ra_dec_corr[i], anticw)

    else:
        M, m, pa = error_ellipse_calc_for_single(
            ra_err, dec_err, ra_dec_corr, anticw)

    return M, m, pa


def compute_error_ellipse_par(catalog, indexes):
    """Computer parameters of error ellipse
    """

    # Calculate the semi-major axis of error ellipse
    pos_err_max, pos_err_min, pa = error_ellipse_calc(
        catalog["ra_error"], catalog["dec_error"], catalog["ra_dec_corr"])

    # Add the semi-major axis of error ellipse to the table
    pos_err_max = Column(pos_err_max, name="pos_err_max", unit=u.mas)
    pos_err_min = Column(pos_err_min, name="pos_err_min", unit=u.mas)
    pa = Column(pa, name="eepa", unit=u.deg)

    # Add columns
    catalog.add_columns([pos_err_max, pos_err_min, pa], indexes=indexes)

    return catalog


if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
