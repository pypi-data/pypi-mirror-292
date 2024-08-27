#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: read_rfc.py
"""
Created on Sat May 22 11:06:18 2021

@author: Neo(niu.liu@nju.edu.cn)

This module provides parser to read the local data file of Radio Fundamental Catalog (RFC) 
or download it directly from http://astrogeo.org/rfc/.

History
2024-01-23: Update read_ocars adapt to the updates of RFC2023d catalog
"""

import numpy as np
from astropy.table import Table, Column
from astropy import units as u
from astropy.coordinates import SkyCoord

# My modules
from .download_online_content import download_online_data
from .cat_vars import load_cfg
from .calc_error_ellipse_pmt import compute_error_ellipse_par


__all__ = ["read_rfc"]


# -----------------------------  MAIN -----------------------------
def parse_radec_str(rfc_file, col_start_indx, col_end_indx, data_start_indx=0):
    """Convert string of RA/Dec into Columns 
    """

    # Position information
    ra_dec_str = Table.read(rfc_file, format="ascii.fixed_width_no_header",
                            names=["ra_dec"], col_starts=[col_start_indx], col_ends=[col_end_indx],
                            data_start=data_start_indx)

    ra_dec = SkyCoord(ra_dec_str["ra_dec"], unit=(u.hourangle, u.deg))
    ra = Column(ra_dec.ra, name="ra")
    dec = Column(ra_dec.dec, name="dec")

    return ra, dec


def read_rfc(rfc_file=None, version="2023d"):
    """Read the RFC catalog

    Information about the RFC catalog could be found at
    http://astrogeo.org/rfc/

    Returns
    -------
    rfc_cat: an astropy.Table object
        data in the catalog

    """

    if rfc_file is None:
        cfg = load_cfg()
        rfc_url = cfg["online_url"]["rfc"] + \
            f"/rfc_{version}/rfc_{version}_cat.txt"

        rfc_file = download_online_data(rfc_url)

    # Read RFC catalog
    rfc_cat = Table.read(rfc_file, format="ascii.fixed_width_no_header",
                         names=["ivs_name", "iau_name_short", "category",
                                "ra", "dec", "ra_error", "dec_error",
                                "ra_dec_corr", "used_obs",
                                "S_total_flux_flag", "S_total_flux",
                                "S_unrev_flux_flag", "S_unrev_flux",
                                "C_total_flux_flag", "C_total_flux",
                                "C_unrev_flux_flag", "C_unrev_flux",
                                "X_total_flux_flag", "X_total_flux",
                                "X_unrev_flux_flag", "X_unrev_flux",
                                "U_total_flux_flag", "U_total_flux",
                                "U_unrev_flux_flag", "U_unrev_flux",
                                "K_total_flux_flag", "K_total_flux",
                                "K_unrev_flux_flag", "K_unrev_flux",
                                "used_band", "catalogue_name"],
                         col_starts=[3, 12, 0, 24, 40, 57, 64, 72, 79,
                                     87, 88, 94, 95, 102, 103, 109, 110,
                                     117, 118, 124, 125, 132, 133, 139, 140,
                                     147, 148, 154, 155, 162, 167],
                         col_ends=[10, 21, 1, 38, 56, 62, 69, 77, 84,
                                   87, 92, 94, 99, 102, 107, 109, 114,
                                   117, 122, 124, 129, 132, 137, 139, 144,
                                   147, 152, 154, 159, 164, 174])

    # Position information
    ra, dec = parse_radec_str(rfc_file, 24, 56)
    rfc_cat["ra"] = ra
    rfc_cat["dec"] = dec

    # Add unit information
    rfc_cat["ra_error"].unit = u.mas
    rfc_cat["dec_error"].unit = u.mas

    # Add the semi-major axis of error ellipse to the table
    rfc_cat = compute_error_ellipse_par(rfc_cat, [9, 9, 9])

    return rfc_cat


def convert_offset_column(str_col):
    """Convert string to values
    """

    val_col = np.zeros_like(str_col)
    for i, stri in enumerate(str_col):
        if stri == "n/a" or stri[-1] == "*":
            val_col[i] = 0
        else:
            val_col[i] = float(stri)

    return val_col


