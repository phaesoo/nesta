#!/bin/bash

# change current directory
MODULE_PATH=$( cd "$(dirname "$0")" ; pwd )
cd ${MODULE_PATH}
cd ..

# export environmental variables
export ABSINTHE_ROOT_PATH=$(pwd)
export ABSINTHE_CONFIG_PATH=${ABSINTHE_ROOT_PATH}/absinthe/configs/debug.yml

# activate virtual environment
source .venv/bin/activate
