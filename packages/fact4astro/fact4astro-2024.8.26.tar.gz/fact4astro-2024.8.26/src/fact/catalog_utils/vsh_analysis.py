#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: VSH_analysis.py
"""
Module for performing Vector Spherical Harmonics (VSH) analysis on positional offsets.

Author: Neo (liuniu@smail.nju.edu.cn)
Created on: Thu Jan  4 12:17:39 2018
Last Modified: [Date of last modification]

History:
---------
N. Liu, 10 Feb 2018: Updated input parameters of function 'vsh_analysis', replacing 'datafile' with 'pos_offset'.
N. Liu, 12 Feb 2018: Added 'X_a', 'X_d', 'X' to input variables of 'catalog_comparison_VSH', 'VSH_analysis', 'apply_condition'.
                     Modified 'print_outlier' to include normalized separation information.
"""


# Set up logging
from astropy.table import Table
import logging
import numpy as np

from .analysis_tools import compute_chi_squared_2d, compute_wrms, compute_weighted_mean, compute_goodness_of_fit
from .data_cleaning import eliminate_outliers_by_sigma, eliminate_outliers_by_criteria
from .catalog_operations import extract_data_from_table
from .error_ellipse import calculate_covariance_matrix
from .vsh_utils import generate_jacobian_matrix_vsh_deg01, generate_jacobian_matrix_vsh_deg02, calculate_normal_matrix, calculate_residuals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------  FUNCTIONS -----------------------------


def log_initial_statistics(dra, ddec, dra_err, ddec_err, log_file):
    """Log initial statistics for RA and Dec residuals."""
    mean_ra = compute_weighted_mean(dra)
    rms_ra = compute_wrms(dra)
    wrms_ra = compute_wrms(dra, dra_err)
    std_ra = np.std(dra)
    mean_dec = compute_weighted_mean(ddec)
    rms_dec = compute_wrms(ddec)
    wrms_dec = compute_wrms(ddec, ddec_err)
    std_dec = np.std(ddec)

    print("# Initial statistics (weighted)\n"
          "# Mean RA: %10.3f\n"
          "# RMS RA: %10.3f\n"
          "# WRMS RA: %10.3f\n"
          "# Std RA: %10.3f\n"
          "# Mean Dec: %10.3f\n"
          "# RMS Dec: %10.3f\n"
          "# WRMS Dec: %10.3f\n"
          "# Std Dec: %10.3f" %
          (mean_ra, rms_ra, wrms_ra, std_ra, mean_dec, rms_dec, wrms_dec, std_dec), file=log_file)


def log_apriori_chi_square(dra, ddec, dra_err, ddec_err, cov, log_file):
    """Log apriori reduced Chi-square."""
    apr_chi2 = compute_chi_squared_2d(
        dra, dra_err, ddec, ddec_err, cov, reduced=True)
    print("# Apriori reduced Chi-square: %10.3f" % apr_chi2, file=log_file)


def log_post_fit_statistics(dra_residuals, ddec_residuals, dra_err, ddec_err, cov, log_file):
    """Log post-fit statistics including residuals, chi-square, and goodness-of-fit."""
    mean_ra = compute_weighted_mean(dra_residuals)
    rms_ra = compute_wrms(dra_residuals)
    wrms_ra = compute_wrms(dra_residuals, dra_err)
    std_ra = np.std(dra_residuals)
    mean_dec = compute_weighted_mean(ddec_residuals)
    rms_dec = compute_wrms(ddec_residuals)
    wrms_dec = compute_wrms(ddec_residuals, ddec_err)
    std_dec = np.std(ddec_residuals)

    print("# Post-fit statistics (weighted)\n"
          "# Mean RA: %10.3f\n"
          "# RMS RA: %10.3f\n"
          "# WRMS RA: %10.3f\n"
          "# Std RA: %10.3f\n"
          "# Mean Dec: %10.3f\n"
          "# RMS Dec: %10.3f\n"
          "# WRMS Dec: %10.3f\n"
          "# Std Dec: %10.3f" %
          (mean_ra, rms_ra, wrms_ra, std_ra, mean_dec, rms_dec, wrms_dec, std_dec), file=log_file)

    M = 6  # Number of parameters (this should be generalized)
    post_chi2_rdc = compute_chi_squared_2d(dra_residuals, dra_err, ddec_residuals,
                                           ddec_err, cov, reduced=True, num_fdm=2 * dra_residuals.size - 1 - M)
    print("# Post-fit reduced Chi-square: %10.3f" %
          post_chi2_rdc, file=log_file)

    post_chi2 = compute_chi_squared_2d(dra_residuals, dra_err,
                                       ddec_residuals, ddec_err, cov)
    print("# Goodness-of-fit: %10.3f" %
          compute_goodness_of_fit(2 * dra_residuals.size - 1 - M, post_chi2), file=log_file)

    return post_chi2_rdc


