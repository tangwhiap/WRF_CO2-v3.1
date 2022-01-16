#!/bin/bash
#  Authors:
#    C. Martin - 03/2017
#    Wenhan TANG - 11/2020
#    ...
 
DIR=`pwd`
source $DIR/../config/configure.sh

#wrfinprefix='wrfrst'
#alias logt='date -u +"%Y/%m/%d %H:%M:%S"' # alias for time format for logging
#shopt -s expand_aliases # make alias available for use

echo "##############################################################"
echo "               WRF-CO2 Wrapper Execution Script"
echo "                C. Martin - Univ. of MD - 2017"
echo ""
echo "            PLEASE REPORT ANY BUGS TO WENHAN TANG at"
echo "                    tangwh@mail.iap.ac.cn"
echo "##############################################################"
#echo "------          Script starting: "`logt`" UTC           ------"


# Set domain options to namelist.wps for WPS geogrid.exe
cd $CASEWORK

$RunScriptsDir/run_init.sh

$RunScriptsDir/run_WPS.sh

$RunScriptsDir/run_real.sh

$RunScriptsDir/driver.sh

