#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: iers_transformations.py
"""
Created on Mon 26 Aug 2024 05:26:26 PM CST

@author: Neo(niu.liu@nju.edu.cn)
"""

import sys
from scipy.optimize import curve_fit
import numpy as np

from astropy.table import Table
from astropy import units as u
from .analysis_tools import compute_chi_squared_2d, compute_goodness_of_fit


# ========================= IERS Transformation Functions =========================

def apply_rotation(X):
    """
    Apply a basic rotation transformation based on input parameters.

    Parameters
    ----------
    X : 1-D array
        (ra, dec) in radians
    """
    ra, dec = X
    dra = -locals["r1"] * np.cos(ra) * np.sin(dec) - locals["r2"] * np.sin(ra) * np.sin(dec) + \
        locals["r3"] * np.cos(dec)
    ddec = locals["r1"] * np.sin(ra) - locals["r2"] * np.cos(ra)

    return np.concatenate((dra, ddec))


def rigid_rotation(pos, rx, ry, rz):
    """
    Apply a rigid rotation to celestial coordinates.

    Parameters
    ----------
    pos : array of float
        Right ascension/declination in radians.
    rx, ry, rz : float
        Rotational angles around X-, Y-, and Z-axis.

    Returns
    -------
    dpos : array of float
        R.A.(*cos(Dec.))/Dec. differences.
    """
    N = len(pos) // 2
    ra, dec = pos[:N], pos[N:]

    dra = -rx * np.cos(ra) * np.sin(dec) - ry * \
        np.sin(ra) * np.sin(dec) + rz * np.cos(dec)
    ddec = rx * np.sin(ra) - ry * np.cos(ra)
    dpos = np.concatenate((dra, ddec))

    return dpos


def rotation_with_declination_bias(pos, rx, ry, rz, dz):
    """
    Apply a rotation with an additional declination bias.

    Parameters
    ----------
    pos : array of float
        Right ascension/declination in radians.
    rx, ry, rz : float
        Rotational angles around X-, Y-, and Z-axis.
    dz : float
        Bias in declination.

    Returns
    -------
    dpos : array of float
        R.A.(*cos(Dec.))/Dec. differences.
    """
    N = len(pos) // 2
    ra, dec = pos[:N], pos[N:]

    dra = -rx * np.cos(ra) * np.sin(dec) - ry * \
        np.sin(ra) * np.sin(dec) + rz * np.cos(dec)
    ddec = rx * np.sin(ra) - ry * np.cos(ra) + dz
    dpos = np.concatenate((dra, ddec))

    return dpos


def rotation_with_declination_slope_and_bias_a(pos, rx, ry, rz, d1, d2, b2):
    """
    Apply a rotation with declination-dependent slopes and a bias (version a).

    Parameters
    ----------
    pos : array of float
        Right ascension/declination in radians.
    rx, ry, rz : float
        Rotational angles around X-, Y-, and Z-axis.
    d1, d2 : float
        Declination-dependent slopes in right ascension/declination.
    b2 : float
        Bias in declination.

    Returns
    -------
    dpos : array of float
        R.A.(*cos(Dec.))/Dec. differences.
    """
    N = len(pos) // 2
    ra, dec = pos[:N], pos[N:]
    dec0 = 0
    delta_dec = dec - dec0

    dra = -rx * np.cos(ra) * np.sin(dec) - ry * np.sin(ra) * np.sin(dec) + rz * np.cos(dec) \
        + d1 * delta_dec * np.cos(dec)
    ddec = rx * np.sin(ra) - ry * np.cos(ra) + d2 * delta_dec + b2
    dpos = np.concatenate((dra, ddec))

    return dpos


