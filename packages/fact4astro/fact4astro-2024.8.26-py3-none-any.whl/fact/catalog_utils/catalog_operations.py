#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: catalog_operations.py
"""
Created on Mon 26 Aug 2024 10:36:25 AM CST

@author: Neo(niu.liu@nju.edu.cn)
"""


import numpy as np


def determine_coordinate_system(table):
    """
    Determine the coordinate system used in the table.

    Parameters
    ----------
    table : astropy.table.Table
        The input table.

    Returns
    -------
    lon_str : str
        The longitude coordinate name.
    lat_str : str
        The latitude coordinate name.
    """
    if "ra" in table.colnames:
        return "ra", "dec"
    elif "elon" in table.colnames:
        return "elon", "elat"
    elif "lon" in table.colnames:
        return "lon", "lat"
    else:
        raise ValueError("No recognized column names for position. "
                         "Please include one of 'ra/dec', 'elon/elat', or 'lon/lat'.")


def extract_position_columns(table, lon_str, lat_str, source_name):
    """
    Extract and prepare position-related columns from the input table.

    Parameters
    ----------
    table : astropy.table.Table
        The input table.
    lon_str : str
        The longitude coordinate name.
    lat_str : str
        The latitude coordinate name.
    source_name : str
        The source name column.
    label : str
        The label for the table columns.
    ref_err : bool, optional
        If True, extract the error columns as well.

    Returns
    -------
    extracted_table : astropy.table.Table
        Table with relevant columns extracted.
    """
    lonerr_str = f"{lon_str}_err"
    laterr_str = f"{lat_str}_err"
    cor_str1 = f"{lon_str}_{lat_str}_corr"
    cor_str2 = f"{lon_str}_{lat_str}_cor"
    cov_str = f"{lon_str}_{lat_str}_cov"

    cols_to_keep = [source_name, lon_str, lat_str, lonerr_str, laterr_str]

    if cor_str1 in table.colnames:
        cols_to_keep.append(cor_str1)
    elif cor_str2 in table.colnames:
        cols_to_keep.append(cor_str2)
    elif cov_str in table.colnames:
        cols_to_keep.append(cov_str)

    extracted_table = table[cols_to_keep]

    return extracted_table


def determine_pm_coordinate_system(table):
    """
    Determine the proper motion coordinate system used in the table.

    Parameters
    ----------
    table : astropy.table.Table
        The input table.

    Returns
    -------
    lon_str : str
        The longitude coordinate name.
    lat_str : str
        The latitude coordinate name.
    pmlon_str : str
        The proper motion longitude coordinate name.
    pmlat_str : str
        The proper motion latitude coordinate name.
    """
    if "pmra" in table.colnames:
        return "ra", "dec", "pmra", "pmdec"
    elif "pmelon" in table.colnames:
        return "elon", "elat", "pmelon", "pmelat"
    elif "pmlon" in table.colnames:
        return "lon", "lat", "pmlon", "pmlat"
    else:
        raise ValueError("No recognized column names for proper motion. "
                         "Please include one of 'pmra/pmdec', 'pmelon/pmelat', or 'pmlon/pmlat'.")


def extract_pm_columns(table, pmlon_str, pmlat_str, lon_str, lat_str, source_name):
    """
    Extract and prepare proper motion-related columns from the input table.

    Parameters
    ----------
    table : astropy.table.Table
        The input table.
    pmlon_str : str
        The proper motion longitude coordinate name.
    pmlat_str : str
        The proper motion latitude coordinate name.
    lon_str : str
        The longitude coordinate name.
    lat_str : str
        The latitude coordinate name.
    source_name : str
        The source name column.
    label : str
        The label for the table columns.
    ref_err : bool, optional
        If True, extract the error columns as well.

    Returns
    -------
    extracted_table : astropy.table.Table
        Table with relevant columns extracted.
    """
    pmlonerr_str = f"{pmlon_str}_err"
    pmlaterr_str = f"{pmlat_str}_err"
    cor_str1 = f"{pmlon_str}_{pmlat_str}_corr"
    cor_str2 = f"{pmlon_str}_{pmlat_str}_cor"
    cov_str = f"{pmlon_str}_{pmlat_str}_cov"

    cols_to_keep = [source_name, pmlon_str, pmlat_str,
                    pmlonerr_str, pmlaterr_str, lon_str, lat_str]

    if cor_str1 in table.colnames:
        cols_to_keep.append(cor_str1)
    elif cor_str2 in table.colnames:
        cols_to_keep.append(cor_str2)
    elif cov_str in table.colnames:
        cols_to_keep.append(cov_str)

    extracted_table = table[cols_to_keep]
    return extracted_table


def calculate_vector_magnitude(x, xerr=None):
    """
    Calculate the magnitude of a vector and optionally its error.

    Parameters
    ----------
    x : array-like
        The vector for which to calculate the magnitude.
    xerr : array-like, optional
        The uncertainties associated with the vector components.

    Returns
    -------
    xmod : float
        The magnitude of the vector.
    xmoderr : float, optional
        The uncertainty in the magnitude, returned only if `xerr` is provided.
    """
    xmod = np.sqrt(np.sum(x**2))

    if xerr is None:
        return xmod
    else:
        xmoderr = np.sqrt(np.dot(x**2, xerr**2)) / xmod
        return xmod, xmoderr


def extract_data_from_table(data_tab):
    """Extract data from the Astropy table and convert to numpy arrays."""

    # Transform astropy.Column into np.array
    if "dra" in data_tab.colnames:
        dra = np.array(data_tab["dra"])
    elif "pmra" in data_tab.colnames:
        dra = np.array(data_tab["pmra"])
    else:
        raise ValueError("'dra' or 'pmra' is not specificed.")

    if "ddec" in data_tab.colnames:
        ddec = np.array(data_tab["ddec"])
    elif "pmdec" in data_tab.colnames:
        ddec = np.array(data_tab["pmdec"])
    else:
        raise ValueError("'ddec' or 'pmdec' is not specificed.")

    ra = np.deg2rad(np.array(data_tab["ra"]))
    dec = np.deg2rad(np.array(data_tab["dec"]))

    if "dra_err" in data_tab.colnames:
        dra_err = np.array(data_tab["dra_err"])
    elif "dra_error" in data_tab.colnames:
        dra_err = np.array(data_tab["dra_error"])
    elif "pmra_err" in data_tab.colnames:
        dra_err = np.array(data_tab["pmra_err"])
    elif "pmra_error" in data_tab.colnames:
        dra_err = np.array(data_tab["pmra_error"])
    else:
        dra_err = np.ones(len(data_tab))
        print("Using equal weights for dra_err.")

    if "ddec_err" in data_tab.colnames:
        ddec_err = np.array(data_tab["ddec_err"])
    elif "ddec_error" in data_tab.colnames:
        ddec_err = np.array(data_tab["ddec_error"])
    elif "pmdec_err" in data_tab.colnames:
        ddec_err = np.array(data_tab["pmdec_err"])
    elif "pmdec_error" in data_tab.colnames:
        ddec_err = np.array(data_tab["pmdec_error"])
    else:
        ddec_err = np.ones(len(data_tab))
        print("Using equal weights for ddec_err.")

    return dra, ddec, dra_err, ddec_err, ra, dec
