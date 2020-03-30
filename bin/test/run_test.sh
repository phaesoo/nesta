#!/bin/bash

source `dirname $0`/conf.sh || exit 1

# run test server
python nesta/server/server.py || exit 1

# run test
pytest -s .

# terminate test server
python nesta/control/control.py server terminate
