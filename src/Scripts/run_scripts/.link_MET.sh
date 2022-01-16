#!/bin/bash
# 
# Authors:
#  ZhengKe - 09/2019 (Original version)
#  Wenhan Tang - 12/2020 (rewrite it, adapt to Input Data API)

source ./config/configure.sh
alias logt='date -u +"%Y/%m/%d %H:%M:%S"' # alias for time format for logging
shopt -s expand_aliases # make alias available for use

echo `logt`
echo "=================== Start Linking ==================="
cd $CASEWORK
#if [ $RunHrs -gt 120 ];then
#  echo `logt`": Linking SST data"
#  cd $rootdir/../input/SST
#  rm -rf *
#  EndDateSST=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y%m%d"`
#  Currenttime=$(date -d "$StartDate $StartTime" +"%Y%m%d")
#  echo $Currenttime  $EndDateSST
#  while [ $Currenttime -le $EndDateSST ];
#  do
#    #echo $Currenttime
#    ln -s $SSTdir/rtg_sst_grb_hr_0.083.$Currenttime .
#    echo "linking $SSTdir/rtg_sst_grb_hr_0.083.$Currenttime to $rootdir/../input/SST "
#    Currenttime=$(date -d "${Currenttime} 1days" +%Y%m%d)
#  done
#fi
mkdir metdata
echo `logt`": Linking Met data"
StartTimeInt=`date -d "$StartDate $StartTime" +"%Y%m%d%H%M"`
EndTimeInt=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y%m%d%H%M"`
CurrentTime=$(date -d "$StartDate $StartTime" +"%Y-%m-%d %H:%M")
CurrentTimeInt=$(date -d "$CurrentTime" +%Y%m%d%H%M)
#echo $CurrentTime
#echo $CurrentTimeInt $EndTimeInt
while [ $CurrentTimeInt -le $EndTimeInt ];
    do
#     echo $CurrentTime
#     echo $CurrentTimeInt
    cmd="export MetFileName=`date -ud \"${CurrentTime}\" +\"${MetNameForm}\"`"
    $cmd
    ln -sf $MetDataDir/$MetFileName ./metdata
    echo "linking $MetDataDir/$MetFileName to $CASEWORK/metdata "
    CurrentTime=$(date -d "${CurrentTime} ${MetDataDt}hour" +"%Y-%m-%d %H:%M")
    CurrentTimeInt=$(date -d "$CurrentTime" +%Y%m%d%H%M)
done

echo `logt`
echo "=================== Finish Linking ==================="

