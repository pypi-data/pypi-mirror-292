#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: vsh_utils.py
"""
Created on Mon 26 Aug 2024 09:07:21 PM CST

@author: Neo(niu.liu@nju.edu.cn)
"""

import sys
import numpy as np
from astropy.table import Table
from astropy import units as u


def generate_jacobian_matrix_vsh_deg01(ra, dec, component="full"):
    """Generate the Jacobian matrix for the first-degree VSH model.

    Parameters
    ----------
    ra : array of float
        Right ascension in radians.
    dec : array of float
        Declination in radians.
    component : str, optional
        Specifies which part of the Jacobian matrix to generate:
        "full" - Generate the full matrix (default).
        "rotation" - Generate only the rotation part.
        "glide" - Generate only the glide part.

    Returns
    ----------
    jacobian_matrix : numpy.ndarray
        The Jacobian matrix.
    jacobian_matrix_transpose : numpy.ndarray
        The transpose of the Jacobian matrix.
    """

    # Define the partial derivatives based on the component type
    if component == "full":
        # RA derivatives for glide and rotation
        d1_ra = -np.sin(ra)
        d2_ra = np.cos(ra)
        d3_ra = np.zeros_like(ra)
        r1_ra = -np.cos(ra) * np.sin(dec)
        r2_ra = -np.sin(ra) * np.sin(dec)
        r3_ra = np.cos(dec)

        # Dec derivatives for glide and rotation
        d1_dec = -np.cos(ra) * np.sin(dec)
        d2_dec = -np.sin(ra) * np.sin(dec)
        d3_dec = np.cos(dec)
        r1_dec = np.sin(ra)
        r2_dec = -np.cos(ra)
        r3_dec = np.zeros_like(ra)

        # Concatenate the partial derivatives
        jacobian_matrix_transpose = np.vstack([
            np.concatenate((d1_ra, d1_dec)),
            np.concatenate((d2_ra, d2_dec)),
            np.concatenate((d3_ra, d3_dec)),
            np.concatenate((r1_ra, r1_dec)),
            np.concatenate((r2_ra, r2_dec)),
            np.concatenate((r3_ra, r3_dec))
        ])

    elif component == "rotation":
        r1_ra = -np.cos(ra) * np.sin(dec)
        r2_ra = -np.sin(ra) * np.sin(dec)
        r3_ra = np.cos(dec)

        r1_dec = np.sin(ra)
        r2_dec = -np.cos(ra)
        r3_dec = np.zeros_like(ra)

        jacobian_matrix_transpose = np.vstack([
            np.concatenate((r1_ra, r1_dec)),
            np.concatenate((r2_ra, r2_dec)),
            np.concatenate((r3_ra, r3_dec))
        ])

    elif component == "glide":
        d1_ra = -np.sin(ra)
        d2_ra = np.cos(ra)
        d3_ra = np.zeros_like(ra)

        d1_dec = -np.cos(ra) * np.sin(dec)
        d2_dec = -np.sin(ra) * np.sin(dec)
        d3_dec = np.cos(dec)

        jacobian_matrix_transpose = np.vstack([
            np.concatenate((d1_ra, d1_dec)),
            np.concatenate((d2_ra, d2_dec)),
            np.concatenate((d3_ra, d3_dec))
        ])
    else:
        raise ValueError(
            "Invalid component type. Choose 'full', 'rotation', or 'glide'.")

    # Transpose the Jacobian matrix
    jacobian_matrix = jacobian_matrix_transpose.T

    return jacobian_matrix, jacobian_matrix_transpose


