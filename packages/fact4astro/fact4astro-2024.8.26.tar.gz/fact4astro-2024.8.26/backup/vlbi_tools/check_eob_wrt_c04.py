#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: c04_apr_calc.py
"""
Created on Sun Dec 10 18:37:34 2017

@author: Neo(liuniu@smail.nju.edu.cn)

Calculate the apriori EOP based C04 series.

History
14/06/2018 : print differences of EOP and Nutation parameters into a
             single file
07/11/2020 : Add functions for plotting offset series
"""


import numpy as np
import os
import time
import sys
from sys import platform as _platform

import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.table import Table, Column, join
from astropy import units as u
from astropy.units import cds
import requests
from scipy.interpolate import CubicSpline

# My module
# from my_progs.stat_func.rms_calc import rms_calc
from ..stat_func.rms_calc import rms_calc
from .get_dir import get_aux_dir
from .delta_tai_utc import delta_tai_utc_calc

__all__ = {"read_c04", "calc_c04_apr", "calc_c04_offset"}


# -----------------------------  FUNCTIONS -----------------------------
def download_c04():
    """Download the C04 file
    """

    datadir = get_aux_dir()
    c04_file = "{}/eopc04_IAU2000.62-now".format(datadir)

    c04_url = "http://hpiers.obspm.fr/iers/eop/eopc04/eopc04_IAU2000.62-now"

    r_data = requests.get(c04_url, stream=True)

    with open(c04_file, "w") as f_c04:
        for chunk in r_data.iter_content(chunk_size=1024):
            if chunk:
                f_c04.write(str(chunk, encoding="utf-8"))

    f_c04.close()

    print("Download C04 file successfully.")


def read_c04(c04_file=None):
    """Read EOP from C04 series.

    Parameters
    ----------
    c04_file : string
        c04 data file

    Returns
    ----------
    t_c04 : astropy.table object
    """

    if c04_file is None:
        datadir = get_aux_dir()
        c04_file = "{}/eopc04_IAU2000.62-now".format(datadir)

    if not os.path.isfile(c04_file):
        print("Couldn't find the file", c04_file)
        sys.exit()

    t_c04 = Table.read(c04_file, format="ascii", data_start=7,
                       names=["year", "month", "date", "epoch",
                              "xp", "yp", "ut1_utc", "lod", "dX", "dY",
                              "xp_err", "yp_err", "ut1_err",
                              "lod_err", "dX_err", "dY_err"])

    # Add the unit information
    # 1) Time tag
    t_c04["epoch"].unit = cds.MJD

    # 2) polar motion (wobble) and rate
    t_c04["xp"].unit = u.arcsec
    t_c04["yp"].unit = u.arcsec
    t_c04["xp_err"].unit = u.arcsec
    t_c04["yp_err"].unit = u.arcsec

    # 3) UT1-UTC and LOD
    t_c04["ut1_utc"].unit = u.second
    t_c04["ut1_err"].unit = u.second
    t_c04["lod"].unit = u.second
    t_c04["lod_err"].unit = u.second

    # 4) polar motion (wobble) and rate
    t_c04["dX"].unit = u.arcsec
    t_c04["dY"].unit = u.arcsec
    t_c04["dX_err"].unit = u.arcsec
    t_c04["dY_err"].unit = u.arcsec

    # Remove the data points which are not estimated in the solution
    mask = ((t_c04["xp_err"] != 0) & (t_c04["yp_err"] != 0)
            & (t_c04["ut1_err"] != 0) & (t_c04["lod_err"] != 0)
            & (t_c04["dX_err"] != 0) & (t_c04["dY_err"] != 0))

    t_c04 = Table(t_c04[mask], masked=False)

    return t_c04


def read_c04_array(c04_file=None):
    """Fetch the C04 series.

    Parameters
    ----------
    c04_file : string
                path and name of C04 data file.

    Returns
    ----------
    epoch_mjd : array, float
        epoch in modified Julian date
    xp : array, float
        xp position of CIP in ITRS, as
    yp : array, float
        yp position of CIP in ITRS, as
    ut : array, float
        UT1 - UTC, second
    LOD : array, float
        length of day, second
    dX : array, float
        xp component of CPO, as
    dY : array, float
        yp component of CPO, as
    """

    if c04_file is None:
        datadir = get_aux_dir()
        c04_file = "{}/eopc04_IAU2000.62-now".format(datadir)

    epoch_mjd, xp, yp, ut, lod, dX, dY = np.genfromtxt(c04_file, skip_header=14,
                                                       usecols=np.arange(3, 10),
                                                       unpack=True)

    return epoch_mjd, xp, yp, ut, lod, dX, dY


