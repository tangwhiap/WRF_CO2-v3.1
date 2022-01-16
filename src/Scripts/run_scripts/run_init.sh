#!/bin/bash
# Authors:
#   Wenhan TANG - 11/2020
#   ...

source ./config/configure.sh


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

echo "Initializing work directory."
if [[ ! -f $APIGeogDir/_${Geog}_config.sh ]]; then
    echo "Geodata setting Error"
    echo "data \"${Geog}\" can't be found, please check the name."
    echo "If it's a new data, don't forget to register it."
    exit
fi

if [[ ! -f $APIMetDir/_${Met}_config.sh ]]; then
    echo "Meteorology data setting Error"
    echo "data \"${Met}\" can't be found, please check the name."
    echo "If it's a new data, don't forget to register it."
    exit
fi

if [[ ! -f $APISSTDir/_${SST}_config.sh ]]; then
    echo "Meteorology data setting Error"
    echo "data \"${SST}\" can't be found, please check the name."
    echo "If it's a new data, don't forget to register it."
    exit
fi

cat $APIGeogDir/_${Geog}_config.sh|grep -Ev '^$|#' > $CASECONFIG/wps_input.sh
cat $APIMetDir/_${Met}_config.sh|grep -Ev '^$|#' >> $CASECONFIG/wps_input.sh
cat $APISSTDir/_${SST}_config.sh|grep -Ev '^$|#' >> $CASECONFIG/wps_input.sh

source ./config/wps_input.sh

mkdir metdata
StartTimeInt=`date -d "$StartDate $StartTime" +"%Y%m%d%H%M"`
EndTimeInt=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y%m%d%H%M"`
CurrentTime=$(date -d "$StartDate $StartTime" +"%Y-%m-%d %H:%M")
CurrentTimeInt=$(date -d "$CurrentTime" +%Y%m%d%H%M)

while [ $CurrentTimeInt -le $EndTimeInt ]; do
    cmd="export MetFileName=`date -ud \"${CurrentTime}\" +\"${MetNameForm}\"`"
    $cmd
    ln -sf $MetDataDir/$MetFileName ./metdata
    CurrentTime=$(date -d "${CurrentTime} ${MetDataDt}hour" +"%Y-%m-%d %H:%M")
    CurrentTimeInt=$(date -d "$CurrentTime" +%Y%m%d%H%M)
done

if [ $RunHrs -gt 120 ];then
    mkdir sstdata
    StartTimeInt=`date -d "$StartDate $StartTime" +"%Y%m%d%H%M"`
    EndTimeInt=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y%m%d%H%M"`
    CurrentTime=$(date -d "$StartDate $StartTime" +"%Y-%m-%d %H:%M")
    CurrentTimeInt=$(date -d "$CurrentTime" +%Y%m%d%H%M)
    while [ $CurrentTimeInt -le $EndTimeInt ]; do
        cmd="export SSTFileName=`date -ud \"${CurrentTime}\" +\"${SSTNameForm}\"`"
        $cmd
        ln -sf $SSTDataDir/$SSTFileName ./sstdata
        CurrentTime=$(date -d "${CurrentTime} ${SSTDataDt}hour" +"%Y-%m-%d %H:%M")
        CurrentTimeInt=$(date -d "$CurrentTime" +%Y%m%d%H%M)
    done
fi

wpsfiles="
    geogrid.exe
    link_grib.csh
    metgrid.exe
    ungrib.exe
    "

# link_WPS_run
for f in $wpsfiles; do
  ln -s $WPSDir/$f $CASEWORK/$f 2> /dev/null
done


# link WRF run
ln -s $WRFDir/run/* $CASEWORK/. 2> /dev/null
if [ -h $CASEWORK/namelist.input ]; then
    echo "WARNING !!! Find the symbolic link of namelist.input in \$WRFDIR/run, unlink it."
    unlink $CASEWORK/namelist.input
fi

cd $CASEWORK/nml
cat nml-wps_demo > nml-wps
cat nml-wrf_demo > nml-wrf
#cat nml-wrf