def generate_jacobian_matrix_vsh_deg02(ra, dec, component="full"):
    """Generate the Jacobian matrix for the second-degree VSH model.

    Parameters
    ----------
    ra : array of float
        Right ascension in radians.
    dec : array of float
        Declination in radians.
    component : str, optional
        Specifies which part of the Jacobian matrix to generate:
        "full" - Generate the full matrix (default).
        "rotation" - Generate only the rotation part.
        "glide" - Generate only the glide part.

    Returns
    ----------
    jacobian_matrix : numpy.ndarray
        The Jacobian matrix.
    jacobian_matrix_transpose : numpy.ndarray
        The transpose of the Jacobian matrix.
    """

    # Partial derivatives for RA
    par1_11ER = -np.sin(ra)
    par1_11EI = np.cos(ra)
    par1_10E = np.zeros_like(ra)
    par1_11MR = -np.cos(ra) * np.sin(dec)
    par1_11MI = -np.sin(ra) * np.sin(dec)
    par1_10M = np.cos(dec)

    par1_22ER = -2 * np.sin(2 * ra) * np.cos(dec)
    par1_22EI = -2 * np.cos(2 * ra) * np.cos(dec)
    par1_21ER = np.sin(ra) * np.sin(dec)
    par1_21EI = np.cos(ra) * np.sin(dec)
    par1_20E = np.zeros_like(ra)
    par1_22MR = -np.cos(2 * ra) * np.sin(2 * dec)
    par1_22MI = np.sin(2 * ra) * np.sin(2 * dec)
    par1_21MR = -np.cos(ra) * np.cos(2 * dec)
    par1_21MI = np.sin(ra) * np.cos(2 * dec)
    par1_20M = np.sin(2 * dec)

    # Partial derivatives for Dec
    par2_11ER = par1_11MR
    par2_11EI = par1_11MI
    par2_10E = par1_10M
    par2_11MR = -par1_11ER
    par2_11MI = -par1_11EI
    par2_10M = -par1_10E

    par2_22ER = par1_22MR
    par2_22EI = par1_22MI
    par2_21ER = par1_21MR
    par2_21EI = par1_21MI
    par2_20E = par1_20M
    par2_22MR = -par1_22ER
    par2_22MI = -par1_22EI
    par2_21MR = -par1_21ER
    par2_21MI = -par1_21EI
    par2_20M = -par1_20E

    if component == "full":
        # Concatenate all components
        jacobian_matrix_transpose = np.vstack([
            np.concatenate((par1_11ER, par2_11ER)),
            np.concatenate((par1_11EI, par2_11EI)),
            np.concatenate((par1_10E, par2_10E)),
            np.concatenate((par1_11MR, par2_11MR)),
            np.concatenate((par1_11MI, par2_11MI)),
            np.concatenate((par1_10M, par2_10M)),
            np.concatenate((par1_22ER, par2_22ER)),
            np.concatenate((par1_22EI, par2_22EI)),
            np.concatenate((par1_21ER, par2_21ER)),
            np.concatenate((par1_21EI, par2_21EI)),
            np.concatenate((par1_20E, par2_20E)),
            np.concatenate((par1_22MR, par2_22MR)),
            np.concatenate((par1_22MI, par2_22MI)),
            np.concatenate((par1_21MR, par2_21MR)),
            np.concatenate((par1_21MI, par2_21MI)),
            np.concatenate((par1_20M, par2_20M))
        ])

    elif component == "rotation":
        # Concatenate only rotation components
        jacobian_matrix_transpose = np.vstack([
            np.concatenate((par1_11MR, par2_11MR)),
            np.concatenate((par1_11MI, par2_11MI)),
            np.concatenate((par1_10M, par2_10M)),
            np.concatenate((par1_22MR, par2_22MR)),
            np.concatenate((par1_22MI, par2_22MI)),
            np.concatenate((par1_21MR, par2_21MR)),
            np.concatenate((par1_21MI, par2_21MI)),
            np.concatenate((par1_20M, par2_20M))
        ])

    elif component == "glide":
        # Concatenate only glide components
        jacobian_matrix_transpose = np.vstack([
            np.concatenate((par1_11ER, par2_11ER)),
            np.concatenate((par1_11EI, par2_11EI)),
            np.concatenate((par1_10E, par2_10E)),
            np.concatenate((par1_22ER, par2_22ER)),
            np.concatenate((par1_22EI, par2_22EI)),
            np.concatenate((par1_21ER, par2_21ER)),
            np.concatenate((par1_21EI, par2_21EI)),
            np.concatenate((par1_20E, par2_20E))
        ])

    else:
        raise ValueError(
            "Invalid component type. Choose 'full', 'rotation', or 'glide'.")

    jacobian_matrix = jacobian_matrix_transpose.T

    return jacobian_matrix, jacobian_matrix_transpose


