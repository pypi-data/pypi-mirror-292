#!/usr/bin/bash
#########################################################################
# File Name: build_code.sh
# Author: Neo
# Mail: niu.liu@nju.edu.cn
# Created Time: Sat 24 Aug 2024 02:31:11 PM CST
#########################################################################

# Install the package on the local machine for testing
local_install() {
    python -m build
    pip install --editable .
}

# Remove the package on the local machine 
local_remove() {
    pip uninstall -y fact
}

# Publish package on PyPI
publish_pypi() {
    rm -rf dist/*
    python3 -m build

    twine check dist/*
    twine upload --repository pypi dist/* --verbose
}

# Publish package on TestPyPI
publish_testpypi() {
    rm -rf dist/*
    python3 -m build

    twine check dist/*
    twine upload --repository testpypi dist/*
}

# Display help information
print_help() {
    echo "Usage: $0 {local_install|local_remove|publish|publish_test}"
    echo "Commands:"
    echo "  local_install   Install the package on the local machine for testing."
    echo "  local_remove    Remove the local installation of the package."
    echo "  publish         Publish the package on PyPI."
    echo "  publish_test    Publish the package on TestPyPI."
}

# Main 
if [ "$#" -eq 0 ]; then
    echo "No arguments provided."
    print_help
elif [ "$1" == "local_install" ]; then
    echo "Installing the package on the local machine."
    local_install
elif [ "$1" == "local_remove" ]; then
    echo "Removing the local installation."
    local_remove
elif [ "$1" == "publish" ]; then
    echo "Publishing the package on PyPI."
    publish_pypi
elif [ "$1" == "publish_test" ]; then
    echo "Publishing the package on TestPyPI."
    publish_testpypi
else
    echo "Invalid argument: $1"
    print_help
fi
