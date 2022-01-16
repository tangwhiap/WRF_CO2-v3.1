#!/bin/bash

#CLEANALL=true

#COMPILEWPS=true

CLEANALL=$1

COMPILEWPS=$2

Me=$( readlink -m $( type -p $0 ))
MYDIR=`dirname $Me`
cd $MYDIR

source .model_def_dir.sh

$TracersSrc/wrf_compile.sh $CLEANALL

if [[ $COMPILEWPS == "true" ]];then
    $TracersSrc/wps_compile.sh
fi