def rotation_with_declination_slope_and_bias_b(pos, rx, ry, rz, d1, d2, b2):
    """
    Apply a rotation with declination-dependent slopes and a bias (version b).

    Parameters
    ----------
    pos : array of float
        Right ascension/declination in radians.
    rx, ry, rz : float
        Rotational angles around X-, Y-, and Z-axis.
    d1, d2 : float
        Declination-dependent slopes in right ascension/declination.
    b2 : float
        Bias in declination.

    Returns
    -------
    dpos : array of float
        R.A.(*cos(Dec.))/Dec. differences.
    """
    N = len(pos) // 2
    ra, dec = pos[:N], pos[N:]
    dec0 = 0
    delta_dec = dec - dec0

    dra = -rx * np.cos(ra) * np.sin(dec) - ry * np.sin(ra) * np.sin(dec) + rz * np.cos(dec) \
        + d1 * delta_dec
    ddec = rx * np.sin(ra) - ry * np.cos(ra) + d2 * delta_dec + b2
    dpos = np.concatenate((dra, ddec))

    return dpos


# ========================= Resolve Results =========================


def initialize_parameter_names(tran_type="1"):
    """
    Initialize parameter names based on the transformation type.

    Parameters
    ----------
    tran_type : str, optional
        The type of transformation (e.g., "1", "2", "3", "3a", "3b").
        Default is "1".

    Returns
    -------
    para_name : list of str
        List of parameter names.
    """

    if tran_type == "1":
        para_name = ["rx", "ry", "rz"]
    elif tran_type == "2":
        para_name = ["rx", "ry", "rz", "dz"]
    elif tran_type in ["3", "3a", "3b"]:
        para_name = ["rx", "ry", "rz", "d1", "d2", "dz"]
    else:
        print("Undefined tran_type")
        sys.exit(1)

    return para_name


def guess_parameter_names(pmt):
    """
    Guess parameter names based on the length of the parameter array.

    Parameters
    ----------
    pmt : array-like
        Array of parameter values.

    Returns
    -------
    para_name : list of str
        List of guessed parameter names.
    """

    N = len(pmt)

    if N == 3:
        para_name = initialize_parameter_names(tran_type="1")
    elif N == 4:
        para_name = initialize_parameter_names(tran_type="2")
    elif N == 6:
        para_name = initialize_parameter_names(tran_type="3")
    else:
        print("Could not guess the parameter names.")
        sys.exit(1)

    return para_name


def process_fit_results(output, popt, pcov, tran_type, pos_chi2_rdc):
    """
    Process the results of a fit, including calculating errors and correlations.

    Parameters
    ----------
    output : dict
        Dictionary to store the results.
    popt : array-like
        Optimized parameter values.
    pcov : array-like
        Covariance matrix of the optimized parameters.
    tran_type : str
        The type of transformation (e.g., "1", "2", "3", "3a", "3b").
    pos_chi2_rdc : float
        Reduced chi-square value for scaling errors.

    Returns
    -------
    output : dict
        Updated dictionary with processed fit results.
    """

    para_name = initialize_parameter_names(tran_type)

    # Covariance matrix -> Correlation matrix
    sig = np.sqrt(pcov.diagonal())

    # Rescale the formal error
    corr_mat = np.array([pcov[i, j] / (sig[i] * sig[j])
                         for j in range(len(sig))
                         for i in range(len(sig))])
    corr_mat.resize((len(sig), len(sig)))

    # Rescale the formal error
    sig = sig * np.sqrt(pos_chi2_rdc)

    output["pmt"] = popt
    output["sig"] = sig
    output["cor_mat"] = corr_mat

    for i, par in enumerate(para_name):
        output[par] = popt[i]
        output[par + "_err"] = sig[i]

    for i, pari in enumerate(para_name):
        for j, parj in enumerate(para_name[i + 1:]):
            output[pari + parj + "_cor"] = corr_mat[i, j]

    return output


# ========================= LSQ fitting =========================

