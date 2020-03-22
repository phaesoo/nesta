#!/bin/bash

source ./conf.sh

python -m absinthe.server

pytest -v .
