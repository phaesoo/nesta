#!/bin/bash

source ./conf.sh

python -m absinthe.control --item=$1 --config_path=./absinthe/configs/debug.yml $@
