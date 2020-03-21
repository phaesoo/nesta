#!/bin/bash

source ./conf.sh

python -m absinthe.control --item=$1 $@
