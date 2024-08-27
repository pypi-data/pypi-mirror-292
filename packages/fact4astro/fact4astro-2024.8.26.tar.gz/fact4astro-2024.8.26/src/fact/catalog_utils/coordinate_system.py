#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: coordinate_system.py
"""
Created on Mon Nov 16 16:43:06 2020

@author: Neo(niu.liu@nju.edu.cn)

Generate the triad vectors of the coordinate system
"""

import numpy as np


# -----------------------------  MAIN -----------------------------


def p_vector(ra, dec, unit_deg=False):
    """
    Return the unit vector in the RA direction.

    vec{p} = [-sin(ra), cos(ra), 0]^T

    Parameters
    ----------
    ra : 1-d array
        Right ascension (RA) in degrees or radians.
    dec : 1-d array
        Declination (Dec) in degrees or radians.
    unit_deg : bool, optional
        If True, the RA/Dec are given in degrees. Default is False.

    Returns
    -------
    p_vec : 2-d array of shape (N, 3)
        Unit vector in the RA direction.
    """

    if unit_deg:
        ra = np.deg2rad(ra)
        dec = np.deg2rad(dec)

    # Check if ra and dec are the same length
    if len(ra) != len(dec):
        raise ValueError(
            f"Length of ra ({len(ra)}) does not equal the length of dec ({len(dec)}).")

    N = len(ra)
    p1 = np.sin(ra)
    p2 = np.cos(ra)
    p3 = np.zeros(N)

    p_vec = np.column_stack((p1, p2, p3))

    return p_vec


def q_vector(ra, dec, unit_deg=False):
    """
    Return the unit vector in the Declination direction.

    vec{q} = [-sin(dec)*cos(ra), -sin(dec)*sin(ra), cos(dec)]^T

    Parameters
    ----------
    ra : 1-d array
        Right ascension (RA) in degrees or radians.
    dec : 1-d array
        Declination (Dec) in degrees or radians.
    unit_deg : bool, optional
        If True, the RA/Dec are given in degrees. Default is False.

    Returns
    -------
    q_vec : 2-d array of shape (N, 3)
        Unit vector in the Declination direction.
    """

    if unit_deg:
        ra = np.deg2rad(ra)
        dec = np.deg2rad(dec)

    # Check if ra and dec are the same length
    if len(ra) != len(dec):
        raise ValueError(
            f"Length of ra ({len(ra)}) does not equal the length of dec ({len(dec)}).")

    N = len(ra)
    q1 = -np.sin(dec) * np.cos(ra)
    q2 = -np.sin(dec) * np.sin(ra)
    q3 = np.cos(dec)

    q_vec = np.column_stack((q1, q2, q3))

    return q_vec


def r_vector(ra, dec, unit_deg=False):
    """
    Return the unit vector in the radial direction.

    vec{r} = [cos(dec)*cos(ra), cos(dec)*sin(ra), sin(dec)]^T

    Parameters
    ----------
    ra : 1-d array
        Right ascension (RA) in degrees or radians.
    dec : 1-d array
        Declination (Dec) in degrees or radians.
    unit_deg : bool, optional
        If True, the RA/Dec are given in degrees. Default is False.

    Returns
    -------
    r_vec : 2-d array of shape (N, 3)
        Unit vector in the radial direction.
    """

    if unit_deg:
        ra = np.deg2rad(ra)
        dec = np.deg2rad(dec)

    # Check if ra and dec are the same length
    if len(ra) != len(dec):
        raise ValueError(
            f"Length of ra ({len(ra)}) does not equal the length of dec ({len(dec)}).")

    N = len(ra)
    r1 = np.cos(dec) * np.cos(ra)
    r2 = np.cos(dec) * np.sin(ra)
    r3 = np.sin(dec)

    r_vec = np.column_stack((r1, r2, r3))

    return r_vec

# --------------------------------- END --------------------------------
