#!/bin/bash
# link_WPS
# symbolically link files from WPS compiled dir
# to work/run dir
# C. Martin - 1/2017 (Original version)
# Wenhan Tang - 12/2020 (rewrite it, adapt to Input Data API)

#if [ $# -ne 3 ]
#  then
#    echo "link_WPS wpsdir metinput rundir"
#    exit
#fi

#wpsdir=$1
#metinput=$2
#rundir=$3

source ./config/configure.sh
wpsfiles="
    geogrid.exe
    link_grib.csh
    metgrid.exe
    ungrib.exe
    "

for f in $wpsfiles; do
  ln -s $WPSDir/$f $CASEWORK/$f
done

# link Vtable
ln -s $WPSDir/ungrib/Variable_Tables/Vtable.$MetVtableName $CASEWORK/Vtable

# link WRF run
ln -s $WRFDir/run/* $CASEWORK/.