def cubic_spline(x, xs, ys):
    '''For series (xi,yi), get y(x) using cubic spline.


    Parameters
    ----------
    xs : array, float
        time series of X component
    ys : array, float
        time series of Y component
    x : float
        X position need to be interpolated

    Returns
    ---------
    Interpolated Y value.
    '''

    cs = CubicSpline(xs, ys)

    return cs(x)


def interpolate_pmr(epoch_pmr, epoch_c04, xp_c04, yp_c04, ut_c04, lod_c04):
    """Get interpolated EOP at a certain epoch.

    Parameters
    ----------
    epoch_pmr : float
        epoch to be interpolated
    poch_c04 : array, float
        20-point of epoch series in MJD
    xp_c04 : array, float
        20-point of xp series
    yp_c04 : array, float
        20-point of yp series
    ut_c04 : array, float
        20-point of UT1-UTC series
    lod_c04 : array, float
        20-point of LOD series

    Returns
    ----------
    xp_apr : float
        interpolated xp value
    yp_apr : float
        interpolated yp value
    ut_apr : float
        interpolated UT1-UTC value
    lod_apr : float
        interpolated LOD value
    """

    xp_apr = np.zeros_like(epoch_pmr)
    yp_apr = np.zeros_like(epoch_pmr)
    ut_apr = np.zeros_like(epoch_pmr)
    lod_apr = np.zeros_like(epoch_pmr)

    insert_ind = np.searchsorted(epoch_c04, epoch_pmr)

    # sort the index
    insert_ind_sort = np.sort(insert_ind)
    if insert_ind_sort[0] == 0:
        # normally it won't happen!!
        print("The epoch %f is too early for the C04 series." % epoch_pmr[0])
        sys.exit()
    elif insert_ind_sort[-1] >= epoch_c04.size:
        print("The epoch %f is too late for the C04 series "
              "so that we need to renew the C04 file." % epoch_pmr[-1])
        download_c04()

        insert_ind = np.searchsorted(epoch_c04, epoch_pmr)
        insert_ind_sort = np.sort(insert_ind)

        if insert_ind_sort[-1] >= epoch_c04.size:
            # This means the epoch to be interpolated is beyond the range of C04 series
            print("The epoch to be interpolated is beyond the range of C04 series")
            sys.exit()

    for i, ind in enumerate(insert_ind):
        if ind < 9 or epoch_c04.size - ind < 10:
            # In this case we will use less datapoints.
            pnum = min(ind, epoch_c04.size - ind)

        else:
            pnum = 10

        epoch_c04_sub = epoch_c04[ind - pnum + 1: ind + pnum + 1]

        # EOP sub-series
        xp_sub = xp_c04[ind - pnum + 1: ind + pnum + 1]
        yp_sub = yp_c04[ind - pnum + 1: ind + pnum + 1]
        ut_sub = ut_c04[ind - pnum + 1: ind + pnum + 1]
        lod_sub = lod_c04[ind - pnum + 1: ind + pnum + 1]

        # Cubic interpolation
        xp_apr[i] = cubic_spline(epoch_pmr[i], epoch_c04_sub, xp_sub)
        yp_apr[i] = cubic_spline(epoch_pmr[i], epoch_c04_sub, yp_sub)
        ut_apr[i] = cubic_spline(epoch_pmr[i], epoch_c04_sub, ut_sub)
        lod_apr[i] = cubic_spline(epoch_pmr[i], epoch_c04_sub, lod_sub)

        # In C04, ut_apr is UT1-UTC while it is UT1-TAI in .eob file,
        # so we need to calculate IAI - UTC and then convert ut_apr to UT1-UTC
        delta_tai_utc = delta_tai_utc_calc(epoch_pmr[i])
        ut_apr[i] -= delta_tai_utc

    return xp_apr, yp_apr, ut_apr, lod_apr


