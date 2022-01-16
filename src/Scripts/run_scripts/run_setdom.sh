#!/bin/bash
# Can only run in $CASEWORK
#echo `pwd`
source ./config/configure.sh
nmlType=$1
if [[ $nmlType == "wps" ]]; then
    $SetdomDir/wps_setdom.py $CASEWORK/config/setdom.nml $CASEWORK/nml/nml-wps $CASEWORK/nml/nml-wps.ngs $Region
    $NGSDir/main_ngs.py $CASEWORK/nml/nml-wps.ngs
fi

if [[ $nmlType == "wrf" ]]; then
    $SetdomDir/wrf_setdom.py $CASEWORK $CASEWORK/nml/nml-wrf $CASEWORK/nml/nml-wrf.ngs $StartDate $StartTime
    $NGSDir/main_ngs.py $CASEWORK/nml/nml-wrf.ngs
fi
