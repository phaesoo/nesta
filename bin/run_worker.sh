#!/bin/bash

source ./conf.sh

python -m regista.worker --config_path=./regista/configs/debug.yml