def solve_vsh(dra, ddec, dra_err, ddec_err, ra, dec, cov=None, fit_type="full", l_max=1, max_num=1000):
    """Solve the VSH function for glide and rotation parameters.

    Parameters
    ----------
    dra : array of float
        Observed R.A. (*cos(Dec.)) differences in microarcseconds.
    ddec : array of float
        Observed Declination differences in microarcseconds.
    dra_err : array of float
        Formal uncertainty of R.A. differences in microarcseconds.
    ddec_err : array of float
        Formal uncertainty of Declination differences in microarcseconds.
    ra : array of float
        Right ascension in radians.
    dec : array of float
        Declination in radians.
    cov : array of float, optional
        Covariance between dra and ddec in microarcseconds^2. Default is None.
    fit_type : string, optional
        Determines which parameters to fit: "full" (default), "rotation", or "glide".
    l_max : int, optional
        Maximum degree of the VSH function, default is 1.
    max_num : int, optional
        Maximum number of calculations for matrix inversion. Default is 1000.

    Returns
    ----------
    parameters : array of float
        Estimated parameters based on the VSH model.
        l_max = 1 -> (d1, d2, d3, r1, r2, r3)
        l_max = 2 -> (d1, d2, d3, r1, r2, r3, ER_22, EI_22, ER_21, EI_21, E_20, MR_22, MI_22, MR_21, MI_21, M_20)
    uncertainties : array of float
        Uncertainty of each estimated parameter in microarcseconds.
    correlation_matrix : matrix
        Correlation matrix of the estimated parameters.
    """

    if l_max == 1:
        jac_mat_func = generate_jacobian_matrix_vsh_deg01
    elif l_max == 2:
        jac_mat_func = generate_jacobian_matrix_vsh_deg02
    else:
        raise ValueError("l_max >= 2 is not supported.")

    if dra.size > max_num:
        div = dra.size // max_num
        rem = dra.size % max_num

        if cov is None:
            A, b = calculate_normal_matrix(dra[:rem], ddec[:rem],
                                           dra_err[:rem], ddec_err[:rem],
                                           ra[:rem], dec[:rem],
                                           cov, fit_type, jac_mat_func)
        else:
            A, b = calculate_normal_matrix(dra[:rem], ddec[:rem],
                                           dra_err[:rem], ddec_err[:rem],
                                           ra[:rem], dec[:rem],
                                           cov[:rem], fit_type, jac_mat_func)

        for i in range(div):
            start = rem + i * max_num
            end = start + max_num

            if cov is None:
                An, bn = calculate_normal_matrix(dra[start:end], ddec[start:end],
                                                 dra_err[start:end], ddec_err[start:end],
                                                 ra[start:end], dec[start:end],
                                                 cov, fit_type, jac_mat_func)
            else:
                An, bn = calculate_normal_matrix(dra[start:end], ddec[start:end],
                                                 dra_err[start:end], ddec_err[start:end],
                                                 ra[start:end], dec[start:end],
                                                 cov[start:end], fit_type, jac_mat_func)
            A += An
            b += bn
    else:
        A, b = calculate_normal_matrix(dra, ddec, dra_err, ddec_err, ra, dec,
                                       cov, fit_type, jac_mat_func)

    # Solve the equations.
    parameters = np.linalg.solve(A, b)

    # Covariance matrix.
    pcov = np.linalg.inv(A)
    uncertainties = np.sqrt(pcov.diagonal())

    # Correlation matrix.
    correlation_matrix = np.array([pcov[i, j] / uncertainties[i] / uncertainties[j]
                                   for j in range(len(parameters))
                                   for i in range(len(parameters))]).reshape(len(parameters), len(parameters))

    return parameters, uncertainties, correlation_matrix


