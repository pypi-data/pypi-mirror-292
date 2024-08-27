#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: read_icrf.py
"""
Created on Sat Sep 29 18:15:50 2018

@author: Neo(liuniu@nju.edu.cn)

History
-------
2023-11-21: Remove the cfg configuration
2024-01-21: Rename columns (ra_err->ra_err, dec_err->dec_err) to be consistent with Gaia 
            catalog
"""

import os

import numpy as np
from astropy.table import Table, Column
from astropy import units as u
from astropy.coordinates import SkyCoord

# my modules
from .data_downloader import download_online_data
from ..catalog_utils.error_ellipse import compute_error_ellipse_par
from .config import load_cfg

__all__ = ["read_icrf1", "read_icrf2", "read_icrf3", "read_icrf"]


# -----------------------------  FUNCTIONS -----------------------------
def parse_radec_str(icrf_file, col_start_index, col_end_index, data_start_index=0):
    """
    Convert strings of RA/Dec into astropy Columns.

    Parameters
    ----------
    icrf_file : str
        Path to the ICRF file.
    col_start_index : int
        The starting column index of the RA/Dec string.
    col_end_index : int
        The ending column index of the RA/Dec string.
    data_start_index : int, optional
        The index of the first data row to be read, by default 0.

    Returns
    -------
    ra : astropy.table.Column
        Right ascension column.
    dec : astropy.table.Column
        Declination column.
    """
    ra_dec_str = Table.read(icrf_file, format="ascii.fixed_width_no_header",
                            names=["ra_dec"], col_starts=[col_start_index], col_ends=[col_end_index],
                            data_start=data_start_index)

    ra_dec = SkyCoord(ra_dec_str["ra_dec"], unit=(u.hourangle, u.deg))
    ra = Column(ra_dec.ra, name="ra")
    dec = Column(ra_dec.dec, name="dec")

    return ra, dec


def correct_pos_err(icrf_cat, dec):
    """
    Correct RA error and add unit information to the catalog.

    Parameters
    ----------
    icrf_cat : astropy.table.Table
        The ICRF catalog data.
    dec : astropy.table.Column
        The declination column.

    Returns
    -------
    icrf_cat : astropy.table.Table
        The corrected ICRF catalog with units added to the error columns.
    """
    icrf_cat["ra_err"] = icrf_cat["ra_err"] * 15e3 * np.cos(dec.to("rad"))
    icrf_cat["ra_err"].unit = u.mas
    icrf_cat["dec_err"].unit = u.arcsec
    icrf_cat["dec_err"] = icrf_cat["dec_err"].to(u.mas)

    return icrf_cat


