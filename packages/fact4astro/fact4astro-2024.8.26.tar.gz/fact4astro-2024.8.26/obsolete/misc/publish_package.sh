#!/usr/local/bin/bash
#########################################################################
# File Name: publish_package.sh
# Author: Neo
# Mail: niu.liu@nju.edu.cn
# Created Time: Tue Feb  8 12:42:34 2022
#########################################################################

rm dist/*
python3 -m build

twine check dist/*
# twine upload dist/*
# twine upload --repository testpypi dist/*
twine upload --repository pypi dist/*  --verbose