def interpolate_nut(epoch_nut, epoch_c04, dX_c04, dY_c04):
    """Get interpolated Nutation offset at a certain epoch.


    Parameters
    ----------
    epoch_nut : float
        epoch to be interpolated
    poch_c04 : array, float
        20-point epoch series
    dX_sub : array, float
        20-point dX series
    dY_sub : array, float
        20-point dY series

    Returns
    ----------
    dX_apr : float
        interpolated xp value
    dY_apr : float
        interpolated yp value
    """

    dX_apr = np.zeros_like(epoch_nut)
    dY_apr = np.zeros_like(epoch_nut)

    insert_ind = np.searchsorted(epoch_c04, epoch_nut)

    for i, ind in enumerate(insert_ind):
        if ind == 0 or ind >= epoch_c04.size:
            # normally it won't happen!!
            print("The epoch %f was too early or too late"
                  " for the C04 series." % epoch_nut[i])
            sys.exit()

        elif ind < 9 or epoch_c04.size - ind < 10:
            # In this case we will use less datapoints.
            pnum = min(ind, epoch_c04.size - ind)

        else:
            pnum = 10

        epoch_c04_sub = epoch_c04[ind - pnum + 1: ind + pnum + 1]

        # EOP sub-series
        dX_sub = dX_c04[ind - pnum + 1: ind + pnum + 1]
        dY_sub = dY_c04[ind - pnum + 1: ind + pnum + 1]

        # Cubic interpolation
        dX_apr[i] = cubic_spline(epoch_nut[i], epoch_c04_sub, dX_sub)
        dY_apr[i] = cubic_spline(epoch_nut[i], epoch_c04_sub, dY_sub)

    return dX_apr, dY_apr


def calc_c04_apr(t_eob, ofile=None):
    """Use Cubic Spline Interpolation to calculate the EOP.


    For the target eopch, We use the 10 successive points in front of
    and behind it in the time series (total 20 points) to do the Cubic
    Spline Interpolation.

    Parameters
    ----------
    t_eob : astropy.table object
        EOP estimates from .eob file

    Returns
    -------
    t_c04_apr : astropy.table object
        C04 a priori values for EOPs
    """

    epoch_pmr = np.array(t_eob["epoch_pmr"])
    epoch_nut = np.array(t_eob["epoch_nut"])

    # Read C04 data
    [epoch_c04, xp_c04, yp_c04, ut_c04, lod_c04, dX_c04, dY_c04] = read_c04_array()

    # Interpolation
    # For polar motion and UT1
    lod_c04 = lod_c04 * 1000  # second -> msec
    xp_apr, yp_apr, dut_apr, lod_apr = interpolate_pmr(
        epoch_pmr, epoch_c04, xp_c04, yp_c04, ut_c04, lod_c04)

    # For nutation offset
    # Convert unit from arc-sec to mas to be consistent with .eob file
    dX_c04, dY_c04 = dX_c04 * 1000, dY_c04 * 1000
    dX_apr, dY_apr = interpolate_nut(epoch_nut, epoch_c04, dX_c04, dY_c04)

    # Creat a table to store the a priori information
    t_c04_apr = Table(
        [t_eob["db_name"], t_eob["epoch_pmr"],
         xp_apr, yp_apr, dut_apr, lod_apr, dX_apr, dY_apr],
        names=["db_name", "epoch", "xp_c04_apr", "yp_c04_apr",
               "ut1_tai_c04_apr", "lod_c04_apr", "dX_c04_apr", "dY_c04_apr"])

    # Add the unit information
    # 1) polar motion (wobble) and rate
    t_c04_apr["xp_c04_apr"].unit = u.arcsec
    t_c04_apr["yp_c04_apr"].unit = u.arcsec

    # 2) UT1-TAI/UT1-UTC
    t_c04_apr["ut1_tai_c04_apr"].unit = u.second
    t_c04_apr["lod_c04_apr"].unit = u.second / 1000

    # 3) Nutation offset
    t_c04_apr["dX_c04_apr"].unit = u.mas
    t_c04_apr["dY_c04_apr"].unit = u.mas

    # Output
    if ofile is not None:
        print("# Output file: %s" % (ofile))
    else:
        ofile = "c04_apr.txt"

    # Header
    t_c04_apr.meta["comments"] = [
        " EOP and nutation series wrt. C04 series",
        " Columns  Units   Meaning",
        "    1     day     Time Tag (MJD)",
        "    3      as     X pole coordinate",
        "    4      as     Y pole coordinate",
        "    5     sec     UT1 - TAI",
        "    6     msec    LOD",
        "    7     mas     dX of Nutation offsets",
        "    8     mas     dY of Nutation offsets",
        " Created date: %s." % time.strftime("%d/%m/%Y", time.localtime())]

    t_c04_apr.write(ofile, format="ascii.fixed_width_no_header",
                    include_names=["epoch", "xp_c04_apr", "yp_c04_apr",
                                   "ut1_tai_c04_apr", "lod_c04_apr",
                                   "dX_c04_apr", "dY_c04_apr"],
                    formats={"epoch": "%13.6f",
                             "xp_c04_apr": "%+14.6f", "yp_c04_apr": "%+14.6f",
                             "ut1_tai_c04_apr": "%+14.6f", "lod_c04_apr": "%14.6f",
                             "dX_c04_apr": "%+8.3f", "dY_c04_apr": "%+8.3f"},
                    delimiter="", overwrite=True)

    return t_c04_apr


