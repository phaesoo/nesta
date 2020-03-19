#!/bin/bash

# change current directory
MODULE_PATH=$( cd "$(dirname "$0")" ; pwd )
cd ${MODULE_PATH}
cd ..

# export project root dir
export ROOT_DIR=$(pwd)

# activate virtual environment
source .venv/bin/activate