def calculate_vsh_deg1(ra, dec, params, fit_type="full"):
    """Calculate VSH function of the first degree.

    Parameters
    ----------
    ra : array of float
        Right ascension in radians.
    dec : array of float
        Declination in radians.
    params : list or array of float
        Parameters for rotation and glide components.
    fit_type : string, optional
        Specifies which components to calculate: 
        "full" (default), "rotation", or "glide".

    Returns
    ----------
    dra : array of float
        R.A.(*cos(Dec.)) differences in microarcseconds.
    ddec : array of float
        Declination differences in microarcseconds.
    """
    if fit_type == "full":
        g1, g2, g3, r1, r2, r3 = params
        dra = (-r1 * np.cos(ra) * np.sin(dec) - r2 * np.sin(ra) * np.sin(dec) +
               r3 * np.cos(dec) - g1 * np.sin(ra) + g2 * np.cos(ra))
        ddec = (r1 * np.sin(ra) - r2 * np.cos(ra) -
                g1 * np.cos(ra) * np.sin(dec) - g2 * np.sin(ra) * np.sin(dec) +
                g3 * np.cos(dec))
    elif fit_type == "rotation":
        r1, r2, r3 = params
        dra = (-r1 * np.cos(ra) * np.sin(dec) - r2 * np.sin(ra) * np.sin(dec) +
               r3 * np.cos(dec))
        ddec = (r1 * np.sin(ra) - r2 * np.cos(ra))
    elif fit_type == "glide":
        g1, g2, g3 = params
        dra = (-g1 * np.sin(ra) + g2 * np.cos(ra))
        ddec = (-g1 * np.cos(ra) * np.sin(dec) - g2 * np.sin(ra) * np.sin(dec) +
                g3 * np.cos(dec))
    else:
        raise ValueError("Invalid fit_type in 'calculate_vsh_deg1' function.")

    return dra, ddec


def calculate_vsh_deg2_component(ra, dec, params, fit_type="full"):
    """Calculate VSH function of the second degree.

    Parameters
    ----------
    ra : array of float
        Right ascension in radians.
    dec : array of float
        Declination in radians.
    params : list or array of float
        Parameters for quadrupolar components.
    fit_type : string, optional
        Specifies which components to calculate: 
        "full" (default), "rotation", or "glide".

    Returns
    ----------
    dra : array of float
        R.A.(*cos(Dec.)) differences in microarcseconds.
    ddec : array of float
        Declination differences in microarcseconds.
    """
    if fit_type == "full":
        ER_22, EI_22, ER_21, EI_21, E_20, MR_22, MI_22, MR_21, MI_21, M_20 = params
        dra = (M_20 * np.sin(2 * dec) -
               (MR_21 * np.cos(ra) - MI_21 * np.sin(ra)) * np.cos(2 * dec) +
               (ER_21 * np.sin(ra) + EI_21 * np.cos(ra)) * np.sin(dec) -
               (MR_22 * np.cos(2 * ra) - MI_22 * np.sin(2 * ra)) * np.sin(2 * dec) -
               2 * (ER_22 * np.sin(2 * ra) + EI_22 * np.cos(2 * ra)) * np.cos(dec))
        ddec = (E_20 * np.sin(2 * dec) -
                (MR_21 * np.sin(ra) + MI_21 * np.cos(ra)) * np.sin(dec) -
                (ER_21 * np.cos(ra) - EI_21 * np.sin(ra)) * np.cos(2 * dec) +
                2 * (MR_22 * np.sin(2 * ra) + MI_22 * np.cos(2 * ra)) * np.cos(dec) -
                (ER_22 * np.cos(2 * ra) - EI_22 * np.sin(2 * ra)) * np.sin(2 * dec))
    elif fit_type == "glide":
        ER_22, EI_22, ER_21, EI_21, E_20 = params
        dra = ((ER_21 * np.sin(ra) + EI_21 * np.cos(ra)) * np.sin(dec) -
               2 * (ER_22 * np.sin(2 * ra) + EI_22 * np.cos(2 * ra)) * np.cos(dec))
        ddec = (E_20 * np.sin(2 * dec) -
                (ER_21 * np.cos(ra) - EI_21 * np.sin(ra)) * np.cos(2 * dec) -
                (ER_22 * np.cos(2 * ra) - EI_22 * np.sin(2 * ra)) * np.sin(2 * dec))
    elif fit_type == "rotation":
        MR_22, MI_22, MR_21, MI_21, M_20 = params
        dra = (M_20 * np.sin(2 * dec) -
               (MR_21 * np.cos(ra) - MI_21 * np.sin(ra)) * np.cos(2 * dec) -
               (MR_22 * np.cos(2 * ra) - MI_22 * np.sin(2 * ra)) * np.sin(2 * dec))
        ddec = (-(MR_21 * np.sin(ra) + MI_21 * np.cos(ra)) * np.sin(dec) +
                2 * (MR_22 * np.sin(2 * ra) + MI_22 * np.cos(2 * ra)) * np.cos(dec))
    else:
        raise ValueError(
            "Invalid fit_type in 'calculate_vsh_deg2_component' function.")

    return dra, ddec