def read_icrf1(icrf1_file=None, ext=None, calc_pos_eepm=False):
    """
    Read the ICRF1 catalog.

    Parameters
    ----------
    icrf1_file : str, optional
        The file name and path of the ICRF1 catalog. If None, it will be downloaded.
    ext : int, optional
        The extension version of the ICRF1 catalog, by default None.
    calc_pos_eepm : bool, optional
        If True, compute the error ellipse parameters, by default False.

    Returns
    -------
    icrf1 : astropy.table.Table
        The ICRF1 catalog data.
    """
    if icrf1_file is None:
        cfg = load_cfg()

        if ext is None:
            icrf_url = cfg["online_url"]["icrf1_all"]
            data_start_index = 20
            col_starts = [5, 24, 34, 37, 39, 79,
                          89, 98, 104, 112, 120, 128, 134]
            col_ends = [21, 32, 35, 38, 40, 87,
                        95, 102, 110, 119, 126, 132, 140]
            ra_index, dec_index = 42, 73
            col_names = ["iau_name", "iers_name", "type", "si_s", "si_x",
                         "ra_err", "dec_err", "ra_dec_corr",
                         "mean_obs", "beg_obs", "end_obs",
                         "nb_sess", "nb_del"]
        elif ext == 1:
            icrf_url = cfg["online_url"]["icrf1_ext1"]
            data_start_index = 22
            col_starts = [5, 24, 34, 37, 39, 76,
                          86, 95, 102, 110, 118, 126, 132]
            col_ends = [21, 32, 35, 38, 40, 83,
                        93, 100, 108, 117, 124, 130, 138]
            ra_index, dec_index = 42, 73
            col_names = ["iau_name", "iers_name", "type", "si_s", "si_x",
                         "ra_err", "dec_err", "ra_dec_corr",
                         "mean_obs", "beg_obs", "end_obs",
                         "nb_sess", "nb_del"]
        elif ext == 2:
            icrf_url = cfg["online_url"]["icrf1_ext2"]
            data_start_index = 13
            col_starts = [5, 23, 70, 82, 92, 102, 111, 121, 130, 137]
            col_ends = [21, 31, 78, 89, 98, 108, 118, 128, 135, 144]
            ra_index, dec_index = 34, 68
            col_names = ["iau_name", "iers_name", "ra_err", "dec_err", "ra_dec_corr",
                         "mean_obs", "beg_obs", "end_obs",
                         "nb_sess", "nb_del"]
        else:
            raise ValueError(f"Invalid extension number {ext} for ICRF1.")

        icrf1_file = download_online_data(icrf_url)

    icrf1_cat = Table.read(icrf1_file, format="ascii.fixed_width_no_header",
                           names=col_names, col_starts=col_starts, col_ends=col_ends,
                           data_start=data_start_index)

    ra, dec = parse_radec_str(icrf1_file, ra_index,
                              dec_index, data_start_index)
    icrf1_cat.add_columns([ra, dec], indexes=[3, 3])

    icrf1_cat = correct_pos_err(icrf1_cat, dec)
    icrf1_cat["ra_dec_corr"] = icrf1_cat["ra_dec_corr"].filled(0)

    if calc_pos_eepm:
        icrf1_cat = compute_error_ellipse_par(icrf1_cat, [8, 8, 8])

    return icrf1_cat


def read_icrf2(icrf2_file=None, calc_pos_eepm=False):
    """
    Read the ICRF2 catalog.

    Parameters
    ----------
    icrf2_file : str, optional
        The file name and path of the ICRF2 catalog. If None, it will be downloaded.
    calc_pos_eepm : bool, optional
        If True, compute the error ellipse parameters, by default False.

    Returns
    -------
    icrf2 : astropy.table.Table
        The ICRF2 catalog data.
    """
    if icrf2_file is None:
        cfg = load_cfg()

        if cfg["cat_file_path"]["icrf2"] and os.path.isfile(cfg["cat_file_path"]["icrf2"]):
            icrf2_file = cfg["cat_file_path"]["icrf2"]
        else:
            icrf_url = cfg["online_url"]["icrf2"]
            icrf2_file = download_online_data(icrf_url)

    data_start_index = 17
    icrf2_cat = Table.read(icrf2_file, format="ascii.fixed_width_no_header",
                           names=["iau_name", "iers_name", "type", "ra_err", "dec_err",
                                  "ra_dec_corr", "mean_obs", "beg_obs", "end_obs",
                                  "nb_sess", "nb_del"],
                           col_starts=[5, 23, 33, 74, 85,
                                       96, 104, 112, 120, 129, 137],
                           col_ends=[21, 31, 34, 83, 93,
                                     102, 111, 119, 127, 134, 140],
                           data_start=data_start_index)

    ra, dec = parse_radec_str(icrf2_file, 36, 72, data_start_index)
    icrf2_cat.add_columns([ra, dec], indexes=[3, 3])

    icrf2_cat = correct_pos_err(icrf2_cat, dec)

    if calc_pos_eepm:
        icrf2_cat = compute_error_ellipse_par(icrf2_cat, [8, 8, 8])

    return icrf2_cat


