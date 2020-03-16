#!/bin/bash

# change current directory
MODULE_PATH=$( cd "$(dirname "$0")" ; pwd )
cd ${MODULE_PATH}
cd ..

source .venv/bin/activate


echo $@

python -m regista.control --item=$1 --config_path=./regista/configs/debug.yml $@
