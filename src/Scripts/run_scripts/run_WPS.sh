#!/bin/bash
# Authors:
#    Wenhan TANG - 11/2020
#    ...


source ./config/configure.sh
source ./config/wps_input.sh

# Set time options to namelist.wps for WPS ungrib.exe
## Caculate end date and time
EndDate=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y-%m-%d"`
EndTime=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%H:%M"`
#echo "Start: $StartDate $StartTime:00"
#echo "End: $EndDate $EndTime:00"

interval_seconds=`python -c "print( int( ${MetDataDt} * 3600 ) )"`
cat > ./nml/nml-wps.ngs << EOF
###  WARNING  ###
# This script is generated automatically by run_WPS.sh.
# Don't edit, your changes to this file will lost.
open &: ./nml/nml-wps
mod &: start_date = [ "${StartDate}_${StartTime}:00","${StartDate}_${StartTime}:00","${StartDate}_${StartTime}:00"]
mod &: end_date = [ "${EndDate}_${EndTime}:00","${EndDate}_${EndTime}:00","${EndDate}_${EndTime}:00"]
mod &: interval_seconds = ${interval_seconds}
mod &: geog_data_path = "$GeoDataDir"
mod &: opt_geogrid_tbl_path = "$WPSDir/geogrid"
mod &: opt_metgrid_tbl_path = "$WPSDir/metgrid"
save &: ./nml/nml-wps
EOF

$NGSDir/main_ngs.py $CASEWORK/nml/nml-wps.ngs

$RunScriptsDir/run_setdom.sh wps

cp -p ./nml/nml-wps $CASEWORK/namelist.wps

echo "Running geogrid.exe ..."
$CASEWORK/geogrid.exe > geogrid.out.log 2> geogrid.err.log
tail -n 3 geogrid.out.log

# link Vtable
if [ -h $CASEWORK/Vtable ]; then
    unlink $CASEWORK/Vtable
fi
ln -s $WPSDir/ungrib/Variable_Tables/Vtable.$MetVtableName $CASEWORK/Vtable

$CASEWORK/link_grib.csh $CASEWORK/metdata/*  
echo "Running ungrib.exe for extracting meteorology data ..."
$CASEWORK/ungrib.exe > ungrib.out.log 2> ungrib.err.log
tail -n 1 ungrib.log

mv ungrib.out.log ungrib.met.out.log
mv ungrib.err.log ungrib.met.err.log
mv ungrib.log ungrib.met.log

if [ $RunHrs -gt 120 ];then
    unlink $CASEWORK/Vtable
    ln -sf $WPSDir/ungrib/Variable_Tables/Vtable.$SSTVtableName $CASEWORK/Vtable
    $NGSDir/NLO "mod &: prefix = \"SST\" | namelist.wps"
    $NGSDir/NLO "mod &: fg_name = [ \"FILE\" , \"SST\" ] | namelist.wps"
    $CASEWORK/link_grib.csh $CASEWORK/sstdata/*
    echo "Running ungrib.exe for extracting sea surface temperature(SST) data ..."
    $CASEWORK/ungrib.exe > ungrib.sst.out.log 2> ungrib.sst.err.log
    tail -n 1 ungrib.log
    mv ungrib.log ungrib.sst.log
fi

echo "Running metgrid.exe ..."
$CASEWORK/metgrid.exe > metgrid.out.log 2> metgrid.err.log
tail -n 3 metgrid.out.log

$RunScriptsDir/run_setdom.sh wrf