def read_rfc_mul(rfc_file=None, version="2023d"):
    """Read the multiband extension of the RFC catalog

    Information about the RFC catalog could be found at
    http://astrogeo.org/rfc/

    Returns
    -------
    rfc_cat: an astropy.Table object
        data in the catalog

    """

    if rfc_file is None:
        cfg = load_cfg()
        rfc_url = cfg["online_url"]["rfc"] + \
            f"/rfc_{version}/rfc_{version}_mul.txt"

        rfc_file = download_online_data(rfc_url)

    # Read RFC catalog
    rfc_cat = Table.read(rfc_file, format="ascii.fixed_width_no_header",
                         names=["iau_name_short",
                                "ra", "dec", "ra_error", "dec_error",
                                "ra_dec_corr", "used_obs",
                                # Dual S/X-band
                                "dra_sx", "ddec_sx", "ra_error_sx",
                                "dec_error_sx", "ra_dec_corr_sx", "used_obs_sx",
                                # S-band
                                "dra_s", "ddec_s", "ra_error_s",
                                "dec_error_s", "ra_dec_corr_s", "used_obs_s",
                                # C-band
                                "dra_c", "ddec_c", "ra_error_c",
                                "dec_error_c", "ra_dec_corr_c", "used_obs_c",
                                # X-band
                                "dra_x", "ddec_x", "ra_error_x",
                                "dec_error_x", "ra_dec_corr_x", "used_obs_x",
                                # K-band
                                "dra_k", "ddec_k", "ra_error_k",
                                "dec_error_k", "ra_dec_corr_k", "used_obs_k",
                                ],
                         col_starts=[4, 16, 31, 49, 56, 64, 72,
                                     89, 99, 107, 114, 119, 127,  # Dual band
                                     141, 149, 157, 164, 171, 178,  # S-band
                                     194, 202, 210, 217, 224, 231,  # C-band
                                     247, 255, 263, 270, 277, 284,  # X-band
                                     301, 308, 316, 323, 330, 337,  # K-band
                                     ],
                         col_ends=[13, 30, 46, 54, 61, 69, 76,
                                   95, 103, 110, 117, 124, 132,  # Dual band
                                   148, 156, 163, 170, 177, 185,  # S-band
                                   201, 209, 216, 223, 230, 238,  # C-band
                                   254, 262, 269, 276, 283, 291,  # X-band
                                   307, 315, 322, 329, 336, 344,  # K-band
                                   ])

    # Position information
    ra, dec = parse_radec_str(rfc_file, 16, 46)
    rfc_cat["ra"] = ra
    rfc_cat["dec"] = dec

    # Add unit information
    rfc_cat["ra_error"].unit = u.mas
    rfc_cat["dec_error"].unit = u.mas

    # Fill the masked value of 'n/a'
    # (1) Dual S/X-band
    rfc_cat["dra_sx"] = convert_offset_column(rfc_cat["dra_sx"])
    rfc_cat["ddec_sx"] = convert_offset_column(rfc_cat["ddec_sx"])
    rfc_cat["ra_error_sx"] = convert_offset_column(
        rfc_cat["ra_error_sx"])
    rfc_cat["dec_error_sx"] = convert_offset_column(
        rfc_cat["dec_error_sx"])
    rfc_cat["ra_dec_corr_sx"] = convert_offset_column(
        rfc_cat["ra_dec_corr_sx"])
    rfc_cat["dra_sx"].unit = u.mas
    rfc_cat["ddec_sx"].unit = u.mas
    rfc_cat["ra_error_sx"].unit = u.mas
    rfc_cat["dec_error_sx"].unit = u.mas
    # (2) S-band
    rfc_cat["dra_s"] = convert_offset_column(rfc_cat["dra_s"])
    rfc_cat["ddec_s"] = convert_offset_column(rfc_cat["ddec_s"])
    rfc_cat["ra_error_s"] = convert_offset_column(
        rfc_cat["ra_error_s"])
    rfc_cat["dec_error_s"] = convert_offset_column(
        rfc_cat["dec_error_s"])
    rfc_cat["ra_dec_corr_s"] = convert_offset_column(
        rfc_cat["ra_dec_corr_s"])
    rfc_cat["dra_s"].unit = u.mas
    rfc_cat["ddec_s"].unit = u.mas
    rfc_cat["ra_error_s"].unit = u.mas
    rfc_cat["dec_error_s"].unit = u.mas
    # (3) C-band
    rfc_cat["dra_c"] = convert_offset_column(rfc_cat["dra_c"])
    rfc_cat["ddec_c"] = convert_offset_column(rfc_cat["ddec_c"])
    rfc_cat["ra_error_c"] = convert_offset_column(
        rfc_cat["ra_error_c"])
    rfc_cat["dec_error_c"] = convert_offset_column(
        rfc_cat["dec_error_c"])
    rfc_cat["ra_dec_corr_c"] = convert_offset_column(
        rfc_cat["ra_dec_corr_c"])
    rfc_cat["dra_c"].unit = u.mas
    rfc_cat["ddec_c"].unit = u.mas
    rfc_cat["ra_error_c"].unit = u.mas
    rfc_cat["dec_error_c"].unit = u.mas
    # (4) X-band
    rfc_cat["dra_x"] = convert_offset_column(rfc_cat["dra_x"])
    rfc_cat["ddec_x"] = convert_offset_column(rfc_cat["ddec_x"])
    rfc_cat["ra_error_x"] = convert_offset_column(
        rfc_cat["ra_error_x"])
    rfc_cat["dec_error_x"] = convert_offset_column(
        rfc_cat["dec_error_x"])
    rfc_cat["ra_dec_corr_x"] = convert_offset_column(
        rfc_cat["ra_dec_corr_x"])
    rfc_cat["dra_x"].unit = u.mas
    rfc_cat["ddec_x"].unit = u.mas
    rfc_cat["ra_error_x"].unit = u.mas
    rfc_cat["dec_error_x"].unit = u.mas
    # (5) K-band
    rfc_cat["dra_k"] = convert_offset_column(rfc_cat["dra_k"])
    rfc_cat["ddec_k"] = convert_offset_column(rfc_cat["ddec_k"])
    rfc_cat["ra_error_k"] = convert_offset_column(
        rfc_cat["ra_error_k"])
    rfc_cat["dec_error_k"] = convert_offset_column(
        rfc_cat["dec_error_k"])
    rfc_cat["ra_dec_corr_k"] = convert_offset_column(
        rfc_cat["ra_dec_corr_k"])
    rfc_cat["dra_k"].unit = u.mas
    rfc_cat["ddec_k"].unit = u.mas
    rfc_cat["ra_error_k"].unit = u.mas
    rfc_cat["dec_error_k"].unit = u.mas

    return rfc_cat


# -------------------------------- MAIN --------------------------------
if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
