#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: ivs_sou_name.py
"""
Created on Tue 26 Dec 2023 03:35:30 PM CST

@author: Neo(niu.liu@nju.edu.cn)

This script is used to download the official IVS source name and translation 
table (cross reference table of source names under multiple conventions 
(e.g., IVS and IERS B1950)) available at 
https://cddis.nasa.gov/archive/vlbi/gsfc/ancillary/solve_apriori/IVS_SrcNamesTable.txt

Since this file is hard to be accessed directly, I put it on my personal website.

"""


import numpy as np
from astropy.table import Table

# My modules
from .download_online_content import download_online_data
from .cat_vars import load_cfg


__all__ = ["read_ivs_sou_name_table"]


# --------------------------------- MAIN -------------------------------
def read_ivs_sou_name_table(sou_name_file=None):
    """
    """

    if sou_name_table is None:
        cfg = load_cfg()
        sou_name_url = cfg["online_url"]["ivs_sou_name_table"]
        sou_name_file = download_online_data(sou_name_url)

    sou_name_table = Table.read(sou_name_file, format="ascii.fixed_width_no_header",
                                names=["ivs_name", "iau_name",
                                       "iau_name_short", "iers_name", "jpl_name"],
                                col_starts=[0, 10, 28, 40, 50],
                                col_ends=[7, 25, 37, 47, 61])

    for i in range(len(sou_name_table)):
        if sou_name_table["iers_name"][i] == "-":
            sou_name_table["iers_name"][i] = sou_name_table["ivs_name"][i]

    return sou_name_table


if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