def fit_iers_transformation(dra, ddec, ra, dec,
                            dra_err=None, ddec_err=None, dra_ddec_cor=None, flog=sys.stdout,
                            unit_deg=True, tran_type="1"):
    """
    Perform least squares fitting for IERS transformation equations.

    The transformation function considering only the rigid rotation is given by:
    d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)
    d_DE   = +r_x*sin(ra) - r_y*cos(ra)

    Parameters
    ----------
    dra/ddec : array of float
        Offset in right ascension/declination.
    ra/dec : array of float
        Right ascension/declination in radians.
    dra_err/ddec_err : array of float, optional
        Formal uncertainties of dra/ddec. Default is None.
    dra_ddec_cor : array of float, optional
        Correlation between dra and ddec. Default is None.
    flog : file-like object, optional
        Log file to output information. Default is sys.stdout.
    unit_deg : bool, optional
        Whether ra/dec are given in degrees. Default is True.
    tran_type : str, optional
        Type of transformation ("1", "2", "3a", "3b"). Default is "1".

    Returns
    -------
    output : dict
        Dictionary containing the fit results, uncertainties, and additional information.
    """

    # Degree -> radian
    if unit_deg:
        ra = np.deg2rad(ra)
        dec = np.deg2rad(dec)

    # Position vector
    pos = np.concatenate((ra, dec))
    dpos = np.concatenate((dra, ddec))
    N = len(dra)

    # Create covariance matrix
    if dra_err is not None:
        cov_mat = np.diag(np.concatenate((dra_err ** 2, ddec_err**2)))

        if dra_ddec_cor is not None:
            # Consider the correlation between dra and ddec
            dra_ddec_cov = dra_err * ddec_err * dra_ddec_cor
            for i, dra_ddec_covi in enumerate(dra_ddec_cov):
                cov_mat[i, i + N] = dra_ddec_covi
                cov_mat[i + N, i] = dra_ddec_covi

    # Select the appropriate transformation function
    if tran_type == "1":
        trans_func = rigid_rotation
    elif tran_type == "2":
        trans_func = rotation_with_declination_bias
    elif tran_type == "3a":
        trans_func = rotation_with_declination_slope_and_bias_a
    elif tran_type in ["3", "3b"]:
        trans_func = rotation_with_declination_slope_and_bias_b
    else:
        print("Undefined tran_type!")
        sys.exit(1)

    # Perform the LSQ fit
    if dra_err is None:
        popt, pcov = curve_fit(trans_func, pos, dpos)
    else:
        popt, pcov = curve_fit(trans_func, pos, dpos,
                               sigma=cov_mat, absolute_sigma=False)

    M = len(popt)

    output = {}
    # Prediction
    predict = trans_func(pos, *popt)
    output["predict_ra"] = predict[:N]
    output["predict_dec"] = predict[N:]

    # Residuals
    output["residual_ra"] = dra - output["predict_ra"]
    output["residual_dec"] = ddec - output["predict_dec"]
    rsd_ra, rsd_ddec = output["residual_ra"], output["residual_dec"]

    # Chi-squared per degree of freedom
    if dra_err is None:
        # Calculate chi2/ndof
        output["chi2_dof_ra"] = np.sum(output["residual_ra"]) / (N - M)
        output["chi2_dof_dec"] = np.sum(output["residual_dec"]) / (N - M)

        unit_wgt = np.ones_like(dra)
        zero_cov = np.zeros_like(dra)
        apr_chi2_rdc = compute_chi_squared_2d(dra, unit_wgt, ddec, unit_wgt, zero_cov,
                                              reduced=True, num_fdm=2*N-1-M)
        pos_chi2_rdc = compute_chi_squared_2d(dra, unit_wgt, ddec, unit_wgt, zero_cov,
                                              reduced=True, num_fdm=2*N-1-M)
        pos_chi2 = compute_chi_squared_2d(
            dra, unit_wgt, ddec, unit_wgt, zero_cov)

    else:
        # Calculate chi2/ndof
        output["chi2_dof_ra"] = np.sum(
            output["residual_ra"] / dra_err) / (N - M)
        output["chi2_dof_dec"] = np.sum(
            output["residual_dec"] / ddec_err) / (N - M)

        apr_chi2_rdc = compute_chi_squared_2d(dra, dra_err, ddec, ddec_err, dra_ddec_cov,
                                              reduced=True, num_fdm=2*N-1-M)
        pos_chi2_rdc = compute_chi_squared_2d(rsd_ra, dra_err, rsd_ddec, ddec_err,
                                              dra_ddec_cov, reduced=True, num_fdm=2*N-1-M)

        pos_chi2 = compute_chi_squared_2d(
            rsd_ra, dra_err, rsd_ddec, ddec_err, dra_ddec_cov)

    if flog is not None:
        print("# apriori reduced Chi-square: %10.3f\n"
              "# posteriori reduced Chi-square: %10.3f" %
              (apr_chi2_rdc, pos_chi2_rdc), file=flog)

        # Calculate the goodness-of-fit
        print("# goodness-of-fit: %10.3f" %
              compute_goodness_of_fit(2*N-1-M, pos_chi2), file=flog)

    # Rescale the formal errors and resolve results
    output = process_fit_results(output, popt, pcov, tran_type, pos_chi2_rdc)

    return output


