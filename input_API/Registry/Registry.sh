#!/bin/bash

#APIDir=/home/tangwh/wrf-latlon/input_API
#PrepSrcDir=/home/tangwh/wrf-latlon

#APIDir=$1
#SrcDir=$2
source .model_def_dir.sh
./main_registry.py $APIDir $ScriptsDir
