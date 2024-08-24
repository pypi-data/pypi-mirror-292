#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: __init__.py
"""
Created on Thu Jul  7 22:49:14 2022

@author: Neo(niu.liu@nju.edu.cn)
"""

# Functions commonly used and contained within this module
from .download_online_content import download_online_data
from .cat_vars import load_cfg

# from .read_icrf import *
# from .read_gaia import *
# from .read_hip import *
# from .read_ocars import *
# from .read_rfc import *

# Load default settings
cfg = load_cfg()
