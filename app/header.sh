#!/bin/bash

if ! hash python; then
    echo "$0 requires python 2.7 or greater to be installed. Please install python"
    exit 1
fi

PY_VERSION="$(python --version 2>&1)"
ver=$(echo $PY_VERSION | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
if [ "$ver" -lt "27" ]; then
    echo "$0 requires python 2.7 or greater to be installed (got $PY_VERSION in $(which python))"
    exit 1
fi

python -suES "$0" "$@"

exit $?

# Python zipapp contents below
# ----------------------------
