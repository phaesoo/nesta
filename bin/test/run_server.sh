#!/bin/bash

source `dirname $0`/conf.sh || exit 1

python nesta/server/server.py
