#!/bin/bash

source ./conf.sh || exit 1

python absinthe/server/server.py
