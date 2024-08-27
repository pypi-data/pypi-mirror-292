#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: cat_vars.py
"""
Created on Thu Jul  7 22:49:14 2022

@author: Neo(niu.liu@nju.edu.cn)

Load configuration of environmental variables

"""

import os
from sys import platform as _platform
import yaml


__all__ = ["load_cfg", "get_cat_dir"]

# Constants for platform detection
LINUX = "linux"
MACOS = "darwin"
WINDOWS = "win32"

# --------------------------------- MAIN --------------------------------


def load_default_cfg():
    """
    Return a dictionary containing default configuration of environmental variables.

    Returns:
        dict: A dictionary containing default directory paths, catalog file paths, and online URLs.
    """
    return {
        "dir_path": {
            "cat_dir": "",
            "cat_dir_linux": "/data/catalogs",
            "cat_dir_macos": "/Users/Neo/Astronomy/data/catalogs",
        },
        "cat_file_path": {
            "icrf1": "",
            "icrf2": "",
            "icrf3sx": "",
            "icrf3k": "",
            "icrf3xka": "",
            "gdr3_icrf": "",
            "gdr3_crf": "",
        },
        "online_url": {
            "icrf1_all": "https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf1-all.txt",
            "icrf1_ext1": "https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf1ext1-all.txt",
            "icrf1_ext2": "https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf1ext2-all.txt",
            "icrf2": "https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf2-all.txt",
            "icrf3sx": "https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf3sx.txt",
            "icrf3k": "https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf3k.txt",
            "icrf3xka": "https://hpiers.obspm.fr/icrs-pc/newwww/icrf/icrf3xka.txt",
            "rfc": "http://astrogeo.org/sol/rfc/",
            "ocars_main": "http://www.gaoran.ru/english/as/ac_vlbi/ocars.txt",
            "ocars_main_csv": "http://www.gaoran.ru/english/as/ac_vlbi/ocars.csv",
            "ivs_sou_name_table_nasa": "https://cddis.nasa.gov/archive/vlbi/gsfc/ancillary/solve_apriori/IVS_SrcNamesTable.txt",
            "ivs_sou_name_table": "https://liuniu.fun/data/IVS_SrcNamesTable.txt",
            "ivs_sou_name_table_astrogeo": "",
        },
    }


def load_cfg():
    """
    Load local configurations from an environment-specified YAML file or return default configurations.

    Returns:
        dict: The configuration dictionary.
    """
    yml_file_path = os.getenv("FACT_CAT_YAML")

    if yml_file_path is None:
        return load_default_cfg()

    try:
        with open(yml_file_path, "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print(
            f"YAML configuration file not found at {yml_file_path}. Loading default configuration.")
        cfg = load_default_cfg()
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}. Loading default configuration.")
        cfg = load_default_cfg()

    return cfg


def get_cat_dir():
    """
    Determine the catalog directory based on the platform and configuration settings.

    Returns:
        str: The path to the catalog directory.
    """
    cfg = load_cfg()

    cat_dir = cfg["dir_path"]["cat_dir"]

    if cat_dir:
        return cat_dir

    # Determine directory based on the operating system
    platform_dirs = {
        LINUX: cfg["dir_path"]["cat_dir_linux"],
        MACOS: cfg["dir_path"]["cat_dir_macos"]
    }

    if _platform in platform_dirs:
        return platform_dirs[_platform]
    elif _platform in [WINDOWS]:
        raise NotImplementedError("Windows platform is not supported yet.")
    else:
        raise ValueError("Unsupported platform.")

# --------------------------------- END --------------------------------


if __name__ == "__main__":
    pass
