#!/bin/bash

Me=$( readlink -m $( type -p $0 ))
MYDIR=`dirname $Me`

echo "clean the process_input testing directory."

source $MYDIR/../../../../.model_def_dir.sh

source $Trashrc $ROOTDIR

cd $MYDIR

rm output/* 2> /dev/null
cd work
shopt -s extglob
rm !(geo_em.d01.nc|geo_em.d02.nc|geo_em.d03.nc|namelist.input) 2> /dev/null
#rm !(namelist.input)
