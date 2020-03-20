#!/bin/bash

source ./conf.sh

python -m absinthe.server --config_path=./absinthe/configs/debug.yml
