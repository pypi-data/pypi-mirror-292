#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: read_gaia.py
"""
Created on Thu Oct  4 16:00:02 2018

@author: Neo(liuniu@smail.nju.edu.cn)

History:
2024-01-21: Use astroquery to get access to online data directly
"""

import numpy as np
from astropy.table import Table, Column
from astropy import units as u
from astroquery.gaia import Gaia

from .cat_vars import get_data_dir

# from ..cat_tools import gaia_ga_corr
# from ..cat_tools import nor_sep_calc
from ...src.fact.catalog_utils import compute_error_ellipse_par


Gaia.ROW_LIMIT = -1

# from astropy.coordinates import SkyCoord


__all__ = ["read_dr1_qso", "read_dr2_iers", "read_dr2_allwise",
           "read_edr3_agn", "read_edr3_crf", "read_edr3_icrf3_sou"]


# -----------------------------  FUNCTIONS -----------------------------
def read_dr1_qso(dr1_qso_file=None):
    """Read the position information of Gaia DR1 quasar auxiliary solution.

    Parameter
    ---------
    dr1_qso_file : string
        file name and path of the Gaia DR1 quasar auxiliary solution

    Return
    ------
    gdr1 : an astropy.Table object
        data in the catalog
    """

    if dr1_qso_file is None:
        # Perfrom asynchronous query
        print("[msg] Use astroquery to perform online query")
        job = Gaia.launch_job_async(
            "select * from gaiadr1.aux_qso_icrf2_match")
        gdr1 = job.get_results()
    else:
        # Parse local ascii file
        gdr1 = Table.read(dr1_qso_file, format="ascii.fixed_width_no_header",
                          names=["solution_id", "source_id", "ref_epoch",
                                 "ra", "ra_error", "dec", "dec_error",
                                 "ra_dec_corr", "phot_g_mean_mag",
                                 "astrometric_priors_used", "icrf2_match",
                                 "rot_flag"])

        # Add unit information
        gdr1["ra_error"].unit = u.mas
        gdr1["dec_error"].unit = u.mas

    # Add the semi-major axis of error ellipse to the table
    gdr1 = compute_error_ellipse_par(gdr1, indexes=[9, 9, 9])

    return gdr1


def read_dr2_iers(dr2_qso_file=None, error_scaling=False):
    """Read the positional information of Gaia DR2 auxiliary IERS catalog.

    Parameter
    ---------
    dr2_qso_file : string
        file name and path of the Gaia DR2 auxiliary IERS catalog
    error_scaling : boolean
        if true, scale gaia position error by chi2/ndf

    Return
    ------
    gdr2 : an astropy.Table object
        data in the catalog
    """

    if dr2_qso_file is None:
        print("[msg] Use astroquery to perform online query")
        job = Gaia.launch_job_async(
            "select qso.iers_name,gaia.* from gaiadr2.aux_iers_gdr2_cross_id as qso, gaiadr2.gaia_source as gaia where qso.source_id=gaia.source_id")
        gdr2 = job.get_results()

    else:
        # Read Gaia DR2 IERS quasar data
        gdr2 = Table.read(dr2_qso_file)

    # Only the positional information are kept.
    gdr2.keep_columns(["iers_name", "source_id",
                       "ra", "ra_error", "dec", "dec_error",
                       "parallax", "parallax_error",
                       "pmra", "pmra_error", "pmdec", "pmdec_error",
                       "ra_dec_corr", "ra_parallax_corr", "ra_pmra_corr",
                       "ra_pmdec_corr", "dec_parallax_corr", "dec_pmra_corr",
                       "dec_pmdec_corr", "parallax_pmra_corr",
                       "parallax_pmdec_corr", "pmra_pmdec_corr",
                       "phot_g_mean_mag", "phot_bp_mean_mag", "phot_rp_mean_mag",
                       "bp_rp", "astrometric_n_obs_al", "astrometric_n_good_obs_al",
                       "astrometric_matched_observations", "astrometric_chi2_al",
                       "astrometric_params_solved"])

    # There are two small errore in the colomn iers_name in this sample
    # 0548+37A --> 0548+377
    # 1954+188 --> 1954+187

    oldnames = ["0548+37A", "1954+188"]
    newnames = ["0548+377", "1954+187"]

    for oldname, newname in zip(oldnames, newnames):
        idx = np.where(gdr2["iers_name"] == oldname)[0][0]
        gdr2[idx]["iers_name"] = newname

    # Determine whether to scale the position error
    if error_scaling:
        # Degree of freedom = #observation - #parameter
        dof = gdr2["astrometric_n_good_obs_al"] - \
            gdr2["astrometric_params_solved"]
        scale = np.sqrt(gdr2["astrometric_chi2_al"] / dof)

        gdr2["ra_error"] = gdr2["ra_error"] * scale
        gdr2["dec_error"] = gdr2["dec_error"] * scale

    # Add the semi-major axis of error ellipse to the table
    gdr2 = compute_error_ellipse_par(gdr2, indexes=[9, 9, 9])

    return gdr2


