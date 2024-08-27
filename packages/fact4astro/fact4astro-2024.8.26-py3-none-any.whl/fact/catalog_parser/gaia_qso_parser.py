#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: read_gaia.py
"""
Module to read and process Gaia catalog data for ICRF sources.

Created on Thu Oct  4 16:00:02 2018

Author: Neo (liuniu@smail.nju.edu.cn)

This module provides functions to access and process Gaia data (DR1, DR2, EDR3, DR3)
for ICRF sources, including online queries and local file processing.

History:
2024-01-21: Updated to use astroquery for direct access to online data.
"""

import os
import numpy as np
from astropy.table import Table
from astropy import units as u
from astroquery.gaia import Gaia

from .config import get_cat_dir, load_cfg

# from ..cat_tools import gaia_ga_corr
# from ..cat_tools import nor_sep_calc
from ..catalog_utils.error_ellipse import compute_error_ellipse_par

Gaia.ROW_LIMIT = -1


__all__ = ["read_gaia_icrf"]


# -----------------------------  FUNCTIONS -----------------------------
def rename_columns(gaia_table):
    """
    Rename columns in the Gaia table to standardize the naming convention.

    Parameters
    ----------
    gaia_table : astropy.table.Table
        The Gaia data table with original column names.

    Returns
    -------
    gaia_table : astropy.table.Table
        The Gaia data table with renamed columns.
    """

    gaia_table.rename_columns(["ra_error", "dec_error", ],
                              ["ra_err", "dec_err",])

    if "pmra" in gaia_table.colnames:
        gaia_table.rename_columns(["pmra_error", "pmdec_error"],
                                  ["pmra_err", "pmdec_err"])

    if "parallax" in gaia_table.colnames:
        gaia_table.rename_columns(["parallax", "parallax_error"],
                                  ["plx", "plx_err"])

    return gaia_table


def read_gdr1_qso(oneline_query=False, gdr1_qso_file=None, calc_pos_eepm=False):
    """
    Read positional information of Gaia DR1 quasar auxiliary solution.

    Parameters
    ----------
    oneline_query : bool, optional
        If True, perform an online query using astroquery.
    gdr1_qso_file : str, optional
        Path to the Gaia DR1 quasar auxiliary solution file.
    calc_pos_eepm : bool, optional
        If True, calculate the position error ellipse parameters.

    Returns
    -------
    gdr1_table : astropy.table.Table
        The Gaia DR1 quasar data table.
    """

    if oneline_query:
        print("[msg] Use astroquery to perform online query")
        job = Gaia.launch_job_async(
            "select * from gaiadr1.aux_qso_icrf2_match")
        gdr1_table = job.get_results()

    else:
        if gdr1_qso_file is None:
            raise FileNotFoundError(
                "No file path provided for Gaia DR1 quasar data.")
        else:
            # Parse local ascii file
            gdr1_table = Table.read(gdr1_qso_file, format="ascii.fixed_width_no_header",
                                    names=["solution_id", "source_id", "ref_epoch",
                                           "ra", "ra_error", "dec", "dec_error",
                                           "ra_dec_corr", "phot_g_mean_mag",
                                           "astrometric_priors_used", "icrf2_match",
                                           "rot_flag"])

        # Add unit information
        gdr1_table["ra_error"].unit = u.mas
        gdr1_table["dec_error"].unit = u.mas

    # Rename some columns
    gdr1_table = rename_columns(gdr1_table)

    # Add the semi-major axis of error ellipse to the table
    if calc_pos_eepm:
        gdr1_table = compute_error_ellipse_par(gdr1_table, indexes=[9, 9, 9])

    return gdr1_table


