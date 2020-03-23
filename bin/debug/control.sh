#!/bin/bash

source ./conf.sh || exit 1

python nesta/control/control.py $@
