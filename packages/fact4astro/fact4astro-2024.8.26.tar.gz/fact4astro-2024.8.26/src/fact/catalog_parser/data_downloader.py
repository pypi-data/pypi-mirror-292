#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: download_online_content.py
"""
Module to download and retrieve online content as plain text.

Created on Thu 28 Dec 2023 02:54:39 PM CST

Author: Neo (niu.liu@nju.edu.cn)

This module contains a function to download data from a specified URL and convert it
into a plain text string that can be parsed by other functions or libraries.
"""

import urllib3

__all__ = ["download_online_data"]

# -----------------------------  FUNCTIONS -----------------------------


def download_online_data(data_url):
    """
    Download online data from a specified URL and convert it to a string.

    Parameters
    ----------
    data_url : str
        The URL from which to download the data.

    Returns
    -------
    data_content : str
        The downloaded content as a plain text string, suitable for parsing by
        other functions or libraries such as astropy.table.Table.

    Raises
    ------
    urllib3.exceptions.HTTPError
        If there is an issue with the HTTP request.
    """
    http = urllib3.PoolManager()

    try:
        resp = http.request("GET", data_url)
        if resp.status != 200:
            raise urllib3.exceptions.HTTPError(
                f"Failed to download data: HTTP {resp.status}")

        data_content = resp.data.decode("utf-8")
    except urllib3.exceptions.HTTPError as e:
        print(f"Error: {e}")
        data_content = ""

    return data_content

# -------------------------------- MAIN --------------------------------


if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