# ========================= LSQ fitting for Astropy Table =========================

def fit_iers_transformation_for_table(data_tab, tran_type="1"):
    """
    IERS-1995 model fit for Astropy.Table.

    Parameters
    ----------
    data_tab : Astropy.table-like
        Must contain column names of ["dra", "ddec", "ra", "dec", "dra_err", "ddec_err"].
    tran_type : str
        Flag to determine which parameters to be fitted.

    Returns
    -------
    output : dict
        Results of the fit.
    """

    # Transform astropy.Column into np.array
    if "dra" in data_tab.colnames:
        dra = np.array(data_tab["dra"])
    elif "pmra" in data_tab.colnames:
        dra = np.array(data_tab["pmra"])
    else:
        print("'dra' or 'pmra' is not specified.")
        sys.exit(1)

    if "ddec" in data_tab.colnames:
        ddec = np.array(data_tab["ddec"])
    elif "pmdec" in data_tab.colnames:
        ddec = np.array(data_tab["pmdec"])
    else:
        print("'ddec' or 'pmdec' is not specified.")
        sys.exit(1)

    ra = np.array(data_tab["ra"])
    dec = np.array(data_tab["dec"])

    if "dra_err" in data_tab.colnames:
        dra_err = np.array(data_tab["dra_err"])
    elif "dra_error" in data_tab.colnames:
        dra_err = np.array(data_tab["dra_error"])
    elif "pmra_err" in data_tab.colnames:
        dra_err = np.array(data_tab["pmra_err"])
    elif "pmra_error" in data_tab.colnames:
        dra_err = np.array(data_tab["pmra_error"])
    else:
        print("'dra_err', 'dra_error', 'pmra_err', or 'pmra_error' is not specified.")
        print("Using equal weights.")
        dra_err = np.ones(len(data_tab))

    if "ddec_err" in data_tab.colnames:
        ddec_err = np.array(data_tab["ddec_err"])
    elif "ddec_error" in data_tab.colnames:
        ddec_err = np.array(data_tab["ddec_error"])
    elif "pmdec_err" in data_tab.colnames:
        ddec_err = np.array(data_tab["pmdec_err"])
    elif "pmdec_error" in data_tab.colnames:
        ddec_err = np.array(data_tab["pmdec_error"])
    else:
        print("'ddec_err', 'ddec_error', 'pmdec_err', or 'pmdec_error' is not specified.")
        print("Using equal weights.")
        ddec_err = np.ones(len(data_tab))

    if "dra_ddec_cov" in data_tab.colnames:
        dra_ddc_cov = np.array(data_tab["dra_ddec_cov"])
        dra_ddc_cor = dra_ddc_cov / dra_err / ddec_err
    elif "dra_ddec_cor" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["dra_ddec_cor"])
    elif "pmra_pmdec_corr" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_corr"])
    elif "pmra_pmdec_cor" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_cor"])
    else:
        print("'dra_ddec_cov', 'dra_ddec_cor', 'pmra_pmdec_corr', or 'pmra_pmdec_cor' is not specified.")
        print("Considering the covariance matrix as diagonal.")
        dra_ddc_cor = None

    # Perform the LSQ fitting
    output = fit_iers_transformation(dra, ddec, ra, dec, dra_err, ddec_err, dra_ddc_cor,
                                     unit_deg=True, tran_type=tran_type, flog=None)

    return output