def read_c04_apr(c04_apr_file=None):
    """Read EOP from C04 series.

    Parameters
    ----------
    c04_apr_file : string
        c04 a priori file

    Returns
    ----------
    t_c04 : astropy.table object
    """

    if c04_file is None:
        c04_file = "c04_apr.txt"

    if not os.path.isfile(c04_apr_file):
        print("Couldn't find the file", c04_apr_file)
        sys.exit()

    t_c04 = Table.read(c04_apr_file, format="ascii",
                       names=["epoch", "xp", "yp", "ut1_utc", "lod", "dX", "dY"])

    # Add the unit information
    # 1) Time tag
    t_c04["epoch"].unit = cds.MJD

    # 2) polar motion (wobble) and rate
    t_c04["xp"].unit = u.arcsec
    t_c04["yp"].unit = u.arcsec

    # 3) UT1-UTC and LOD
    t_c04["ut1_utc"].unit = u.second
    t_c04["lod"].unit = u.second

    # 4) polar motion (wobble) and rate
    t_c04["dX"].unit = u.arcsec
    t_c04["dY"].unit = u.arcsec

    return t_c04


def calc_c04_offset(t_eob, aprfile=None, oftfile=None):
    """Calculate the EOP offset wrt. the C04 series.

    Parameters
    ----------
    t_eob : astropy.table object
        EOP estimates from .eob file
    aprfile : string
        a prori file of C04 series
    oftfile : string
        offset wrt. C04 series a priori

    Returns
    -------
    t_eob_oft : astropy.table object
        EOP offset wrt. the C04 series
    """

    # C04 a priori values
    t_c04_apr = calc_c04_apr(t_eob, aprfile)

    # Cross-match two tables by sessoion identifier
    t_eob_oft = join(t_eob, t_c04_apr, keys="db_name")

    dxp = t_eob_oft["xp"] - t_eob_oft["xp_c04_apr"]
    dyp = t_eob_oft["yp"] - t_eob_oft["yp_c04_apr"]
    dut = t_eob_oft["ut1_tai"] - t_eob_oft["ut1_tai_c04_apr"]
    dlod = t_eob_oft["lod"] - t_eob_oft["lod_c04_apr"]
    ddX = t_eob_oft["dX"] - t_eob_oft["dX_c04_apr"]
    ddY = t_eob_oft["dY"] - t_eob_oft["dY_c04_apr"]

    # Convert unit from arcsec/second to micro-arcsec/second
    # Polar motion
    dxp.convert_unit_to(u.uas)
    dyp.convert_unit_to(u.uas)
    t_eob_oft["xp_err"].convert_unit_to(u.uas)
    t_eob_oft["yp_err"].convert_unit_to(u.uas)

    # UT1-UTC (s -> us)
    dut.convert_unit_to(u.second / 1e6)
    t_eob_oft["ut1_tai"].convert_unit_to(u.second / 1e6)
    t_eob_oft["ut1_err"].convert_unit_to(u.second / 1e6)
    dlod.convert_unit_to(u.second / 1e6)
    t_eob_oft["lod_err"].convert_unit_to(u.second / 1e6)

    # Nutation offset
    ddX.convert_unit_to(u.uas)
    ddY.convert_unit_to(u.uas)
    t_eob_oft["dX_err"].convert_unit_to(u.uas)
    t_eob_oft["dY_err"].convert_unit_to(u.uas)

    t_eob_oft.add_columns([dxp, dyp, dut, dlod, ddX, ddY],
                          names=["dxp_c04", "dyp_c04", "dut_c04",
                                 "dlod_c04", "ddX_c04", "ddY_c04"])

    # Output
    if oftfile is not None:
        print("# Output file: %s" % (oftfile))
    else:
        oftfile = "c04_offset.txt"

    # Header
    t_eob_oft.meta["comments"] = [
        " EOP and Nutation difference wrt. C04 series",
        " Columns  Units   Meaning",
        "    1     day     Time Tag (MJD)",
        "    3     uas     offset of X pole coordinate",
        "    4     uas     offset of Y pole coordinate",
        "    5     usec    offset of UT1",
        "    6     usec    offset of LOD",
        "    6     uas     offset of dX of Nutation offsets",
        "    7     uas     offset of dY of Nutation offsets",
        " Created date: %s." % time.strftime("%d/%m/%Y", time.localtime())]

    t_eob_oft.write(oftfile, format="ascii.fixed_width_no_header",
                    include_names=["epoch_pmr", "dxp_c04", "dyp_c04",
                                   "dut_c04", "dlod_c04", "ddX_c04", "ddY_c04"],
                    formats={"epoch_pmr": "%13.6f",
                             "dxp_c04": "%+8.1f", "dyp_c04": "%+8.1f",
                             "dut_c04": "%+8.1f", "dlod_c04": "%+8.1f",
                             "ddX_c04": "%+8.1f", "ddY_c04": "%+8.1f"},
                    delimiter="", overwrite=True)

    return t_eob_oft


