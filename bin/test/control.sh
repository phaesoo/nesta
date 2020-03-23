#!/bin/bash

source ./conf.sh || exit 1

python absinthe/control/control.py $@
