#!/bin/bash
# Authors:
#    Ruqi YANG - 12/2020
#    Wenhan TANG - 12/2020
#    ...

source ./config/configure.sh
source ./config/max_dom.sh
source $Trashrc $ROOTDIR
#CASEOUT=/home/tangwh/WRF-CO2-v3.0/cases/test1/output
#CASECONFIG=/home/tangwh/WRF-CO2-v3.0/cases/test1/config
#CASEWORK=/home/tangwh/WRF-CO2-v3.0/cases/test2/work
#StartDate='2019-01-01'
#StartTime='00:00'
#RunHrs=6
#max_dom=1
#BinHourlyOut=true
#BinMonthlyOut=true
#BinDailyOut=true


StartTime=${StartTime}:00
TempDir=./.wrf2bin_temp
EndDate=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y-%m-%d"`
EndTime=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%H:%M:%S"`
if [[ ! -d $CASEOUT/wrfbin ]]; then
    mkdir -p $CASEOUT/wrfbin
fi
for (( i=1;i<=${max_dom};i++ )); do
    $WRF2BINDir/wrf2bin.py ${StartDate}_${StartTime} ${EndDate}_${EndTime} $i $CASEOUT/wrfco2 $CASEOUT/wrfbin $CASEWORK $TempDir $BinHourlyOut $BinDailyOut $BinMonthlyOut 
done
    
