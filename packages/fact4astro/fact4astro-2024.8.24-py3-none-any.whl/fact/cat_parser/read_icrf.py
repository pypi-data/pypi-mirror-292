#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: read_icrf.py
"""
Created on Sat Sep 29 18:15:50 2018

@author: Neo(liuniu@nju.edu.cn)

History
-------
2023-11-21: Remove the cfg configuration
2024-01-21: Rename columns (ra_err->ra_error, dec_err->dec_error) to be consistent with Gaia 
            catalog
"""

import numpy as np

from astropy.table import Table, Column
from astropy import units as u
from astropy.coordinates import SkyCoord

# my modules
from .download_online_content import download_online_data
from .calc_error_ellipse_pmt import compute_error_ellipse_par
from .cat_vars import load_cfg

__all__ = ["read_icrf1", "read_icrf2", "read_icrf3", "read_icrf"]


# -----------------------------  FUNCTIONS -----------------------------
def parse_radec_str(icrf_file, col_start_indx, col_end_indx, data_start_indx=0):
    """Convert string of RA/Dec into Columns 
    """

    # Position information
    ra_dec_str = Table.read(icrf_file, format="ascii.fixed_width_no_header",
                            names=["ra_dec"], col_starts=[col_start_indx], col_ends=[col_end_indx],
                            data_start=data_start_indx)

    ra_dec = SkyCoord(ra_dec_str["ra_dec"], unit=(u.hourangle, u.deg))
    ra = Column(ra_dec.ra, name="ra")
    dec = Column(ra_dec.dec, name="dec")

    return ra, dec


def correct_pos_err(icrf_cat, dec):
    """Correct RA error and add unit information
    """

    icrf_cat["ra_error"] = icrf_cat["ra_error"] * 15e3 * np.cos(dec.to("rad"))
    icrf_cat["ra_error"].unit = u.mas
    icrf_cat["dec_error"].unit = u.arcsec
    icrf_cat["dec_error"] = icrf_cat["dec_error"].to(u.mas)

    return icrf_cat


def read_icrf1(icrf1_file=None, ext=None):
    """Read the ICRF1 catalog

    Parameter
    ---------
    icrf1_file : string
        file name and path of the ICRF1 catalog

    Return
    ------
    icrf1 : an astropy.Table object
        data in the catalog
    """

    if icrf1_file is None:
        cfg = load_cfg()

        # Download online data
        if ext is None:
            icrf_url = cfg["online_url"]["icrf1_all"]
            data_start_indx = 20
            col_starts = [5, 24, 34, 37, 39, 79, 89,
                          98, 104, 112, 120, 128, 134]
            col_ends = [21, 32, 35, 38, 40, 87, 95,
                        102, 110, 119, 126, 132, 140]
            ra_indx, dec_index = 42, 73
            col_names = ["iau_name", "iers_name", "type",
                         "si_s", "si_x",
                         "ra_error", "dec_error", "ra_dec_corr",
                         "mean_obs", "beg_obs", "end_obs",
                         "nb_sess", "nb_del"]
        elif ext == 1:
            icrf_url = cfg["online_url"]["icrf1_ext1"]
            data_start_indx = 22
            col_starts = [5, 24, 34, 37, 39, 76, 86,
                          95, 102, 110, 118, 126, 132]
            col_ends = [21, 32, 35, 38, 40, 83, 93,
                        100, 108, 117, 124, 130, 138]
            ra_indx, dec_index = 42, 73
            col_names = ["iau_name", "iers_name", "type",
                         "si_s", "si_x",
                         "ra_error", "dec_error", "ra_dec_corr",
                         "mean_obs", "beg_obs", "end_obs",
                         "nb_sess", "nb_del"]
        elif ext == 2:
            icrf_url = cfg["online_url"]["icrf1_ext2"]
            data_start_indx = 13
            col_starts = [5, 23, 70, 82, 92, 102, 111, 121, 130, 137]
            col_ends = [21, 31, 78, 89, 98, 108, 118, 128, 135, 144]
            ra_indx, dec_index = 34, 68
            col_names = ["iau_name", "iers_name",
                         "ra_error", "dec_error", "ra_dec_corr",
                         "mean_obs", "beg_obs", "end_obs",
                         "nb_sess", "nb_del"]
        else:
            print(f"Invalid number of extension {ext} of ICRF1")
            exit(1)

        icrf1_file = download_online_data(icrf_url)

    # Read ICRF1 catalog
    icrf1 = Table.read(icrf1_file,
                       format="ascii.fixed_width_no_header",
                       names=col_names,
                       col_starts=col_starts,
                       col_ends=col_ends,
                       data_start=data_start_indx)

    # Position information
    ra, dec = parse_radec_str(icrf1_file, ra_indx, dec_index, data_start_indx)

    # Add source position to the table
    icrf1.add_columns([ra, dec], indexes=[3, 3])

    # Add unit information
    icrf1 = correct_pos_err(icrf1, dec)
    icrf1["ra_dec_corr"] = icrf1["ra_dec_corr"].filled(0)

    # Add the semi-major axis of error ellipse to the table
    icrf1 = compute_error_ellipse_par(icrf1, [8, 8, 8])

    return icrf1