def read_icrf3(icrf3_file=None, band="sx", calc_pos_eepm=False):
    """
    Read the ICRF3 catalog.

    Parameters
    ----------
    icrf3_file : str, optional
        The file name and path of the ICRF3 catalog. If None, it will be downloaded.
    band : str, optional, default "sx"
        Observing band of VLBI. Can be 'sx', 'k', or 'xka'.
    calc_pos_eepm : bool, optional
        If True, compute the error ellipse parameters, by default False.

    Returns
    -------
    icrf3 : astropy.table.Table
        The ICRF3 catalog data.
    """
    if icrf3_file is None:
        cfg = load_cfg()

        if band.lower() in ["sx", "s/x"]:
            if cfg["cat_file_path"]["icrf3sx"] and os.path.isfile(cfg["cat_file_path"]["icrf3sx"]):
                icrf3_file = cfg["cat_file_path"]["icrf3sx"]
            else:
                icrf_url = cfg["online_url"]["icrf3sx"]
                icrf3_file = download_online_data(icrf_url)
        elif band.lower() == "k":
            if cfg["cat_file_path"]["icrf3k"] and os.path.isfile(cfg["cat_file_path"]["icrf3k"]):
                icrf3_file = cfg["cat_file_path"]["icrf3k"]
            else:
                icrf_url = cfg["online_url"]["icrf3k"]
                icrf3_file = download_online_data(icrf_url)
        elif band.lower() in ["xka", "x/ka"]:
            if cfg["cat_file_path"]["icrf3xka"] and os.path.isfile(cfg["cat_file_path"]["icrf3xka"]):
                icrf3_file = cfg["cat_file_path"]["icrf3xka"]
            else:
                icrf_url = cfg["online_url"]["icrf3xka"]
                icrf3_file = download_online_data(icrf_url)
        else:
            raise ValueError("Band must be 'sx', 'k', or 'xka' for ICRF3.")

    data_start_index = 16
    icrf3_cat = Table.read(icrf3_file, format="ascii.fixed_width", data_start=data_start_index,
                           names=["iau_name", "iers_name", "type", "ra_err", "dec_err",
                                  "ra_dec_corr", "mean_obs", "beg_obs", "end_obs",
                                  "nb_sess", "nb_del"],
                           col_starts=[0, 25, 35, 83, 98,
                                       108, 118, 127, 136, 145, 150],
                           col_ends=[20, 32, 35, 92, 106, 114, 124, 133, 142, 148, 155])

    ra, dec = parse_radec_str(icrf3_file, 40, 77, data_start_index)
    icrf3_cat.add_columns([ra, dec], indexes=[3, 3])

    icrf3_cat = correct_pos_err(icrf3_cat, dec)

    if calc_pos_eepm:
        icrf3_cat = compute_error_ellipse_par(icrf3_cat, [8, 8, 8])

    return icrf3_cat


def read_icrf(data_file=None, gen=3, band="sx", ext=None, calc_pos_eepm=False):
    """
    Parse the ICRF catalog.

    Parameters
    ----------
    data_file : str, optional
        Path to the catalog file on the local machine. 
        If None, the function will download the related files online.
    gen : int, default 3
        The generation of the ICRF catalog (1, 2, or 3).
    band : str, default "sx"
        Observing band of VLBI, only applicable to ICRF3 (e.g., 'sx', 'k', 'xka').
    ext : int, optional
        Extension version, only applicable to ICRF1.
    calc_pos_eepm : bool, default False
        If True, compute the error ellipse parameters.

    Returns
    -------
    icrf_cat : astropy.Table
        Parsed ICRF catalog data.

    Raises
    ------
    ValueError
        If an invalid ICRF generation is specified.
    """

    if gen == 3:
        # ICRF3
        return read_icrf3(icrf3_file=data_file, band=band, calc_pos_eepm=calc_pos_eepm)
    elif gen == 2:
        # ICRF2
        return read_icrf2(icrf2_file=data_file, calc_pos_eepm=calc_pos_eepm)
    elif gen == 1:
        # ICRF1
        return read_icrf1(icrf1_file=data_file, ext=ext, calc_pos_eepm=calc_pos_eepm)
    else:
        raise ValueError(
            f"Invalid ICRF generation: {gen}. Expected values are 1, 2, or 3.")


# -------------------------------- MAIN --------------------------------
if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
