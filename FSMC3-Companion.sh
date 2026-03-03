#!/bin/sh
LOCATION=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
source $LOCATION/venv/bin/activate
python $LOCATION/FSMC3-Companion.py