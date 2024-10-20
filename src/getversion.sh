#! /bin/bash

VL=$(grep -E "__version__ *=" ../ilff/__init__.py)
bash -c "echo $(echo ${VL##*=})"