def fit_iers_transformation_type1(data_tab):
    """
    Perform IERS transformation fitting for type 1.
    """
    return fit_iers_transformation_for_table(data_tab, tran_type="1")


def fit_iers_transformation_type2(data_tab):
    """
    Perform IERS transformation fitting for type 2.
    """
    return fit_iers_transformation_for_table(data_tab, tran_type="2")


def fit_iers_transformation_type3(data_tab):
    """
    Perform IERS transformation fitting for type 3.
    """
    return fit_iers_transformation_for_table(data_tab, tran_type="3")


def display_transformation_model_info(tran_type="1"):
    """Display the transformation model information based on the tran_type."""

    if tran_type == "1":
        print("\nThe transformation function is given as:\n"
              "d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec),\n"
              "d_DE   = +r_x*sin(ra) - r_y*cos(ra).\n"
              "The unknowns are the rotation angles around the X-, Y-, and Z-axis, "
              "which are r_x, r_y, and r_z.")

    elif tran_type == "2":
        print("\nThe transformation function is given as:\n"
              "d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec),\n"
              "d_DE   = +r_x*sin(ra) - r_y*cos(ra) + dz.\n"
              "The unknowns are the rotation angles around the X-, Y-, and Z-axis, "
              "which are r_x, r_y, and r_z, and dz is the declination bias.")

    elif tran_type == "3a":
        print("\nThe transformation function is given as:\n"
              "d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)\n"
              "         + D_1*(dec-DE0)*cos(dec),\n"
              "d_DE   = +r_x*sin(ra) - r_y*cos(ra)\n"
              "         + D_2*(dec-DE0) + B_2.\n"
              "The unknowns are the rotation angles around the X-, Y-, and Z-axis, "
              "which are r_x, r_y, and r_z, B_2 is the declination bias, and D_1 and D_2 are the slopes.\n"
              "The reference declination is chosen as DE0 = 0.")

    elif tran_type in ["3", "3b"]:
        print("\nThe transformation function is given as:\n"
              "d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)\n"
              "         + D_1*(dec-DE0),\n"
              "d_DE   = +r_x*sin(ra) - r_y*cos(ra)\n"
              "         + D_2*(dec-DE0) + B_2.\n"
              "The unknowns are the rotation angles around the X-, Y-, and Z-axis, "
              "which are r_x, r_y, and r_z, B_2 is the declination bias, and D_1 and D_2 are the slopes.\n"
              "The reference declination is chosen as DE0 = 0.")

    else:
        print("Undefined tran_type!")
        sys.exit(1)


def display_correlation_matrix(names, parcorrs, deci_digit=2, included_one=True, opt=sys.stdout):
    """Display the correlation coefficient matrix.

    Parameters
    ----------
    names : array
        Names or labels of the parameters.
    parcorrs : array of N * N
        Matrix of correlation coefficients.
    deci_digit : int
        Number of decimal digits to display. Only 1 and 2 are supported. Default is 2.
    included_one : boolean
        Whether to include the correlation between the same parameters (value = 1).
        Default is True.
    opt : file handling
        File handle where the output will be printed. Defaults to stdout.
    """

    parnb = len(names)

    print("\nCorrelation Coefficient Matrix", file=opt)
    print("---------------------------------------------------------", file=opt)

    if isinstance(parcorrs, (np.matrix, np.mat)):
        parcorrs = np.array(parcorrs)

    if deci_digit == 1:
        if included_one:
            print(("  %4s" * (parnb + 1)) % ("    ", *names), file=opt)
            for i, pmt_namei in enumerate(names):
                line_fmt = "  %4s" + "  %+4.1f" * (i + 1)
                print(line_fmt % (pmt_namei, *parcorrs[i, :i+1]), file=opt)
        else:
            print(("  %4s" * parnb) % ("    ", *names[:-1]), file=opt)
            for i in range(1, parnb):
                line_fmt = "  %4s" + "  %+4.1f" * i
                print(line_fmt % (names[i], *parcorrs[i, :i]), file=opt)

    elif deci_digit == 2:
        if included_one:
            print(("  %5s" * (parnb + 1)) % ("    ", *names), file=opt)
            for i, pmt_namei in enumerate(names):
                line_fmt = "  %5s" + "  %+5.2f" * (i + 1)
                print(line_fmt % (pmt_namei, *parcorrs[i, :i+1]), file=opt)
        else:
            print(("  %5s" * parnb) % ("    ", *names[:-1]), file=opt)
            for i in range(1, parnb):
                line_fmt = "  %5s" + "  %+5.2f" * i
                print(line_fmt % (names[i], *parcorrs[i, :i]), file=opt)
    else:
        raise ValueError("Only 1 or 2 decimal digits are supported!")


