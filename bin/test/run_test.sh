#!/bin/bash

source ./conf.sh

python -m absinthe.server --config_path=./tests/configs/test.yml

pytest -v .
