#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: download_online_content.py
"""
Created on Thu 28 Dec 2023 02:54:39 PM CST

@author: Neo(niu.liu@nju.edu.cn)

History
2023-12-28:
    - Add a function to download online content

"""

import urllib3

__all__ = ["download_online_data"]


def download_online_data(data_url):
    """Download online data and convert into strings

    Parameter
    ---------
    data_url : str
        url link

    Return
    ------
    data_content : str
        plain text that can be parsed by other functions such as astropy.table.Table
    """

    http = urllib3.PoolManager()
    resp = http.request("GET", data_url)
    data_content = resp.data.decode("utf-8")

    return data_content


# -------------------------------- MAIN --------------------------------
if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
