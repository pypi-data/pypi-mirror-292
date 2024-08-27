#!/usr/bin/bash
#########################################################################
# File Name: install_local.sh
# Author: Neo
# Mail: niu.liu@nju.edu.cn
# Created Time: Wed Feb 16 16:10:20 2022
#########################################################################

python -m build
pip install --editable .
