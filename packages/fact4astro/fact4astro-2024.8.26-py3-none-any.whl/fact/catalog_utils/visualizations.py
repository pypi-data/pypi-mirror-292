#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: visualizations.py
"""
Created on Mon 26 Aug 2024 10:55:27 AM CST

@author: Neo(niu.liu@nju.edu.cn)
"""


from scipy import stats
from matplotlib.ticker import NullFormatter
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
from matplotlib.ticker import MultipleLocator, NullFormatter

import astropy.units as u
from astropy.coordinates import SkyCoord

from .galactic_aberration import generate_glide_field


__all__ = ["plot_positional_offset_with_histograms",
           "plot_positional_offset",
           "plot_normalized_offsets",
           "plot_angular_separation_distribution",
           "plot_normalized_separation_distribution",
           "plot_angular_vs_normalized_separation"]


def plot_confidence_ellipse(x, y, ax, pearson=None, n_std=1.0, facecolor="none", **kwargs):
    """
    Create a plot of the covariance confidence ellipse of `x` and `y`.

    Parameters
    ----------
    x, y : array_like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float, optional
        The number of standard deviations to determine the ellipse's radiuses.
        Default is 1.0.

    Returns
    -------
    matplotlib.patches.Ellipse

    Other parameters
    ----------------
    kwargs : `~matplotlib.patches.Patch` properties
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    if pearson is None:
        cov = np.cov(x, y)
        pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])

    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0),
                      width=ell_radius_x * 2,
                      height=ell_radius_y * 2,
                      facecolor=facecolor,
                      **kwargs)

    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


def plot_glide_field(gv, output=None, fig_title=None):
    """
    Plot the glide field using a quiver plot in an Aitoff projection.

    Parameters
    ----------
    gv : array of float
        Glide vector components [g1, g2, g3] in microarcseconds.
    output : string, optional
        Full path to the output file where the plot will be saved. If None, the plot will be displayed.
    fig_title : string, optional
        Title of the figure.

    Returns
    -------
    None
    """

    # Generate a grid of RA and Dec values
    ra = np.linspace(0, 360, 20) * u.deg
    dec = np.linspace(-90, 90, 20) * u.deg
    c = SkyCoord(ra=ra, dec=dec, frame="icrs")

    ra_rad = c.ra.wrap_at(180 * u.deg).radian
    dec_rad = c.dec.radian

    # Generate the glide field
    X, Y = np.meshgrid(ra_rad, dec_rad)
    U, V = generate_glide_field(gv, X, Y)

    # Galactic Center (GC) position
    c1_gal = SkyCoord(l=0 * u.deg, b=0 * u.deg, frame="galactic")
    c1_icrs = c1_gal.icrs
    ra_gc_rad = c1_icrs.ra.wrap_at(180 * u.deg).radian
    dec_gc_rad = c1_icrs.dec.radian

    # Anti-Galactic Center (anti-GC) position
    c2_gal = SkyCoord(l=180 * u.deg, b=0 * u.deg, frame="galactic")
    c2_icrs = c2_gal.icrs
    ra_agc_rad = c2_icrs.ra.wrap_at(180 * u.deg).radian
    dec_agc_rad = c2_icrs.dec.radian

    # Create the plot
    plt.figure(figsize=(8, 4.2))
    plt.subplot(111, projection="aitoff")

    # Plot the glide field
    quiver = plt.quiver(X, Y, U, V, units="xy", scale=100.0)
    plt.quiverkey(quiver, 0.90, 0.90, 50, r"$50 \mu as$", labelpos="E",
                  coordinates="figure")

    # Mark the positions of the GC and anti-GC
    plt.plot(ra_gc_rad, dec_gc_rad, "r+", label="GC")
    plt.plot(ra_agc_rad, dec_agc_rad, "r+", label="Anti-GC")
    plt.text(ra_gc_rad, dec_gc_rad, "GC", color="r", fontsize=12)

    # Add title if provided
    if fig_title is not None:
        plt.title(fig_title, y=1.08)

    # Add grid and adjust layout
    plt.grid(True)
    plt.subplots_adjust(top=0.95, bottom=0.05)

    # Save or show the plot
    if output is None:
        plt.show()
    else:
        plt.savefig(output)


def plot_positional_offset_with_histograms(x, y, xymax=5, label="", unit_str="mas", save_fig=False, save_fig_name=None):
    """
    Create a scatter plot with histograms for positional offsets in right ascension and declination.

    Parameters
    ----------
    x : array-like
        Positional offsets in right ascension.
    y : array-like
        Positional offsets in declination.
    xymax : float, optional
        Maximum limit for both axes (default is 5).
    label : str, optional
        Label for axis titles (default is an empty string).
    unit_str : str, optional
        Unit string for the axis labels (default is "mas").
    save_fig : bool, optional
        Whether to save the figure (default is False).
    save_fig_name : str, optional
        Custom file name for saving the figure (default is None).

    Returns
    -------
    None
    """
    if len(x) != len(y):
        raise ValueError("The lengths of x and y must be the same.")

    # Define the layout of the plot
    left, width = 0.12, 0.65
    bottom, height = 0.12, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    # Create figure and axes
    fig = plt.figure(figsize=(6., 6.))
    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    # Hide the labels on the histograms
    nullfmt = NullFormatter()
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    # Scatter plot
    axScatter.scatter(x, y, s=2, lw=0.5, facecolors="None", edgecolors="b")

    # Axis labels
    if label and unit_str:
        axis_label = f"{label}, {unit_str}"
    elif label:
        axis_label = label
    else:
        axis_label = unit_str

    xaxis_label = f"$\\Delta\\,\\alpha\\,\\cos\\delta$ ({axis_label})"
    yaxis_label = f"$\\Delta\\,\\delta$ ({axis_label})"

    axScatter.set_xlabel(xaxis_label, fontsize=12)
    axScatter.set_ylabel(yaxis_label, fontsize=12)

    # Set limits and bin size
    binwidth = 0.1
    lim = (int(xymax / binwidth) + 1) * binwidth

    axScatter.set_xlim((-lim, lim))
    axScatter.set_ylim((-lim, lim))

    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHistx.hist(x, bins=bins, fill=False, edgecolor='b')
    axHisty.hist(y, bins=bins, orientation="horizontal",
                 fill=False, edgecolor='b')

    axHistx.set_xlim(axScatter.get_xlim())
    axHisty.set_ylim(axScatter.get_ylim())

    axScatter.grid(lw=0.1)
    axHistx.grid(lw=0.1)
    axHisty.grid(lw=0.1)

    if save_fig:
        if save_fig_name is None:
            from time import gmtime, strftime
            time_tag = strftime("%Y-%m-%d", gmtime())
            save_fig_name = f"positional_offset_{time_tag}.png"
            print(f"[msg] Output file: {save_fig_name}")
        plt.savefig(save_fig_name, bbox_inches="tight")
    else:
        plt.show()


def plot_positional_offset(data, plot_type="ra", title_name="", unit_str="mas", y_lim=[-5, 5], save_fig=False, save_fig_name=None):
    """
    Create a plot of positional offsets in either RA or Dec with error bars.

    Parameters
    ----------
    data : pandas.DataFrame or astropy.table.Table
        Table containing columns 'ra', 'dec', 'dra', 'dra_err', 'ddec', and 'ddec_err'.
    plot_type : str, optional
        The type of plot to create. Options are 'ra' (default) to plot against right ascension
        or 'dec' to plot against declination.
    title_name : str, optional
        Title of the plot (default is an empty string).
    unit_str : str, optional
        Unit string for the y-axis labels (default is "mas").
    y_lim : list of float, optional
        Limits for the y-axis (default is [-5, 5]).
    save_fig : bool, optional
        Whether to save the figure (default is False).
    save_fig_name : str, optional
        Custom file name for saving the figure (default is None).

    Returns
    -------
    None
    """
    fig, (ax0, ax1) = plt.subplots(
        figsize=(8, 6), nrows=2, sharex=True, sharey=True)

    if plot_type == "ra":
        x_data = data["ra"]
        x_label = "RA ($^\\circ$)"
        x_ticks = np.arange(0, 361, 60)
        x_lim = [0, 360]
    elif plot_type == "dec":
        x_data = data["dec"]
        x_label = "Declination ($^\\circ$)"
        x_ticks = np.arange(-90, 91, 30)
        x_lim = [-90, 90]
    else:
        raise ValueError("Invalid plot_type. Choose 'ra' or 'dec'.")

    ax0.errorbar(x_data, data["dra"], yerr=data["dra_err"],
                 fmt=".", color="b", elinewidth=0.2, ms=2)
    ax1.errorbar(x_data, data["ddec"], yerr=data["ddec_err"],
                 fmt=".", color="b", elinewidth=0.2, ms=2)

    ax0.set_xticks(x_ticks)
    if x_lim:
        ax0.set_xlim(x_lim)
    ax0.set_ylim(y_lim)

    ax1.set_xlabel(x_label, fontsize=15)
    ax0.set_ylabel(f"$\\Delta \\alpha*$ ({unit_str})", fontsize=15)
    ax1.set_ylabel(f"$\\Delta \\delta$ ({unit_str})", fontsize=15)

    if len(title_name):
        ax0.set_title(title_name, fontsize=15)
    fig.tight_layout()

    if save_fig:
        if save_fig_name is None:
            import time
            t = time.gmtime()
            time_tag = time.strftime("%Y-%m-%d", t)
            save_fig_name = f"/tmp/positional_offset_{time_tag}.png"
            print(f"[msg] Output file: {save_fig_name}")
        plt.savefig(save_fig_name, bbox_inches="tight")
    else:
        plt.show()


def plot_normalized_offsets(data, add_gaussian_dist=True, bin_range=(-10, 10), bin_count=50, y_lim=[0, 16], label=""):
    """
    Plot histograms for normalized RA and Dec with optional Gaussian distribution overlay.

    Parameters
    ----------
    data : pandas.DataFrame or astropy.table.Table
        Table containing columns 'nor_ra' and 'nor_dec'.
    add_gaussian_dist : bool, optional
        If True, adds a standard Gaussian distribution overlay (default is True).
    bin_range : tuple of float, optional
        Range for the histogram bins (default is (-10, 10)).
    bin_count : int, optional
        Number of bins in the histogram (default is 50).
    y_lim : list of float, optional
        Limits for the y-axis (default is [0, 16]).

    Returns
    -------
    None
    """
    num_sou = len(data)
    bins_array = np.linspace(bin_range[0], bin_range[1], bin_count)
    bin_size = (bin_range[1] - bin_range[0]) / bin_count
    weights = np.ones(num_sou) * 100. / num_sou

    fig, (ax0, ax1) = plt.subplots(figsize=(8, 4), ncols=2, sharey=True)
    ax0.hist(data["nor_ra"], bins_array, weights=weights,
             facecolor='w', alpha=0.75, edgecolor="b")
    ax1.hist(data["nor_dec"], bins_array, weights=weights,
             facecolor="w", edgecolor="b", alpha=0.75)

    if len(label):
        fig.suptitle(label, fontsize=15)

    # add a '(standard) Gaussian distribution' line
    if add_gaussian_dist:
        gaussian_dist = stats.norm.pdf(bins_array, 0, 1) * bin_size
        ax0.plot(bins_array, gaussian_dist * 100, "r--", linewidth=1)
        ax1.plot(bins_array, gaussian_dist * 100, "r--", linewidth=1)

    ax0.set_yticks(np.arange(0, y_lim[1] + 2, 2))
    ax1.set_yticks(np.arange(0, y_lim[1] + 2, 2))

    ax0.set_ylim(y_lim)
    ax1.set_ylim(y_lim)

    ax0.set_xlabel("$X_\\alpha*$", fontsize=12)
    ax1.set_xlabel("$X_\\delta$", fontsize=12)

    ax0.set_ylabel("% in bin", fontsize=12)

    fig.tight_layout()
    plt.show()


def plot_angular_separation_distribution(data, column_name="ang_sep", label="",
                                         xlabel="Angular separation $\\rho$ (mas)",
                                         ylabel="% in bin", bins=50, max_value=5,
                                         save_fig=False, save_fig_name=None):
    """
    Plot the distribution of angular separation with an optional label.

    Parameters
    ----------
    data : pandas.DataFrame or astropy.table.Table
        Table containing the angular separation data.
    column_name : str, optional
        Name of the column containing the angular separation data (default is "ang_sep").
    label : str, optional
        Label for the plot (default is "ICRF3 S/X").
    xlabel : str, optional
        Label for the x-axis (default is "Angular separation $\\rho$ (mas)").
    ylabel : str, optional
        Label for the y-axis (default is "% in bin").
    bins : int, optional
        Number of bins for the histogram (default is 50).
    max_value : float, optional
        Maximum value for the x-axis (default is 5).
    save_fig : bool, optional
        Whether to save the figure (default is False).
    save_fig_name : str, optional
        Custom file name for saving the figure (default is None).

    Returns
    -------
    None
    """

    num_sou = len(data)
    bins_array = np.linspace(0, max_value, bins)
    weights = np.ones(num_sou) * 100.0 / num_sou

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(data[column_name], bins_array, weights=weights,
            facecolor="w", edgecolor="b")

    if len(label):
        ax.set_title(label, fontsize=15)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    fig.tight_layout()

    if save_fig:
        if save_fig_name is None:
            import time
            t = time.gmtime()
            time_tag = time.strftime("%Y-%m-%d", t)
            save_fig_name = f"/tmp/angular_separation_distribution_{time_tag}.png"
            print(f"[msg] Output file: {save_fig_name}")
        plt.savefig(save_fig_name, bbox="tight")
    else:
        plt.show()


def plot_normalized_separation_distribution(data, column_name="nor_sep", label="",
                                            xlabel="Normalized separation $X$", ylabel="% in bin",
                                            bins=50, max_value=10, add_rayleigh_dist=True,
                                            save_fig=False, save_fig_name=None):
    """
    Plot the distribution of normalized separation with an optional Rayleigh distribution curve.

    Parameters
    ----------
    data : pandas.DataFrame or astropy.table.Table
        Table containing the normalized separation data.
    column_name : str, optional
        Name of the column containing the normalized separation data (default is "nor_sep").
    label : str, optional
        Label for the plot (default is "ICRF3 S/X").
    xlabel : str, optional
        Label for the x-axis (default is "Normalized separation $X$").
    ylabel : str, optional
        Label for the y-axis (default is "% in bin").
    bins : int, optional
        Number of bins for the histogram (default is 50).
    max_value : float, optional
        Maximum value for the x-axis (default is 10).
    add_rayleigh_dist : bool, optional
        Whether to overlay a Rayleigh distribution curve (default is True).
    save_fig : bool, optional
        Whether to save the figure (default is False).
    save_fig_name : str, optional
        Custom file name for saving the figure (default is None).

    Returns
    -------
    None
    """

    num_sou = len(data)
    bins_array = np.linspace(0, max_value, bins)
    weights = np.ones(num_sou) * 100.0 / num_sou

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(data[column_name], bins_array, weights=weights,
            facecolor="w", edgecolor="b")

    if add_rayleigh_dist:
        rayleigh_dist = stats.rayleigh.pdf(
            bins_array) * (max_value / bins) * 100
        ax.plot(bins_array, rayleigh_dist, "r--", linewidth=1)

    if len(label):
        ax.set_title(label, fontsize=15)

    ax.set_xlim([0, max_value])
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    fig.tight_layout()

    if save_fig:
        if save_fig_name is None:
            import time
            t = time.gmtime()
            time_tag = time.strftime("%Y-%m-%d", t)
            save_fig_name = f"/tmp/normalized_separation_distribution_{time_tag}.png"
            print(f"[msg] Output file: {save_fig_name}")
        plt.savefig(save_fig_name, bbox="tight")
    else:
        plt.show()


def plot_angular_vs_normalized_separation(data, norm_sep_col="nor_sep", ang_sep_col="ang_sep", label="",
                                          xlabel="Angular separation $\\rho$ (mas)", ylabel="Normalized separation $X$",
                                          xlim=[0.02, 600], ylim=[0.01, 600], save_fig=False, save_fig_name=None):
    """
    Plot the relationship between angular separation and normalized separation on a logarithmic scale.

    Parameters
    ----------
    data : pandas.DataFrame or astropy.table.Table
        Table containing the angular and normalized separation data.
    norm_sep_col : str, optional
        Name of the column containing the normalized separation data (default is "nor_sep").
    ang_sep_col : str, optional
        Name of the column containing the angular separation data (default is "ang_sep").
    xlabel : str, optional
        Label for the x-axis (default is "Angular separation $\\rho$ (mas)").
    ylabel : str, optional
        Label for the y-axis (default is "Normalized separation $X$").
    xlim : list of float, optional
        Limits for the x-axis (default is [0.02, 600]).
    ylim : list of float, optional
        Limits for the y-axis (default is [0.01, 600]).
    save_fig : bool, optional
        Whether to save the figure (default is False).
    save_fig_name : str, optional
        Custom file name for saving the figure (default is None).

    Returns
    -------
    None
    """

    fig, ax = plt.subplots()

    ax.plot(data[norm_sep_col], data[ang_sep_col], "b*", ms=1.5)

    if len(label):
        ax.set_title(label, fontsize=15)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    fig.tight_layout()

    if save_fig:
        if save_fig_name is None:
            import time
            t = time.gmtime()
            time_tag = time.strftime("%Y-%m-%d", t)
            save_fig_name = f"/tmp/angular_vs_normalized_separation_{time_tag}.png"
            print(f"[msg] Output file: {save_fig_name}")
        plt.savefig(save_fig_name, bbox_inches="tight")
    else:
        plt.show()