def display_iers1995_correlation(parcorrs, parnames):
    """Display the correlation coefficient matrix for IERS-1995 parameters.

    Parameters
    ----------
    parcorrs : array of N * N
        Matrix of correlation coefficients.
    parnames : array of string
        Names or labels of the parameters.
    """

    parnb = len(parnames)

    if parcorrs.shape != (parnb, parnb):
        raise ValueError(
            f"The shape of the correlation matrix should be ({parnb}, {parnb})!")

    display_correlation_matrix(
        parnames, parcorrs, deci_digit=1, included_one=True, opt=sys.stdout)


def display_iers1995_results(pmts, sigs, parcorrs, tran_type="1", opt=sys.stdout, fmt="%5.0f"):
    """Display estimates and corresponding formal errors of IERS-1995 parameters.

    Parameters
    ----------
    pmts : array of float
        Estimates of parameters.
    sigs : array of float
        Formal errors of estimates.
    parcorrs : array of N * N
        Matrix of correlation coefficients.
    tran_type : string
        The type of transformation model used.
    opt : file handling
        File handle where the output will be printed. Defaults to stdout.
    fmt : string
        Specifier for the output format. Default is "%5.0f".
    """

    parnames = guess_parameter_names(pmts)

    tpmt = Table([parnames, pmts, sigs], names=[
                 "Parameter", "Estimate", "Error"])
    tpmt["Estimate"].format = fmt
    tpmt["Error"].format = fmt
    tpmt["Estimate"].unit = u.uas
    tpmt["Error"].unit = u.uas

    print(tpmt, file=opt)

    display_iers1995_correlation(parcorrs, parnames)


def display_iers1995_results_from_dict(output, parnames=None, tran_type="1", opt=sys.stdout, fmt="%5.0f"):
    """Display estimates and corresponding formal errors of IERS-1995 parameters from a dictionary.

    Parameters
    ----------
    output : dict
        Dictionary containing the results of the fit.
    parnames : array of string, optional
        Names or labels of the parameters. If not provided, they are guessed.
    tran_type : string
        The type of transformation model used.
    opt : file handling
        File handle where the output will be printed. Defaults to stdout.
    fmt : string
        Specifier for the output format. Default is "%5.0f".
    """

    pmts = output["pmt"]
    sigs = output["sig"]
    parcorrs = output["cor_mat"]

    parnames = guess_parameter_names(pmts) if parnames is None else parnames

    tvsh = Table([parnames, pmts, sigs], names=[
                 "Parameter", "Estimate", "Error"])
    tvsh["Estimate"].format = fmt
    tvsh["Error"].format = fmt
    tvsh["Estimate"].unit = u.uas
    tvsh["Error"].unit = u.uas

    display_transformation_model_info(tran_type)
    print("\n", file=opt)
    print(tvsh, file=opt)
    display_iers1995_correlation(parcorrs, parnames)


def main():
    print("Hello, World!")
    # You can call other functions or write your main program logic here.


if __name__ == "__main__":
    main()