def read_gdr2_iers(oneline_query=False, gdr2_iers_file=None, error_scaling=False, calc_pos_eepm=False):
    """
    Read positional information from Gaia DR2 auxiliary IERS catalog.

    Parameters
    ----------
    oneline_query : bool, optional
        If True, perform an online query using astroquery.
    gdr2_iers_file : str, optional
        Path to the Gaia DR2 auxiliary IERS catalog file.
    error_scaling : bool, optional
        If True, scale Gaia position errors by chi2/ndf.
    calc_pos_eepm : bool, optional
        If True, calculate the position error ellipse parameters.

    Returns
    -------
    gdr2_table : astropy.table.Table
        The Gaia DR2 auxiliary IERS catalog data table.
    """

    if oneline_query:
        print("[msg] Use astroquery to perform online query")
        job = Gaia.launch_job_async(
            "select qso.iers_name,gaia.* from gaiadr2.aux_iers_gdr2_cross_id as qso, gaiadr2.gaia_source as gaia where qso.source_id=gaia.source_id")
        gdr2_table = job.get_results()
        # gdr2_table.rename_column("SOURCE_ID", "source_id")
    else:

        if gdr2_iers_file is None:
            # Read Gaia DR2 IERS quasar data
            gdr2_table = Table.read(gdr2_iers_file)

    # Only the positional information are kept.
    # gdr2_table.keep_columns(["iers_name", "source_id",
    #                          "ra", "ra_error", "dec", "dec_error",
    #                          "parallax", "parallax_error",
    #                          "pmra", "pmra_error", "pmdec", "pmdec_error",
    #                          "ra_dec_corr", "ra_parallax_corr", "ra_pmra_corr",
    #                          "ra_pmdec_corr", "dec_parallax_corr", "dec_pmra_corr",
    #                          "dec_pmdec_corr", "parallax_pmra_corr",
    #                          "parallax_pmdec_corr", "pmra_pmdec_corr",
    #                          "phot_g_mean_mag", "phot_bp_mean_mag", "phot_rp_mean_mag",
    #                          "bp_rp", "astrometric_n_obs_al", "astrometric_n_good_obs_al",
    #                          "astrometric_matched_observations", "astrometric_chi2_al",
    #                          "astrometric_params_solved"])

    # Rename some columns
    gdr2_table = rename_columns(gdr2_table)

    # There are two small errore in the colomn iers_name in this sample
    # 0548+37A --> 0548+377
    # 1954+188 --> 1954+187

    oldnames = ["0548+37A", "1954+188"]
    newnames = ["0548+377", "1954+187"]

    for oldname, newname in zip(oldnames, newnames):
        idx = np.where(gdr2_table["iers_name"] == oldname)[0][0]
        gdr2_table[idx]["iers_name"] = newname

    # Determine whether to scale the position error
    if error_scaling:
        # Degree of freedom = #observation - #parameter
        dof = gdr2_table["astrometric_n_good_obs_al"] - \
            gdr2_table["astrometric_params_solved"]
        scale = np.sqrt(gdr2_table["astrometric_chi2_al"] / dof)

        gdr2_table["ra_err"] = gdr2_table["ra_err"] * scale
        gdr2_table["dec_err"] = gdr2_table["dec_err"] * scale

    # Add the semi-major axis of error ellipse to the table
    if calc_pos_eepm:
        gdr2_table = compute_error_ellipse_par(gdr2_table, indexes=[9, 9, 9])

    return gdr2_table


def read_gedr3_icrf3_sou(oneline_query=False, gedr3_icrf_file=None, radio_band="all", calc_pos_eepm=False):
    """
    Read data for ICRF3 sources in Gaia EDR3 catalog.

    Parameters
    ----------
    oneline_query: bool, optional
        If True, perform an online query using astroquery.
    gedr3_icrf_file: str, optional
        Path to the Gaia EDR3 ICRF3 sources file.
    radio_band: str, optional, default "all"
        The radio band of the ICRF sources(S/X, K, X/Ka, or all).
    calc_pos_eepm: bool, optional
        If True, calculate the position error ellipse parameters.

    Returns
    -------
    gedr3_table: astropy.table.Table
        The Gaia EDR3 ICRF3 source data table.
    """

    if oneline_query:
        # Determine the query conditions from the radio band
        if radio_band in ["sx", "SX", "S/X", "s/x"]:
            query_cond = "qso.catalogue_name='ICRF3 S/X'"
        elif radio_band in ["k", "K"]:
            query_cond = "qso.catalogue_name='ICRF3 K'"
        elif radio_band in ["xka", "XKa", "XKA", "X/KA", "X/Ka", "x/ka"]:
            query_cond = "qso.catalogue_name='ICRF3 X/Ka'"
        elif radio_band in ["all", "ALL"]:
            query_cond = "(qso.catalogue_name='ICRF3 S/X' or qso.catalogue_name='ICRF3 K' or qso.catalogue_name='ICRF3 X/Ka')"
        else:
            print(f"recongnized radio_band {radio_band}")

        job = Gaia.launch_job_async(
            "select qso.source_name_in_catalogue,qso.catalogue_name,gaia.* "
            "from gaiaedr3.agn_cross_id as qso, gaiaedr3.gaia_source as gaia "
            f"where {query_cond} and gaia.source_id=qso.source_id")
        gedr3_table = job.get_results()

    else:
        if gedr3_icrf_file is None:
            cfg = load_cfg()

            if cfg["cat_file_path"]["gdr3_icrf"] and os.path.isfile(cfg["cat_file_path"]["gdr3_icrf"]):
                gedr3_icrf_file = cfg["cat_file_path"]["gdr3_icrf"]
            else:
                data_dir = get_cat_dir()
                if os.path.isfile(f"{data_dir}/gaia/edr3/gaia_edr3_icrf3_source.fits"):
                    gedr3_icrf_file = f"{data_dir}/gaia/edr3/gaia_edr3_icrf3_source.fits"
                else:
                    print("Cannot find the data file of Gaia DR3 ICRF sources.")
                    os.exit()

        # Read Gaia edr3 quasar data
        gedr3_table = Table.read(gedr3_icrf_file)

    # Rename some columns
    gedr3_table = rename_columns(gedr3_table)

    # Add the semi-major axis of error ellipse to the table
    if calc_pos_eepm:
        gedr3_table = compute_error_ellipse_par(
            gedr3_table, indexes=[13, 13, 13])

    return gedr3_table