def calculate_vsh_deg2(ra, dec, params, fit_type="full"):
    """Calculate the combined VSH function of the first and second degree.

    Parameters
    ----------
    ra : array of float
        Right ascension in radians.
    dec : array of float
        Declination in radians.
    params : list or array of float
        Parameters for both first and second degree VSH components.
    fit_type : string, optional
        Specifies which components to calculate: 
        "full" (default), "rotation", or "glide".

    Returns
    ----------
    dra : array of float
        R.A.(*cos(Dec.)) differences in microarcseconds.
    ddec : array of float
        Declination differences in microarcseconds.
    """
    dra1, ddec1 = calculate_vsh_deg1(ra, dec, params[:6], fit_type)
    dra2, ddec2 = calculate_vsh_deg2_component(ra, dec, params[6:], fit_type)

    return dra1 + dra2, ddec1 + ddec2


def calculate_weight_matrix(ra_errors, dec_errors, covariance=None):
    """Generate the weight matrix for least squares fitting.

    Parameters
    ----------
    ra_errors : array of float
        Formal uncertainties of RA (*cos(Dec.)) in microarcseconds.
    dec_errors : array of float
        Formal uncertainties of Dec. in microarcseconds.
    covariance : array of float, optional
        Covariance between RA and Dec. in square microarcseconds. Default is None.

    Returns
    ----------
    weight_matrix : ndarray
        The weight matrix to be used in least squares fitting.
    """

    # Concatenate RA and Dec errors
    errors = np.concatenate((ra_errors, dec_errors), axis=0)

    # Create the covariance matrix
    cov_matrix = np.diag(errors**2)

    if covariance is not None:
        # Include the off-diagonal covariance elements
        num = ra_errors.size
        for i, cov in enumerate(covariance):
            cov_matrix[i, i + num] = cov
            cov_matrix[i + num, i] = cov

    # Invert the covariance matrix to obtain the weight matrix
    weight_matrix = np.linalg.inv(cov_matrix)

    return weight_matrix


def calculate_normal_matrix(ra, dec, dra, ddec, ra_errors, dec_errors, covariance=None,
                            fit_type="full", jacobian_function=None):
    """Calculate the normal matrix for least squares fitting.

    Parameters
    ----------
    ra : array of float
        Right ascension in radians.
    dec : array of float
        Declination in radians.
    dra : array of float
        R.A. (*cos(Dec.)) differences in microarcseconds.
    ddec : array of float
        Declination differences in microarcseconds.
    ra_errors : array of float
        Formal uncertainties of R.A. (*cos(Dec.)) in microarcseconds.
    dec_errors : array of float
        Formal uncertainties of Declination in microarcseconds.
    covariance : array of float, optional
        Covariance between R.A. and Declination in square microarcseconds. Default is None.
    fit_type : string, optional
        Determines which parameters to fit: "full" (default), "rotation", or "glide".
    jacobian_function : callable
        Function to calculate the Jacobian matrix.

    Returns
    ----------
    A : ndarray
        Normal matrix.
    b : ndarray
        Observational matrix.
    """

    if jacobian_function is None:
        raise ValueError(
            "The Jacobian matrix calculation function must be provided.")

    # Calculate the Jacobian matrix and its transpose
    jacobian_matrix, jacobian_transpose = jacobian_function(ra, dec, fit_type)

    # Calculate the weight matrix
    weight_matrix = calculate_weight_matrix(ra_errors, dec_errors, covariance)

    # Calculate the normal matrix A and observational matrix b
    A = np.dot(np.dot(jacobian_transpose, weight_matrix), jacobian_matrix)
    positional_differences = np.concatenate((dra, ddec), axis=0)
    b = np.dot(np.dot(jacobian_transpose, weight_matrix),
               positional_differences)

    return A, b


