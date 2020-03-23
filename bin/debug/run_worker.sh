#!/bin/bash

source ./conf.sh || exit 1

python -m nesta.worker
