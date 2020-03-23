#!/bin/bash

source ./conf.sh || exit 1

# run test server
python absinthe/server/server.py || exit 1

# run test
pytest -s .

# terminate test server
python absinthe/control/control.py server terminate