def calculate_residuals(dra, ddec, ra, dec, parameters, fit_type="full", l_max=1):
    """Calculate the residuals of RA/Dec differences.

    Parameters
    ----------
    dra : array of float
        Observed R.A. (*cos(Dec.)) differences in microarcseconds.
    ddec : array of float
        Observed Declination differences in microarcseconds.
    ra : array of float
        Right ascension in radians.
    dec : array of float
        Declination in radians.
    parameters : array of float
        Estimated parameters for rotation and glide.
    fit_type : string, optional
        Determines which parameters to fit: "full" (default), "rotation", or "glide".
    l_max : int, optional
        Maximum degree of the VSH function, default is 1.

    Returns
    ----------
    residuals_ra : array of float
        Residuals for R.A. (*cos(Dec.)) in microarcseconds.
    residuals_dec : array of float
        Residuals for Declination in microarcseconds.
    """

    if l_max == 1:
        vsh_function = calculate_vsh_deg1
    elif l_max == 2:
        vsh_function = calculate_vsh_deg2
    else:
        raise ValueError("l_max >= 2 is not supported.")

    # Calculate the theoretical values using the VSH function
    theoretical_dra, theoretical_ddec = vsh_function(
        ra, dec, parameters, fit_type)

    # Calculate the residuals (Observed - Theoretical)
    residuals_ra = dra - theoretical_dra
    residuals_dec = ddec - theoretical_ddec

    return residuals_ra, residuals_dec


def init_par_names(parnb):
    """Initialize the names of parameters if they are not given.

    Parameters
    ----------
    parnb : int
        Number of parameters.

    Returns
    -------
    par_names : list of str
        Names of VSH parameters for the first 2 degrees.

    Raises
    ------
    ValueError
        If the number of parameters is not recognized.
    """
    if parnb == 6:
        par_names = ["D1", "D2", "D3", "R1", "R2", "R3"]
    elif parnb == 16:
        par_names = ["D1", "D2", "D3", "R1", "R2", "R3",
                     "E22R", "E22I", "E21R", "E21I", "E20",
                     "M22R", "M22I", "M21R", "M21I", "M20"]
    elif parnb == 10:
        par_names = ["E22R", "E22I", "E21R", "E21I", "E20",
                     "M22R", "M22I", "M21R", "M21I", "M20"]
    else:
        raise ValueError("Unrecognized number of parameters: {}".format(parnb))

    return par_names


def write_htable(cat_names, pmts, sigs, names=None, opt=sys.stdout, fmt="8.2f"):
    """Print estimates and corresponding formal errors into a horizontal table.

    Parameters
    ----------
    cat_names : list of str
        Names of catalogs or data sets.
    pmts : list of arrays of float
        Estimates of parameters.
    sigs : list of arrays of float
        Formal errors of estimates.
    names : list of str, optional
        Names or labels of parameters. If None, they are initialized based on the length of pmts.
    opt : file-like object, optional
        Default is to print all the output on the screen.
    fmt : str, optional
        Specifier of the output format, default is "8.2f".
    """

    if names is None:
        names = init_par_names(len(pmts[0]))

    if len(pmts) != len(sigs) or len(pmts) != len(cat_names):
        raise ValueError(
            "Length of pmts, sigs, and cat_names must be the same.")

    # Table header
    head_line = ["{:10s}".format("Catalog")]
    head_line.extend([f"  &${name:10s}$" for name in names])
    head_line.append(" \\\\")
    print("".join(head_line), file=opt)
    print("\\hline", file=opt)

    # Data lines
    data_fmt = f"  &${{:{fmt}}} \\pm {{:{fmt}}}$"

    for i in range(len(cat_names)):
        data_line = [f"{cat_names[i]:10s}"]
        pmt, sig = pmts[i], sigs[i]

        for j in range(len(pmt)):
            data_line.append(data_fmt.format(pmt[j], sig[j]))

        data_line.append(" \\\\")
        print("".join(data_line), file=opt)


