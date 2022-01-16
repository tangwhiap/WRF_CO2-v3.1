#!/bin/bash
CASEOUT=/home/tangwh/WRF-CO2-v3.0/cases/test1/output
CASECONFIG=/home/tangwh/WRF-CO2-v3.0/cases/test1/config
CASEWORK=/home/tangwh/WRF-CO2-v3.0/cases/test2/work
StartDate='2019-01-01'
StartTime='00:00'
RunHrs=6
max_dom=1
hourly=true
monthly=true
daily=true


StartTime=${StartTime}:00
TempDir=./temp
EndDate=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y-%m-%d"`
EndTime=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%H:%M:%S"`
if [[ ! -d $CASEOUT/wrfbin ]]; then
    mkdir -p $CASEOUT/wrfbin
fi
for (( i=1;i<=${max_dom};i++ )); do
    python wrf2bin.py ${StartDate}_${StartTime} ${EndDate}_${EndTime} $i $CASEOUT/wrfco2 $CASEOUT/wrfbin $CASEWORK $TempDir $hourly $daily $monthly 
done
    
