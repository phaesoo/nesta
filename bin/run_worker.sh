#!/bin/bash

# change current directory
MODULE_PATH=$( cd "$(dirname "$0")" ; pwd )
cd ${MODULE_PATH}
cd ..

source .venv/bin/activate

celery -A regista.tasks.tasks worker --loglevel=info 