# ----------- Correlation coefficients -------------------
def display_correlation_matrix(names, parcorrs, deci_digit=2, included_one=True,
                               opt=sys.stdout):
    """Display the correlation coefficient matrix.

    Parameters
    ----------
    names : array
        Names or labels of the parameters.
    parcorrs : array of N * N
        Matrix of correlation coefficients.
    deci_digit : int
        Decimal digits. Only 1 and 2 are supported. Default is 2.
    included_one : boolean
        Whether to include the correlation between the same parameters (value equals to 1). True for yes.
    opt : file handling
        Default to print all the output on the screen.
    """

    parnb = names.size

    print("\nCorrelation coefficient matrix", file=opt)
    print("---------------------------------------------------------", file=opt)

    # If the correlation matrix is an object of np.mat type,
    # convert it to np.ndarray
    if type(parcorrs) is np.mat or type(parcorrs) is np.matrix:
        parcorrs = np.array(parcorrs)

    if deci_digit == 1:
        # Begin printing the correlation coefficients
        if included_one:
            # The first line
            print(("  %4s" * (parnb + 1)) % ("    ", *names), file=opt)

            # Include the correlation coefficient of one
            for i, pmt_namei in enumerate(names):
                line_fmt = "  %4s" + "  %+4.1f" * (i + 1)
                print(line_fmt % (pmt_namei, *parcorrs[i, :i + 1]), file=opt)
        else:
            # The first line
            print(("  %4s" * parnb) % ("    ", *names[:-1]), file=opt)

            for i in range(1, parnb):
                line_fmt = "  %4s" + "  %+4.1f" * i
                print(line_fmt % (names[i], *parcorrs[i, :i]), file=opt)

    elif deci_digit == 2:

        # Begin printing the correlation coefficients
        if included_one:
            # The first line
            print(("  %5s" * (parnb + 1)) % ("    ", *names), file=opt)

            for i, pmt_namei in enumerate(names):
                line_fmt = "  %5s" + "  %+5.2f" * (i + 1)
                print(line_fmt % (pmt_namei, *parcorrs[i, :i + 1]), file=opt)
        else:
            # The first line
            print(("  %5s" * parnb) % ("    ", *names[:-1]), file=opt)

            for i in range(1, parnb):
                line_fmt = "  %5s" + "  %+5.2f" * i
                print(line_fmt % (names[i], *parcorrs[i, :i]), file=opt)
    else:
        print("Only 1 or 2 decimal digits are supported!")
        sys.exit()


def display_vsh_correlation_matrix(parcorrs, par_names=None,
                                   deci_digit=1, included_one=True, opt=sys.stdout):
    """Display the correlation coefficient matrix for VSH02 parameters.

    Parameters
    ----------
    parcorrs : array of N * N
        Matrix of correlation coefficients.
    par_names : array of string, optional
        Names or labels of the parameters. If not provided, default names will be used based on matrix size.
    deci_digit : int
        Decimal digits. Only 1 and 2 are supported. Default is 1.
    included_one : boolean
        Whether to include the correlation between the same parameters (value equals to 1). True for yes.
    opt : file handling, optional
        Output destination. Default is to print on the screen.
    """

    if par_names is None:
        parnb = parcorrs.shape[0]
        if parnb == 6:
            par_names = np.array(["D1", "D2", "D3", "R1", "R2", "R3"])
        elif parnb == 16:
            par_names = np.array(["D1", "D2", "D3", "R1", "R2", "R3",
                                  "E22R", "E22I", "E21R", "E21I", "E20",
                                  "M22R", "M22I", "M21R", "M21I", "M20"])
        else:
            raise ValueError(f"Unsupported number of parameters: {parnb}")
    else:
        parnb = par_names.size

    # Check the shape of the matrix
    a, b = parcorrs.shape
    if a != b or a != parnb:
        raise ValueError(
            f"The shape of the correlation matrix should be ({parnb}, {parnb})!")

    display_correlation_matrix(
        par_names, parcorrs, deci_digit, included_one, opt)


def display_vsh_fit_results(pmts, sigs, parcorrs,
                            par_names=None, opt=sys.stdout, fmt="%5.0f"):
    """Display VSH fit results including parameter estimates, errors, and correlation matrix.

    Parameters
    ----------
    par_names : array of string, optional
        Names or labels of the parameters. If not provided, default names will be used based on the number of parameters.
    pmts : array of float
        Estimates of parameters.
    sigs : array of float
        Formal errors of the estimates.
    parcorrs : array of float
        Correlation matrix of the parameters.
    opt : file handling, optional
        Output destination. Default is to print on the screen.
    fmt : string, optional
        Format specifier for the output. Default is "%5.0f".
    """

    parnb = len(pmts)

    if par_names is None:
        par_names = init_par_names(parnb)

    # Create a table with parameter names, estimates, and errors
    tvsh = Table([par_names, pmts, sigs], names=[
        "Parameter", "Estimate", "Error"])
    tvsh["Estimate"].format = fmt
    tvsh["Error"].format = fmt
    tvsh["Estimate"].unit = u.uas
    tvsh["Error"].unit = u.uas

    # Print the table
    print(tvsh, file=opt)

    # Display the correlation matrix
    display_vsh_correlation_matrix(parcorrs, par_names,
                                   deci_digit=1, included_one=True, opt=opt)


