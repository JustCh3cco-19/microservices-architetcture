#!/bin/bash

# Make sure that we are in the right directory
if [ ! -f Dockerfile ] || [ ! -f ../dummy_dvde_api.py ]; then
    echo "Error: Either Dockerfile is missing in the current directory or dummy_dvde_api.py is missing in the parent directory."
    exit 1
fi

mkdir -p build_temp
cp ../dummy_dvde_api.py build_temp

# Sudo is typically not required on Mac OS
if [[ $(uname) == "Darwin" ]]; then
    docker build . -t as-slam
else
    sudo docker build . -t as-slam
fi