def read_icrf2(icrf2_file=None):
    """Read the ICRF1 catalog

    Parameter
    ---------
    icrf2_file : string
        file name and path of the ICRF2 catalog

    Return
    ------
    icrf2 : an astropy.Table object
        data in the catalog
    """

    if icrf2_file is None:
        cfg = load_cfg()

        # Download online data
        icrf_url = cfg["online_url"]["icrf2"]
        icrf2_file = download_online_data(icrf_url)

    # Read ICRF2 catalog
    data_start_indx = 17
    icrf2 = Table.read(icrf2_file,
                       format="ascii.fixed_width_no_header",
                       names=["iau_name", "iers_name", "type",
                              "ra_error", "dec_error", "ra_dec_corr",
                              "mean_obs", "beg_obs", "end_obs",
                              "nb_sess", "nb_del"],
                       col_starts=[5, 23, 33, 74, 85,
                                   96, 104, 112, 120, 129, 137],
                       col_ends=[21, 31, 34, 83, 93,
                                 102, 111, 119, 127, 134, 140],
                       data_start=data_start_indx)

    # Position information
    ra, dec = parse_radec_str(icrf2_file, 36, 72, data_start_indx)

    # Add source position to the table
    icrf2.add_columns([ra, dec], indexes=[3, 3])

    # Add unit information
    icrf2 = correct_pos_err(icrf2, dec)

    # Add the semi-major axis of error ellipse to the table
    icrf2 = compute_error_ellipse_par(icrf2, [8, 8, 8])

    return icrf2


def read_icrf3(icrf3_file=None, band="sx"):
    """Read the ICRF3 catalog.

    Parameter
    ---------
    icrf3_file : string
        path to or content of the ICRF3 catalog
    band : str, default "sx"
        observing band of VLBI, only works for ICRF3

    Return
    ------
    icrf3 : an astropy.Table object
        data in the catalog
    """

    if icrf3_file is None:
        cfg = load_cfg()

        # Download online data
        if band in ["sx", "SX", "s/x", "S/X"]:
            icrf_url = cfg["online_url"]["icrf3sx"]
        elif band in ["k", "K"]:
            icrf_url = cfg["online_url"]["icrf3k"]
        elif band in ["xka", "XKA", "XKa", "x/ka", "X/Ka", "X/KA"]:
            icrf_url = cfg["online_url"]["icrf3xka"]
        else:
            print("wv could only be 'sx', 'k', or 'xka' for ICRF3.")
            exit(1)

        icrf3_file = download_online_data(icrf_url)

    # Read ICRF3 catalog
    data_start_indx = 16
    icrf3 = Table.read(icrf3_file,
                       format="ascii.fixed_width", data_start=data_start_indx,
                       names=["iau_name", "iers_name", "type",
                              "ra_error", "dec_error", "ra_dec_corr",
                              "mean_obs", "beg_obs", "end_obs",
                              "nb_sess", "nb_del"],
                       col_starts=[0, 25, 35, 83, 98,
                                   108, 118, 127, 136, 145, 150],
                       col_ends=[20, 32, 35, 92, 106,
                                 114, 124, 133, 142, 148, 155])

    # Position information
    ra, dec = parse_radec_str(icrf3_file, 40, 77, data_start_indx)

    # Add source position to the table
    icrf3.add_columns([ra, dec], indexes=[3, 3])

    # Add unit information
    icrf3 = correct_pos_err(icrf3, dec)

    # Add the semi-major axis of error ellipse to the table
    icrf3 = compute_error_ellipse_par(icrf3, [8, 8, 8])

    return icrf3


def read_icrf(data_file=None, gen=3, band="sx", ext=None):
    """Parse the ICRF catalog

    Parameters
    ----------
    data_file : str, default None
        path to the catalog file on the local machine. 
        If None, it will download the related files online.
    gen : int, default 3
        generation of the ICRF
    band : str, default "sx"
        observing band of VLBI, only works for ICRF3
    ext : int, default None
        extention version, only works for ICRF1
    """

    if gen == 3:
        # ICRF3
        icrf_cat = read_icrf3(icrf3_file=data_file, band=band)

    elif gen == 2:
        # ICRF2
        icrf_cat = read_icrf2(data_file)

    elif gen == 1:
        # ICRF1
        icrf_cat = read_icrf1(data_file, ext=ext)

    else:
        print(f"Invalid ICRF generation of {gen}")
        exit(1)

    return icrf_cat


# -------------------------------- MAIN --------------------------------
if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
