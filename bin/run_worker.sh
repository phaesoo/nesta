#!/bin/bash

source ./conf.sh

python -m absinthe.worker --config_path=./absinthe/configs/debug.yml