def fit_vsh(dra, ddec, ra, dec, dra_err=None, ddec_err=None, cov=None, log_file=None,
            elimination_criteria="sigma", threshold=3.0, ang_sep=None, X=None, fit_type="full",
            return_aux=False, l_max=1):
    """Main function to perform VSH fitting with optional outlier elimination."""

    # Log initial statistics and apriori chi-square
    if log_file is not None:
        log_initial_statistics(dra, ddec, dra_err, ddec_err, log_file)
        log_apriori_chi_square(dra, ddec, dra_err, ddec_err, cov, log_file)

    # Outlier elimination and fitting
    if elimination_criteria in [None, "none"]:
        params, uncertainties, correlation_matrix = solve_vsh(
            dra, ddec, dra_err, ddec_err, ra, dec, cov, fit_type, l_max)
        good_indices = np.arange(dra.size)

    elif elimination_criteria == "sigma":
        dra_n, ddec_n, dra_err_n, ddec_err_n, cov_n, ra_n, dec_n, good_indices = eliminate_outliers_by_sigma(
            dra, ddec, dra_err, ddec_err, ra, dec, cov, fit_type, l_max, threshold, log_file)

        params, uncertainties, correlation_matrix = solve_vsh(
            dra_n, ddec_n, dra_err_n, ddec_err_n, ra_n, dec_n, cov_n, fit_type, l_max)
    else:
        dra_n, ddec_n, dra_err_n, ddec_err_n, cov_n, ra_n, dec_n, good_indices = eliminate_outliers_by_criteria(
            dra, ddec, dra_err, ddec_err, ra, dec, cov, ang_sep, X, elimination_criteria, threshold, fit_type, l_max, log_file)
        params, uncertainties, correlation_matrix = solve_vsh(
            dra_n, ddec_n, dra_err_n, ddec_err_n, ra_n, dec_n, cov_n, fit_type, l_max)

    # Calculate post-fit residuals
    dra_residuals, ddec_residuals = calculate_residuals(
        dra, ddec, ra, dec, params, fit_type, l_max)

    # Log post-fit statistics
    if log_file is not None:
        post_chi2_rdc = log_post_fit_statistics(
            dra_residuals, ddec_residuals, dra_err, ddec_err, cov, log_file)

    # Rescale the formal errors
    uncertainties *= np.sqrt(post_chi2_rdc)

    # Return the result
    if return_aux:
        return params, uncertainties, correlation_matrix, good_indices, dra_residuals, ddec_residuals
    else:
        return params, uncertainties, correlation_matrix


def vsh_fit_4_table(data_tab, fit_type="full", return_aux=False, l_max=1):
    """VSH fit for Astropy Table."""
    dra, ddec, dra_err, ddec_err, ra, dec = extract_data_from_table(data_tab)
    dra_ddec_cov = calculate_covariance_matrix(data_tab, dra_err, ddec_err)

    output_data = fit_vsh(
        dra, ddec, ra, dec,
        e_dRA=dra_err, e_dDE=ddec_err,
        cov=dra_ddec_cov,
        elim_flag="nor_ang",
        ang_sep=np.array(data_tab["ang_sep"]),
        X=np.array(data_tab["nor_sep"]),
        fit_type=fit_type,
        return_aux=return_aux,
        l_max=l_max
    )

    output = {
        "pmt": output_data[0],
        "sig": output_data[1],
        "cor_mat": output_data[2],
    }

    if return_aux:
        output.update({
            "outlier_index": output_data[3],
            "dra_residual": output_data[4],
            "ddec_residual": output_data[5],
        })

    return output


# ----------------------------- MAIN FUNCTION -----------------------------
def main():
    pass  # Add a test or demonstration of the module's functionality here


if __name__ == "__main__":
    main()
