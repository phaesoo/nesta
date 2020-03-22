#!/bin/bash

source ./conf.sh

# run test server
python absinthe/server/server.py

# run test
pytest -s .

# terminate test server
python absinthe/control/control.py server terminate