def read_dr2_allwise(dr2_qso_file=None):
    """Read the positional information of Gaia DR2 auxiliary AllWISE catalog.

    Parameter
    ---------
    dr2_qso_file : string
        file name and path of the Gaia DR2 auxiliary AllWISE catalog

    Return
    ------
    gdr2 : an astropy.Table object
        data in the catalog
    """

    if dr2_qso_file is None:
        data_dir = get_data_dir()
        dr2_qso_file = "{}/gaia/dr2/gaiadr2_qso_all.fits".format(data_dir)

    # Read Gaia DR2 quasar data
    gdr2 = Table.read(dr2_qso_file)

    # Add the semi-major axis of error ellipse to the table
    gdr2 = compute_error_ellipse_par(gdr2, indexes=[9, 9, 9])

    return gdr2


def read_edr3_icrf3_sou(edr3_qso_file=None, oneline_query=False, band="all"):
    """Read data for ICRF3 sources in Gaia EDR3 catalog.

    Parameter
    ---------
    calc_pos_err: Boolean
        flag to tell if calculate the position error ellipse parameters
    calc_nor_pm: boolean
        flag to tell if calculate the normalized proper motion

    Return
    ------
    gedr3 : an astropy.Table object
        data in the catalog
    """

    if edr3_qso_file is None:
        if oneline_query:
            if band in ["sx", "SX", "S/X", "s/x"]:
                job = Gaia.launch_job_async(
                    "select qso.source_name_in_catalogue,qso.catalogue_name,gaia.* "
                    "from gaiaedr3.agn_cross_id as qso, gaiaedr3.gaia_source as gaia "
                    "where qso.catalogue_name='ICRF3 S/X' and gaia.source_id=qso.source_id")
            elif band in ["k", "K"]:
                job = Gaia.launch_job_async(
                    "select qso.source_name_in_catalogue,qso.catalogue_name,gaia.* "
                    "from gaiaedr3.agn_cross_id as qso, gaiaedr3.gaia_source as gaia "
                    "where qso.catalogue_name='ICRF3 K' and gaia.source_id=qso.source_id")
            elif band in ["xka", "XKa", "XKA", "X/KA", "X/Ka", "x/ka"]:
                job = Gaia.launch_job_async(
                    "select qso.source_name_in_catalogue,qso.catalogue_name,gaia.* "
                    "from gaiaedr3.agn_cross_id as qso, gaiaedr3.gaia_source as gaia "
                    "where qso.catalogue_name='ICRF3 X/Ka' and gaia.source_id=qso.source_id")
            else:
                job = Gaia.launch_job_async(
                    "select qso.source_name_in_catalogue,qso.catalogue_name,gaia.* "
                    "from gaiaedr3.agn_cross_id as qso, gaiaedr3.gaia_source as gaia "
                    "where (qso.catalogue_name='ICRF3 S/X' or qso.catalogue_name='ICRF3 K' "
                    "or qso.catalogue_name='ICRF3 X/Ka') and gaia.source_id=qso.source_id")
            gedr3 = job.get_results()
        else:
            data_dir = get_data_dir()
            edr3_qso_file = "{}/gaia/edr3/gaia_edr3_icrf3_source.fits".format(
                data_dir)
            # Read Gaia edr3 quasar data
            gedr3 = Table.read(edr3_qso_file)
    else:
        # Read Gaia edr3 quasar data
        gedr3 = Table.read(edr3_qso_file)

    # Add the semi-major axis of error ellipse to the table
    gedr3 = compute_error_ellipse_par(gedr3, indexes=[13, 13, 13])

    return gedr3