def c04_pm_offset_plot(t_eob_oft, fig_file="C04_pm_offset.png"):
    """Plot polar motion offset of VLBI solution wrt. C04
    """

    # Create a Time object for epochs of polar motion
    # which is convenient to convert unit from mjd to jyear
    pm_epoch = Time(t_eob_oft["epoch_pmr"], format="mjd")
    pm_epoch = pm_epoch.jyear

    # Polar motion difference
    fig, (ax0, ax1) = plt.subplots(figsize=(12, 4), sharex=True, sharey=True, nrows=2)

    # Error bar plot
    ax0.errorbar(pm_epoch, t_eob_oft["dxp_c04"]/1e3, yerr=t_eob_oft["xp_err"],
                 fmt="b.", ms=1, elinewidth=0.1, ecolor="k", errorevery=5)
    ax1.errorbar(pm_epoch, t_eob_oft["dyp_c04"]/1e3, yerr=t_eob_oft["yp_err"],
                 fmt="b.", ms=1, elinewidth=0.1, ecolor="k", errorevery=5)

    # Limits
    ax0.axis([1979, 2020, -1, 1])
    # ax1.set_ylim([-5, 5])

    # Titles and Labels
    ax0.set_title("Polar motion wrt. IERS 14 C04")
    # ax0.set_ylabel("$\Delta x_p\,(\mu as)$")
    # ax1.set_ylabel("$\Delta y_p\,(\mu as)$")
    ax0.set_ylabel("$\Delta x_p$ (mas)")
    ax1.set_ylabel("$\Delta y_p$ (mas)")

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.1)
    plt.savefig(fig_file)


def c04_ut1_offset_plot(t_eob_oft, fig_file="C04_ut1_offset.png"):
    """Plot UT1 offset of VLBI solution wrt. C04
    """

    # Create a Time object for epochs of UT1，
    # which is convenient to convert unit from mjd to jyear
    ut_epoch = Time(t_eob_oft["epoch_pmr"], format="mjd")
    ut_epoch = ut_epoch.jyear

    # UT1 difference
    fig, ax = plt.subplots(figsize=(12, 3))

    # Error bar plot
    ax.errorbar(ut_epoch, t_eob_oft["dut_c04"]/1e3, yerr=t_eob_oft["ut1_err"],
                fmt="b.", ms=1, elinewidth=0.1, ecolor="k", errorevery=5)

    # Limits
    ax.axis([1979, 2020, -0.5, 0.5])

    # Titles and Labels
    ax.set_title("UT1 wrt. IERS 14 C04")
    # ax.set_ylabel("$\Delta UT1\,(\mu s)$")
    ax.set_ylabel("$\Delta UT1$ (ms)")

    plt.tight_layout()
    plt.savefig(fig_file)


