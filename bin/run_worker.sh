#!/bin/bash

# change current directory
MODULE_PATH=$( cd "$(dirname "$0")" ; pwd )
cd ${MODULE_PATH}
cd ..

source .venv/bin/activate

python -m regista.worker --config_path=./regista/configs/debug.yml
