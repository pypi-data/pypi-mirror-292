#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: cat_vars.py
"""
Created on Thu Jul  7 22:49:14 2022

@author: Neo(niu.liu@nju.edu.cn)

Load configuration of environmental variables

History
"""

import sys
from sys import platform as _platform
import yaml


__all__ = ["load_cfg", "get_data_dir"]


# --------------------------------- MAIN -------------------------------
def environmental_variables():
    """Return configuration of environmental variables
    """

    yml_content = """
# Default path to various directories 
dir_path:
  # Directory containing catalog files 
  data_dir:
  # Only work for me
  data_dir_linux: /data/catalogs
  dara_dir_macos: /Users/Neo/Astronomy/data/catalogs

# Default path to various catalog data files 
file_path:
  icrf1:
  icrf2:
  icrf3sx:
  icrf3k:
  icrf3xka:

# Link to online materials
online_url:
  icrf1_all: https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf1-all.txt 
  icrf1_ext1: https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf1ext1-all.txt
  icrf1_ext2: https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf1ext2-all.txt
  icrf2: https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf2-all.txt
  icrf3sx: https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf3sx.txt
  icrf3k: https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf3k.txt
  icrf3xka: https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf3xka.txt
  rfc: http://astrogeo.org/sol/rfc/
  ocars_main: http://www.gaoran.ru/english/as/ac_vlbi/ocars.txt
  ocars_main_csv: http://www.gaoran.ru/english/as/ac_vlbi/ocars.csv
  ivs_sou_name_table_nasa: https://cddis.nasa.gov/archive/vlbi/gsfc/ancillary/solve_apriori/IVS_SrcNamesTable.txt 
  ivs_sou_name_table: https://liuniu.fun/data/IVS_SrcNamesTable.txt 
    """

    return yml_content


def load_cfg():
    """Load local configurations
    """

    # with open("~/Git/fact/src/fact/cat_parser/cat_vars.yml", "r") as ymlfile:
    cfg = yaml.load(environmental_variables(), Loader=yaml.FullLoader)

    return cfg


def get_data_dir():

    cfg = load_cfg()

    if cfg["dir_path"]["data_dir"]:
        # If this variable is set
        data_dir = cfg["dir_path"]["data_dir"]
    else:
        # Check the type of OS
        if _platform in ["linux", "linux2"]:
            # linux
            data_dir = cfg["dir_path"]["data_dir_linux"]
        elif _platform in ["darwin"]:
            # MAC OS X
            data_dir = cfg["dir_path"]["data_dir_macos"]
        elif _platform in ["win32", "win64"]:
            # Windows
            print("Not implemented yet")
            sys.exit()

    return data_dir


if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
