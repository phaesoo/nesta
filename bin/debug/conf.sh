#!/bin/bash

# change current directory
MODULE_PATH=$( cd "$(dirname "$0")" ; pwd )
cd ${MODULE_PATH}
cd ..
cd ..

# export environmental variables
export NESTA_ROOT_PATH=$(pwd)
export NESTA_CONFIG_PATH=${NESTA_ROOT_PATH}/nesta/configs/debug.yml

# activate virtual environment
source .venv/bin/activate
