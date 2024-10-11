#! /bin/bash

set -e

mydir=$(dirname $BASH_SOURCE)

cd $mydir

python3 test_writes.py $1
python3 test_cwrites.py $1