def c04_lod_offset_plot(t_eob_oft, fig_file="C04_lod_offset.png"):
    """Plot LOD offset of VLBI solution wrt. C04
    """

    # Create a Time object for epochs of UT1，
    # which is convenient to convert unit from mjd to jyear
    ld_epoch = Time(t_eob_oft["epoch_nut"], format="mjd")
    ld_epoch = ld_epoch.jyear

    # Plot
    fig, ax = plt.subplots(figsize=(12, 3))

    # Error bar plot
    ax.errorbar(ld_epoch, t_eob_oft["dlod_c04"]/1e3, yerr=t_eob_oft["lod_err"]/1e3,
                fmt="b.", ms=1, elinewidth=0.05, ecolor="k")
    # Limits
    ax.axis([1979, 2020, -8, 4])
    # ax.set_ylim([-1000, 1000])

    # Titles and Labels
    ax.set_title("Excess of the length-of-day")
    ax.set_ylabel("$\Delta LOD$ (ms)")
    ax.set_xlabel("Year")

    plt.tight_layout()
    plt.savefig(fig_file)


def c04_nut_offset_plot(t_eob_oft, fig_file="C04_nut_offset.png"):
    """Plot Nutation (CPO) offset of VLBI solution wrt. C04
    """

    # Create a Time object for epochs of UT1，
    # which is convenient to convert unit from mjd to jyear
    pn_epoch = Time(t_eob_oft["epoch_nut"], format="mjd")
    pn_epoch = pn_epoch.jyear

    # Plot
    fig, (ax0, ax1) = plt.subplots(figsize=(12, 4), sharex=True, sharey=True, nrows=2)

    # Error bar plot
    ax0.errorbar(pn_epoch, t_eob_oft["ddX_c04"]/1e3, yerr=t_eob_oft["dX_err"]/1e3,
                 fmt="b.", ms=1, elinewidth=0.05, ecolor="k")
    ax1.errorbar(pn_epoch, t_eob_oft["ddY_c04"]/1e3, yerr=t_eob_oft["dY_err"]/1e3,
                 fmt="b.", ms=1, elinewidth=0.05, ecolor="k")

    # Limits
    ax0.axis([1979, 2020, -1, 1])
    # ax1.set_ylim([-1000, 1000])

    # Titles and Labels
    ax0.set_title("Nutation offset wrt. IERS 14 C04")
    # ax0.set_ylabel("$\Delta dX\,(\mu as)$")
    # ax1.set_ylabel("$\Delta dY\,(\mu as)$")
    ax0.set_ylabel("$\Delta dX$ (mas)")
    ax1.set_ylabel("$\Delta dY$ (mas)")
    ax1.set_xlabel("Year")

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.1)
    plt.savefig(fig_file)


def c04_eob_offset_plot(t_eob_oft, tag=[""], fig_file=[""]):
    """Plot EOP offset series wrt. C04 series.
    """

    if len(tag) != len(fig_file):
        print("The length of 'tag' and 'fig_file' must be equal!")
        sys.exit()

    if "pm" in tag:
        c04_pm_offset_plot(t_eob_oft, fig_file[tag.index("pm")])
        print("Plot of polar motion offset wrt. C04:", fig_file[tag.index("pm")])

    if "ut1" in tag:
        c04_ut1_offset_plot(t_eob_oft, fig_file[tag.index("ut1")])
        print("Plot of UT1 offset wrt. C04:", fig_file[tag.index("ut1")])

    if "lod" in tag:
        c04_lod_offset_plot(t_eob_oft, fig_file[tag.index("lod")])
        print("Plot of LOD offset wrt. C04:", fig_file[tag.index("lod")])

    if "nut" in tag:
        c04_nut_offset_plot(t_eob_oft, fig_file[tag.index("nut")])
        print("Plot of Nutation offset wrt. C04:", fig_file[tag.index("nut")])


# --------------------------------- MAIN -------------------------------
if __name__ == "__main__":
    print("Nothing to do")
# --------------------------------- END --------------------------------
