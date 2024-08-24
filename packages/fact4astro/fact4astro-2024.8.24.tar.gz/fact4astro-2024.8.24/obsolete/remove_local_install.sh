#!/usr/bin/bash
#########################################################################
# File Name: remove_local_install.sh
# Author: Neo
# mail: niu.liu@nju.edu.cn
# Created Time: Tue Mar 15 17:43:52 2022
#########################################################################

# if [ "$(uname)" == "Darwin" ];
# then
#     rm -r /Users/Neo/Scisoft/miniconda3/lib/python3.*/site-packages/fact4astro-*
# elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ];
# then
#     rm -r /data/softwares/miniconda3/lib/python3.*/site-packages/fact4astro-*
#     rm /home/niu/miniconda3/lib/python3.*/site-packages/fact4astro-*
# fi

# rm -r ${CONDA_PREFIX}/lib/python3.*/site-packages/fact-*
pip uninstall fact
