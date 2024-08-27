#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: read_ocars.py
"""
Created on Fri Sep 11 11:05:17 2020

@author: Neo(liuniu@smail.nju.edu.cn)

This module provides functions for access of the Optical Characteristics of Astrometric Radio Sources (OCARS) catalog available at http://www.gaoran.ru/english/as/ac_vlbi/#OCARS.

History
2024-01-23: Update read_ocars adapt to the updates of OCRAS catalog

"""

from astropy.table import Table
from astropy import units as u

# My modules
from .download_online_content import download_online_data
from .cat_vars import load_cfg


__all__ = ["read_ocars"]


# -----------------------------  MAIN -----------------------------
def read_ocars(ocars_file=None):
    """Read the OCARS catalog

    Returns
    -------
    ocars_cat: an astropy.Table object
        data in the catalog

    """

    if ocars_file is None:
        cfg = load_cfg()
        ocars_main_url = cfg["online_url"]["ocars_main_csv"]

        # Download online data
        ocars_file = download_online_data(ocars_main_url)

    # Parse the data
    ocars_cat = Table.read(ocars_file, format="ascii.csv",
                           names=["iers_name", "iau_name_short",
                                  "ra", "dec", "ra_error", "dec_error", "ra_dec_corr", "pos_epoch",
                                  "ra_x", "dec_x", "ra_error_x", "dec_error_x", "ra_dec_corr_x", "pos_epoch_x",
                                  "ra_k", "dec_k", "ra_error_k", "dec_error_k", "ra_dec_corr_k", "pos_epoch_k",
                                  "ra_ka", "dec_ka", "ra_error_ka", "dec_error_ka", "ra_dec_corr_ka", "pos_epoch_ka",
                                  "ra_c", "dec_c", "ra_error_c", "dec_error_c", "ra_dec_corr_c", "pos_epoch_c",
                                  "ra_l", "dec_l", "ra_error_l", "dec_error_l", "ra_dec_corr_l", "pos_epoch_l",
                                  "ra_s", "dec_s", "ra_error_s", "dec_error_s", "ra_dec_corr_s", "pos_epoch_s",
                                  "ra_q", "dec_q", "ra_error_q", "dec_error_q", "ra_dec_corr_q", "pos_epoch_q",
                                  "gal_lon", "gal_lat", "class",
                                  "z", "z_flag", "z_simbad", "z_simbad_flag", "z_sdss", "z_sdss_flag",
                                  "u_mag", "U_mag", "B_mag", "g_mag", "V_mag", "r_mag",
                                  "R_mag", "i_mag", "I_mag", "z_mag", "J_mag", "H_mag",
                                  "K_mag", "G_mag", "GBP_mag", "GRP_mag"])

    # # Add Correction factor to 'ra_err'
    # arc_fac = np.cos(np.deg2rad(ocars_cat["dec"]))
    # ocars_cat["ra_err"] = ocars_cat["ra_err"] * arc_fac

    # Add unit information
    # (1) Mixture?
    ocars_cat["ra"].unit = u.deg
    ocars_cat["dec"].unit = u.deg
    ocars_cat["ra_error"].unit = u.mas
    ocars_cat["dec_error"].unit = u.mas
    ocars_cat["pos_epoch"].unit = u.yr
    # (2) X-band
    ocars_cat["ra_x"].unit = u.deg
    ocars_cat["dec_x"].unit = u.deg
    ocars_cat["ra_error_x"].unit = u.mas
    ocars_cat["dec_error_x"].unit = u.mas
    ocars_cat["pos_epoch_x"].unit = u.yr
    # (3) K-band
    ocars_cat["ra_k"].unit = u.deg
    ocars_cat["dec_k"].unit = u.deg
    ocars_cat["ra_error_k"].unit = u.mas
    ocars_cat["dec_error_k"].unit = u.mas
    ocars_cat["pos_epoch_k"].unit = u.yr
    # (4) Ka-band
    ocars_cat["ra_ka"].unit = u.deg
    ocars_cat["dec_ka"].unit = u.deg
    ocars_cat["ra_error_ka"].unit = u.mas
    ocars_cat["dec_error_ka"].unit = u.mas
    ocars_cat["pos_epoch_ka"].unit = u.yr
    # (5) C-band
    ocars_cat["ra_c"].unit = u.deg
    ocars_cat["dec_c"].unit = u.deg
    ocars_cat["ra_error_c"].unit = u.mas
    ocars_cat["dec_error_c"].unit = u.mas
    ocars_cat["pos_epoch_c"].unit = u.yr
    # (6) L-band
    ocars_cat["ra_l"].unit = u.deg
    ocars_cat["dec_l"].unit = u.deg
    ocars_cat["ra_error_l"].unit = u.mas
    ocars_cat["dec_error_l"].unit = u.mas
    ocars_cat["pos_epoch_l"].unit = u.yr
    # (7) S-band
    ocars_cat["ra_s"].unit = u.deg
    ocars_cat["dec_s"].unit = u.deg
    ocars_cat["ra_error_s"].unit = u.mas
    ocars_cat["dec_error_s"].unit = u.mas
    ocars_cat["pos_epoch_s"].unit = u.yr
    # (8) Q-band
    ocars_cat["ra_q"].unit = u.deg
    ocars_cat["dec_q"].unit = u.deg
    ocars_cat["ra_error_q"].unit = u.mas
    ocars_cat["dec_error_q"].unit = u.mas
    ocars_cat["pos_epoch_q"].unit = u.yr

    return ocars_cat


# -------------------------------- MAIN --------------------------------
if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
