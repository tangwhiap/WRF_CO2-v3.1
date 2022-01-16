#!/bin/bash
# Authors:
#    Wenhan TANG - 11/2020
#    ...


source ./config/configure.sh

CycleStart=$1
CycleEnd=$2
isFirst=$3
#isLinkEmiss=$4
#isLinkCfta=$5

CycleStartDate=`date -ud "$CycleStart UTC" +"%Y-%m-%d"`
CycleStartTime=`date -ud "$CycleStart UTC" +"%H:%M"`

CycleEndDate=`date -ud "$CycleEnd UTC" +"%Y-%m-%d"`
CycleEndTime=`date -ud "$CycleEnd UTC" +"%H:%M"`

if [[ $isFirst == "true" ]]; then
    restart=False
else
    restart=True
fi

cat > $CASEWORK/nml/nml-wrf-${CycleStartDate}_${CycleStartTime}:00.ngs << EOF
open &: $CASEWORK/namelist.input
mod &: start_year = [int("${CycleStartDate:0:4}"), int("${CycleStartDate:0:4}"), int("${CycleStartDate:0:4}")]
mod &: start_month = [int("${CycleStartDate:5:2}"), int("${CycleStartDate:5:2}"), int("${CycleStartDate:5:2}")]
mod &: start_day = [int("${CycleStartDate:8:2}"), int("${CycleStartDate:8:2}"), int("${CycleStartDate:8:2}")]
mod &: start_hour = [int("${CycleStartTime:0:2}"), int("${CycleStartTime:0:2}"),int("${CycleStartTime:0:2}")]
mod &: start_minute = [int("${CycleStartTime:3:2}"), int("${CycleStartTime:3:2}"), int("${CycleStartTime:3:2}")]

mod &: end_year = [int("${CycleEndDate:0:4}"), int("${CycleEndDate:0:4}"), int("${CycleEndDate:0:4}")]
mod &: end_month = [int("${CycleEndDate:5:2}"), int("${CycleEndDate:5:2}"), int("${CycleEndDate:5:2}")]
mod &: end_day = [int("${CycleEndDate:8:2}"), int("${CycleEndDate:8:2}"), int("${CycleEndDate:8:2}")]
mod &: end_hour = [int("${CycleEndTime:0:2}"), int("${CycleEndTime:0:2}"), int("${CycleEndTime:0:2}")]
mod &: end_minute = [int("${CycleEndTime:3:2}"), int("${CycleEndTime:3:2}"), int("${CycleEndTime:3:2}")]
mod &: restart = $restart
save &: $CASEWORK/namelist.input
EOF
$NGSDir/main_ngs.py $CASEWORK/nml/nml-wrf-${CycleStartDate}_${CycleStartTime}:00.ngs

#echo "Making fossil fuel emission using data: $Emiss"
echo "Making fossil fuel emission ..."
inputType=FFE
if [[ $isLinkEmiss == "true" ]]; then
    $EmissProcDir/make_tracers_input.py $CASENAME $inputType --rundir $CASEWORK --link true --origdir $CASEFFE
else
    $EmissProcDir/make_tracers_input.py $CASENAME $inputType --rundir $CASEWORK --core $NTASKS
fi

#echo "Making Cfta using data: $Cfta"
echo "Making Cfta data ..."
inputType=FTA
if [[ $isLinkCfta == "true" ]]; then
    $EmissProcDir/make_tracers_input.py $CASENAME $inputType --rundir $CASEWORK --link true --origdir $CASEFTA
else
    $EmissProcDir/make_tracers_input.py $CASENAME $inputType --rundir $CASEWORK --core $NTASKS
fi

echo "Running WRF-chem ..."
mpirun -np $NTASKS $CASEWORK/wrf.exe