def read_gdr3_icrf3_sou(oneline_query=False, gdr3_icrf_file=None, radio_band="all", calc_pos_eepm=False):
    """
    Read data for ICRF3 sources in Gaia DR3 catalog.

    Parameters
    ----------
    oneline_query: bool, optional
        If True, perform an online query using astroquery.
    gedr3_icrf_file: str, optional
        Path to the Gaia EDR3 ICRF3 sources file.
    radio_band: str, optional, default "all"
        The radio band of the ICRF sources(S/X, K, X/Ka, or all).
    calc_pos_eepm: bool, optional
        If True, calculate the position error ellipse parameters.

    Returns
    -------
    gedr3_table: astropy.table.Table
        The Gaia EDR3 ICRF3 source data table.
    """

    if oneline_query:
        # Determine the query conditions from the radio band
        if radio_band in ["sx", "SX", "S/X", "s/x"]:
            query_cond = "qso.catalogue_name='ICRF3 S/X'"
        elif radio_band in ["k", "K"]:
            query_cond = "qso.catalogue_name='ICRF3 K'"
        elif radio_band in ["xka", "XKa", "XKA", "X/KA", "X/Ka", "x/ka"]:
            query_cond = "qso.catalogue_name='ICRF3 X/Ka'"
        elif radio_band in ["all", "ALL"]:
            query_cond = "(qso.catalogue_name='ICRF3 S/X' or qso.catalogue_name='ICRF3 K' or qso.catalogue_name='ICRF3 X/Ka')"
        else:
            raise ValueError(f"Unrecognized radio_band: {radio_band}")

        job = Gaia.launch_job_async(
            "select qso.source_name_in_catalogue,qso.catalogue_name,gaia.* "
            "from gaiadr3.agn_cross_id as qso, gaiadr3.gaia_source as gaia "
            f"where {query_cond} and gaia.source_id=qso.source_id")
        gdr3_table = job.get_results()

    else:
        if gdr3_icrf_file is None:
            cfg = load_cfg()

            if cfg["cat_file_path"]["gdr3_icrf"] and os.path.isfile(cfg["cat_file_path"]["gdr3_icrf"]):
                gdr3_icrf_file = cfg["cat_file_path"]["gdr3_icrf"]
            else:
                data_dir = get_cat_dir()
                if os.path.isfile(f"{data_dir}/gaia/edr3/gaia_edr3_icrf3_source.fits"):
                    gdr3_icrf_file = f"{data_dir}/gaia/edr3/gaia_edr3_icrf3_source.fits"
                else:
                    raise FileNotFoundError(
                        "Cannot find the data file of Gaia EDR3 ICRF3 sources.")

        # Read Gaia edr3 quasar data
        gdr3_table = Table.read(gdr3_icrf_file)

    # Rename some columns
    gdr3_table = rename_columns(gdr3_table)

    # Add the semi-major axis of error ellipse to the table
    if calc_pos_eepm:
        gdr3_table = compute_error_ellipse_par(
            gdr3_table, indexes=[13, 13, 13])

    return gdr3_table