def read_edr3_crf(edr3_qso_file=None, table_type="all", calc_pos_err=False,
                  only_used_sou=False):
    """Read data for Gaia-CRF3 sources in Gaia edr3 catalog.

    Parameter
    ---------
    edr3_qso_file : string
        file name and path
    table_type : string
        flag to tell if return subset, could be "all", "orientation", "spin"
    calc_pos_err: Boolean
        flag to tell if calculate the position error ellipse parameters
    only_used_sou : boolean
        flag to decide whether to keep only those sources used for calculating
        the orientation and spin parameters for Gaia-CRF3

    Return
    ------
    gedr3 : an astropy.Table object
        data in the catalog
    """

    if edr3_qso_file is None:
        # data_dir = get_data_dir()
        # edr3_qso_file = "{}/gaia/edr3/gedr3_frame_rotator_source.fits".format(
        #     data_dir)
        job = Gaia.launch_job_async(
            "select gaia.*,qso.* from gaiaedr3.frame_rotator_source as qso, gaiaedr3.gaia_source as gaia where qso.source_id=gaia.source_id")
        gedr3 = job.get_results()
    else:
        # Read Gaia edr3 quasar data
        gedr3 = Table.read(edr3_qso_file)

    # Check which subset should be used
    if table_type == "orientation":
        if only_used_sou:
            mask = gedr3["used_for_reference_frame_orientation"]
        else:
            mask = gedr3["considered_for_reference_frame_orientation"]

    elif table_type == "spin":
        if only_used_sou:
            mask = gedr3["used_for_reference_frame_spin"]
        else:
            mask = gedr3["considered_for_reference_frame_spin"]

    else:
        if only_used_sou:
            mask1 = gedr3["used_for_reference_frame_orientation"]
            mask2 = gedr3["used_for_reference_frame_spin"]
        else:
            mask1 = gedr3["considered_for_reference_frame_orientation"]
            mask2 = gedr3["considered_for_reference_frame_spin"]
        mask = (mask1 | mask2)

    gedr3 = gedr3[mask]

    # Calculate the semi-major axis of error ellipse for position
    if calc_pos_err:
        gedr3 = compute_error_ellipse_par(gedr3, indexes=[9, 9, 9])

    return gedr3


def read_edr3_agn(edr3_qso_file=None):
    """Read positional information for AGN in Gaia edr3 catalog.

    Parameter
    ---------
    edr3_qso_file : string
        file name and path

    Return
    ------
    gedr3 : an astropy.Table object
        data in the catalog
    """

    if edr3_qso_file is None:
        data_dir = get_data_dir()
        edr3_qso_file = "{}/gaia/edr3/gedr3_agn.fits".format(data_dir)

    # Read Gaia edr3 quasar data
    gedr3 = Table.read(edr3_qso_file)

    # Add the semi-major axis of error ellipse to the table
    gedr3 = compute_error_ellipse_par(gedr3, indexes=[9, 9, 9])

    return gedr3


def read_edr3_agn(edr3_qso_file=None, calc_nor_pm=False):
    """Read positional information for AGN in Gaia edr3 catalog.

    Parameter
    ---------
    edr3_qso_file : string
        file name and path
    calc_nor_pm: boolean
        flag to tell if calculate the normalized proper motion

    Return
    ------
    gedr3 : an astropy.Table object
        data in the catalog
    """

    if edr3_qso_file is None:
        data_dir = get_data_dir()
        edr3_qso_file = "{}/gaia/edr3/gedr3_agn.fits".format(data_dir)

    # Read Gaia edr3 quasar data
    gedr3 = Table.read(edr3_qso_file)

    # Calculate the semi-major axis of error ellipse
    gedr3 = compute_error_ellipse_par(gedr3, indexes=[9, 9, 9])

    # Calculate the normalized proper motion
    # This is a quantity similar to normalized separation
    # if calc_nor_pm:
    #     data = nor_sep_calc(gedr3["pmra"], gedr3["pmra_err"],
    #                         gedr3["pmdec"], gedr3["pmdec_err"], gedr3["pmra_pmdec_corr"])
    #     nor_pm = Column(data[3], name="nor_pm", unit=None)
    #     gedr3.add_column(nor_pm)

    #     # GA-effect correction
    #     gedr3 = gaia_ga_corr(gedr3)

    return gedr3


if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
