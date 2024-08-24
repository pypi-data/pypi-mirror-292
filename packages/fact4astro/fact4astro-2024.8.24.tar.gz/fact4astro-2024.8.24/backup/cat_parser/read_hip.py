#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: read_hip.py
"""
Created on Wed Nov  3 09:35:24 2021

@author: Neo(niu.liu@nju.edu.cn)

This code is used to load the Hipparcos catalog (ESA 1997) and extract data 
for some specific sources
"""

import numpy as np

from astropy.table import Table, Column
from astropy import units as u

# My modules
from .cat_vars import get_data_dir


__all__ = ["read_hip_main", "read_tyc_main", "read_hip_dmo"]


# -----------------------------  FUNCTIONS -----------------------------
def get_hip_dir():
    """Return the directory where the Hipparcos data are stored.

    """

    cat_dir = get_data_dir()
    hip_dir = "{:s}/hipparcos".format(cat_dir)

    return hip_dir


def read_hip_main():
    """Load the Hipparcos main catalog
    """

    hip_dir = get_hip_dir()
    hip_main_file = "{:s}/I_239_hip_main.dat.fits".format(hip_dir)
    hip_main_table = Table.read(hip_main_file)

    return hip_main_table


def read_tyc_main():
    """Load the Tycho main catalog
    """

    hip_dir = get_hip_dir()
    tyc_main_file = "{:s}/I_239_tyc_main.dat.fits".format(hip_dir)
    tyc_main_table = Table.read(tyc_main_file)

    return tyc_main_table


def read_hip_dmo():
    """Load the Hipparcos orbital solution

    """

    hip_dir = get_hip_dir()
    hip_dmo_file = "{:s}/I_239_hip_dm_o.dat.gz.fits".format(hip_dir)
    hip_dmo_table = Table.read(hip_dmo_file)

    return hip_main_table


# -------------------------------- MAIN --------------------------------
if __name__ == "__main__":
    read_hip_dmo()
# --------------------------------- END --------------------------------
