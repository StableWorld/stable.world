#!/bin/bash

# print when 'DEBUG' envvar is set
decho () {
  if [ ! -z "${DEBUG}" ]; then
    echo $0 [$(date)] $*
  fi
}

PYTHON="$(which python)"
decho Found python $PYTHON
if [ -z "${PYTHON}" ]; then
    echo "$0 requires python 2.7 or greater to be installed. Please install python"
    exit 1
fi



PY_VERSION="$($PYTHON --version 2>&1)"
decho $PY_VERSION

ver=$(echo $PY_VERSION | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
if [ "$ver" -lt "27" ]; then
    echo "$0 requires python 2.7 or greater to be installed (got $PY_VERSION in $(which python))"
    exit 1
fi
decho running command $PYTHON -suES "$0" "$@"
$PYTHON -suES "$0" "$@"

exit $?

# Python zipapp contents below
# ----------------------------