def read_gaia_icrf(version=3, oneline_query=False, gaia_icrf_file=None, calc_pos_eepm=False, error_scaling=False, radio_band="all"):
    """
    Read Gaia astrometric data of ICRF sources.

    Parameters
    ----------
    version: int, optional
        Version of the Gaia data release(1 for DR1, 2 for DR2, 2.5 for EDR3, 3 for DR3).
    oneline_query: bool, optional
        If True, perform an online query using astroquery.
    gaia_icrf_file: str, optional
        Path to the Gaia ICRF source file.
    calc_pos_eepm: bool, optional
        If True, calculate the position error ellipse parameters.
    error_scaling: bool, optional
        If True, scale Gaia position errors by chi2/ndf.
    radio_band: str, optional
        The radio band of the ICRF sources(applicable for DR3).

    Returns
    -------
    gaia_icrf_table: astropy.table.Table
        The Gaia ICRF source data table.
    """
    if version == 1:
        gaia_icrf_table = read_gdr1_qso(
            oneline_query=oneline_query, gdr1_qso_file=gaia_icrf_file, calc_pos_eepm=calc_pos_eepm
        )
    elif version == 2:
        gaia_icrf_table = read_gdr2_iers(
            oneline_query=oneline_query, gdr2_iers_file=gaia_icrf_file, error_scaling=error_scaling, calc_pos_eepm=calc_pos_eepm
        )
    elif version == 2.5:
        gaia_icrf_table = read_gedr3_icrf3_sou(
            oneline_query=oneline_query, gedr3_icrf_file=gaia_icrf_file, calc_pos_eepm=calc_pos_eepm, radio_band=radio_band
        )
    elif version == 3:
        gaia_icrf_table = read_gdr3_icrf3_sou(
            oneline_query=oneline_query, gdr3_icrf_file=gaia_icrf_file, calc_pos_eepm=calc_pos_eepm, radio_band=radio_band
        )
    else:
        raise ValueError(
            f"Unknown data version {version}. Supported values are 1 (DR1), 2 (DR2), 2.5 (EDR3), and 3 (DR3)."
        )

    return gaia_icrf_table


def read_dr2_allwise(oneline_query=False, gdr2_qso_file=None, calc_pos_eepm=False):
    """Read the positional information of Gaia DR2 auxiliary AllWISE catalog.

    Parameter
    ---------
    gdr2_qso_file: string
        file name and path of the Gaia DR2 auxiliary AllWISE catalog

    Return
    ------
    gdr2: an astropy.Table object
        data in the catalog
    """

    if oneline_query:
        print("[msg] Use astroquery to perform online query")
        job = Gaia.launch_job_async(
            "select gaia.*,qso.* from gaiaedr3.frame_rotator_source as qso, gaiaedr3.gaia_source as gaia where qso.source_id=gaia.source_id")
        gdr2_table = job.get_results()

    else:
        if gdr2_qso_file is None:
            cfg = load_cfg()

            if cfg["cat_file_path"]["gdr2_agn"] and os.path.isfile(cfg["cat_file_path"]["gdr2_agn"]):
                gdr2_qso_file = cfg["cat_file_path"]["gdr2_agn"]
            else:
                data_dir = get_cat_dir()
                if os.path.isfile(f"{data_dir}/gaia/dr2/gaiadr2_qso_all.fits"):
                    gdr2_qso_file = f"{data_dir}/gaia/dr2/gaiadr2_qso_all.fits"
                else:
                    print("Cannot find the data file of Gaia DR2 X AllWISE sources.")
                    os.exit()

        # Read Gaia DR2 quasar data
        gdr2_table = Table.read(gdr2_qso_file)

    # Rename some columns
    gdr2_table = rename_columns(gdr2_table)

    # Add the semi-major axis of error ellipse to the table
    if calc_pos_eepm:
        gdr2_table = compute_error_ellipse_par(gdr2_table, indexes=[9, 9, 9])

    return gdr2_table


