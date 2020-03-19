#!/bin/bash

source ./conf.sh

python -m regista.control --item=$1 --config_path=./regista/configs/debug.yml $@
