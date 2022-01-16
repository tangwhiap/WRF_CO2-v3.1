#!/bin/bash


source ./config/configure.sh


$RunScriptsDir/run_init.sh

source ./config/wps_input.sh

# Set time options to namelist.wps for WPS ungrib.exe
## Caculate end date and time
#EndDate=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y-%m-%d"`
#EndTime=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%H:%M"`
#echo "Start: $StartDate $StartTime:00"
#echo "End: $EndDate $EndTime:00"

#interval_seconds=`python -c "print( int( ${MetDataDt} * 3600 ) )"`

cd $CASEWORK
cat > ./nml/nml-geogrid.ngs << EOF
###  WARNING  ###
# This script is generated automatically by run_WPS.sh.
# Don't edit, your changes to this file will lost.
open &: ./nml/nml-wps
mod &: geog_data_path = "$GeoDataDir"
mod &: opt_geogrid_tbl_path = "$WPSDir/geogrid"
save &: ./nml/nml-wps
EOF

$NGSDir/main_ngs.py $CASEWORK/nml/nml-geogrid.ngs

$RunScriptsDir/run_setdom.sh wps

cp -p ./nml/nml-wps $CASEWORK/namelist.wps

echo "Running geogrid.exe ..."
$CASEWORK/geogrid.exe > $CASEWORK/geogrid.out.log 2> $CASEWORK/geogrid.err.log
tail -n 3 $CASEWORK/geogrid.out.log

cd $CASEWORK
source $Trashrc $ROOTDIR
shopt -s extglob
rm !(config|nml|geo_em*.nc|*.log) 2> /dev/null
cd nml
rm !(nml-wps_demo|nml-wrf_demo) 2> /dev/null
cd $CASECONFIG
rm wps_input.sh 2> /dev/null