def display_vsh_results_from_dict(output, par_names=None, opt=sys.stdout, fmt="%5.0f"):
    """Display VSH fit results from a dictionary including parameter estimates, errors, and correlation matrix.

    Parameters
    ----------
    output : dict
        Dictionary containing VSH fit results with keys "pmt" for parameters, "sig" for uncertainties, and "cor_mat" for the correlation matrix.
    par_names : array of string, optional
        Names or labels of the parameters. If not provided, default names will be used based on the number of parameters.
    opt : file-like object, optional
        Output destination. Default is to print to the screen.
    fmt : string, optional
        Format specifier for the output. Default is "%5.0f".
    """

    pmts = output["pmt"]
    sigs = output["sig"]
    parcorrs = output["cor_mat"]

    parnb = len(pmts)

    if par_names is None:
        par_names = init_par_names(parnb)

    # Create a table with parameter names, estimates, and errors
    tvsh = Table([par_names, pmts, sigs], names=[
        "Parameter", "Estimate", "Error"])
    tvsh["Estimate"].format = fmt
    tvsh["Error"].format = fmt
    tvsh["Estimate"].unit = u.uas
    tvsh["Error"].unit = u.uas

    # Print the table
    print(tvsh, file=opt)

    # Display the correlation matrix
    display_vsh_correlation_matrix(parcorrs, par_names,
                                   deci_digit=1, included_one=True, opt=opt)


def save_vsh_results_to_file(pmts, sigs, output_file, par_names=None, fmt="%5.0f", comment=""):
    """Save the VSH results, including parameter estimates and errors, into a text file.

    Parameters
    ----------
    pmts : array of float
        Estimates of VSH parameters.
    sigs : array of float
        Formal errors associated with the parameter estimates.
    output_file : str
        The path to the output text file where results will be saved.
    par_names : list of str, optional
        Names or labels of the parameters. If not provided, default names will be generated based on the number of parameters.
    fmt : str, optional
        Format specifier for the numerical output. Default is "%5.0f".
    comment : str, optional
        Additional comments to include in the output file metadata.
    """

    parnb = len(pmts)

    if par_names is None:
        par_names = init_par_names(parnb)

    # Create a table with parameter names, estimates, and errors
    tvsh = Table([par_names, pmts, sigs],
                 names=["Parameter", "Estimate", "Error"])
    tvsh["Estimate"].format = fmt
    tvsh["Error"].format = fmt
    tvsh["Estimate"].unit = u.uas
    tvsh["Error"].unit = u.uas
    tvsh.meta["comment"] = comment

    # Write the table to the specified file
    tvsh.write(output_file, format="ascii", overwrite=True)


def save_vsh_results_to_latex(catalog_names, parameter_estimates, parameter_errors, output_file=sys.stdout, parameter_names=None, format_specifier="%5.0f"):
    """Save the VSH results into a LaTeX table.

    Parameters
    ----------
    catalog_names : list of str
        Names of the catalogs or data sets being analyzed.
    parameter_estimates : array of float
        Estimates of VSH parameters for each catalog.
    parameter_errors : array of float
        Formal errors associated with the parameter estimates.
    output_file : file-like object, optional
        File handle to write the LaTeX table to. Defaults to printing on the screen (sys.stdout).
    parameter_names : list of str, optional
        Names or labels of the parameters. If not provided, default names will be generated based on the number of parameters.
    format_specifier : str, optional
        Format specifier for the numerical output. Default is "%5.0f".
    """

    # Determine the number of parameters
    num_parameters = len(parameter_estimates[0])

    # Initialize parameter names if not provided
    if parameter_names is None:
        parameter_names = init_par_names(num_parameters)

    # Write the table using the helper function
    write_htable(catalog_names, parameter_estimates, parameter_errors,
                 parameter_names, output_file, format_specifier)
