#! /bin/bash

mydir=$(dirname $BASH_SOURCE)

cd $mydir

python3 TestWrites.py $1