def read_gedr3_crf(oneline_query=False, gedr3_icrf_file=None, table_type="all", calc_pos_eepm=False, only_used_sou=False):
    """Read data for Gaia-CRF3 sources in Gaia edr3 catalog.

    Parameter
    ---------
    gedr3_qso_file: string
        file name and path
    table_type: string
        flag to tell if return subset, could be "all", "orientation", "spin"
    calc_pos_eepm: Boolean
        flag to tell if calculate the position error ellipse parameters
    only_used_sou: boolean
        flag to decide whether to keep only those sources used for calculating
        the orientation and spin parameters for Gaia-CRF3

    Return
    ------
    gedr3: an astropy.Table object
        data in the catalog
    """

    if oneline_query:
        job = Gaia.launch_job_async(
            "select gaia.*,qso.* from gaiaedr3.frame_rotator_source as qso, gaiaedr3.gaia_source as gaia where qso.source_id=gaia.source_id")
        gedr3_table = job.get_results()

    else:
        if gedr3_icrf_file is None:
            cfg = load_cfg()

            if cfg["cat_file_path"]["gdr3_crf"] and os.path.isfile(cfg["cat_file_path"]["gdr3_crf"]):
                gedr3_icrf_file = cfg["cat_file_path"]["gdr3_crf"]
            else:
                data_dir = get_cat_dir()
                if os.path.isfile(f"{data_dir}/gaia/edr3/gedr3_frame_rotator_source.fits"):
                    gedr3_icrf_file = f"{data_dir}/gaia/edr3/gedr3_frame_rotator_source.fits"
                else:
                    print("Cannot find the data file of Gaia DR3 ICRF sources.")
                    os.exit()

        # Read Gaia edr3 quasar data
        gedr3_table = Table.read(gedr3_icrf_file)

    # Check which subset should be used
    if table_type == "orientation":
        if only_used_sou:
            mask = gedr3_table["used_for_reference_frame_orientation"]
        else:
            mask = gedr3_table["considered_for_reference_frame_orientation"]

    elif table_type == "spin":
        if only_used_sou:
            mask = gedr3_table["used_for_reference_frame_spin"]
        else:
            mask = gedr3_table["considered_for_reference_frame_spin"]

    else:
        if only_used_sou:
            mask1 = gedr3_table["used_for_reference_frame_orientation"]
            mask2 = gedr3_table["used_for_reference_frame_spin"]
        else:
            mask1 = gedr3_table["considered_for_reference_frame_orientation"]
            mask2 = gedr3_table["considered_for_reference_frame_spin"]
        mask = (mask1 | mask2)

    gedr3_table = gedr3_table[mask]
    # Rename some columns
    gedr3_table = rename_columns(gedr3_table)

    # Calculate the semi-major axis of error ellipse for position
    if calc_pos_eepm:
        gedr3_table = compute_error_ellipse_par(gedr3_table, indexes=[9, 9, 9])

    # return gedr3_table


def read_gedr3_agn(gedr3_qso_file=None, calc_pos_eepm=False, calc_nor_pm=False):
    """Read positional information for AGN in Gaia edr3 catalog.

    Parameter
    ---------
    gedr3_qso_file: string
        file name and path
    calc_nor_pm: boolean
        flag to tell if calculate the normalized proper motion

    Return
    ------
    gedr3: an astropy.Table object
        data in the catalog
    """

    if gedr3_qso_file is None:
        cfg = load_cfg()

        if cfg["cat_file_path"]["gdr3_icrf"] and os.path.isfile(cfg["cat_file_path"]["gdr3_icrf"]):
            gedr3_qso_file = cfg["cat_file_path"]["gdr3_icrf"]
        else:
            data_dir = get_cat_dir()
            if os.path.isfile(f"{data_dir}/gaia/edr3/gedr3_agn.fits"):
                gedr3_qso_file = f"{data_dir}/gaia/edr3/gedr3_agn.fits"
            else:
                print("Cannot find the data file of Gaia EDR3 ICRF sources.")

    # Read Gaia edr3 quasar data
    gedr3_table = Table.read(gedr3_qso_file)

    # Rename some columns
    gedr3_table = rename_columns(gedr3_table)

    # Calculate the semi-major axis of error ellipse
    if calc_pos_eepm:
        gedr3_table = compute_error_ellipse_par(gedr3_table, indexes=[9, 9, 9])

    # Calculate the normalized proper motion
    # This is a quantity similar to normalized separation
    # if calc_nor_pm:
    #     data = nor_sep_calc(gedr3_table["pmra"], gedr3_table["pmra_err"],
    #                         gedr3_table["pmdec"], gedr3_table["pmdec_err"], gedr3_table["pmra_pmdec_corr"])
    #     nor_pm = Column(data[3], name="nor_pm", unit=None)
    #     gedr3_table.add_column(nor_pm)

    #     # GA-effect correction
    #     gedr3_table = gaia_ga_corr(gedr3_table)

    return gedr3_table


# -------------------------------- MAIN --------------------------------

if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------


if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
