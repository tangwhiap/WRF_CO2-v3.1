#!/bin/bash
# Authors:
#   Wenhan TANG - 11/2020
#   ...

source ./config/configure.sh
source ./config/wps_input.sh
cd $CASEWORK
EndDate=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y-%m-%d"`
EndTime=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%H:%M"`

interval_seconds=`python -c "print( int ( ${MetDataDt} * 3600 ) )"`
cat > $CASEWORK/nml/nml-wrf.ngs << EOF
open &: $CASEWORK/nml/nml-wrf
mod &: start_year = [int("${StartDate:0:4}"), int("${StartDate:0:4}"), int("${StartDate:0:4}")]
mod &: start_month = [int("${StartDate:5:2}"), int("${StartDate:5:2}"), int("${StartDate:5:2}")]
mod &: start_day = [int("${StartDate:8:2}"), int("${StartDate:8:2}"), int("${StartDate:8:2}")]
mod &: start_hour = [int("${StartTime:0:2}"), int("${StartTime:0:2}"),int("${StartTime:0:2}")]
mod &: start_minute = [int("${StartTime:3:2}"), int("${StartTime:3:2}"), int("${StartTime:3:2}")]

mod &: end_year = [int("${EndDate:0:4}"), int("${EndDate:0:4}"), int("${EndDate:0:4}")]
mod &: end_month = [int("${EndDate:5:2}"), int("${EndDate:5:2}"), int("${EndDate:5:2}")]
mod &: end_day = [int("${EndDate:8:2}"), int("${EndDate:8:2}"), int("${EndDate:8:2}")]
mod &: end_hour = [int("${EndTime:0:2}"), int("${EndTime:0:2}"), int("${EndTime:0:2}")]
mod &: end_minute = [int("${EndTime:3:2}"), int("${EndTime:3:2}"), int("${EndTime:3:2}")]
mod &: interval_seconds = ${interval_seconds}
save &: $CASEWORK/nml/nml-wrf
EOF
$NGSDir/main_ngs.py $CASEWORK/nml/nml-wrf.ngs
if [[ $set_time_step_by_user == "false" ]]; then
    $RunScriptsDir/time_step_set.py $CASEWORK/nml/nml-wrf
fi
$RunScriptsDir/special_setting_nml-wrf.sh
cp -p $CASEWORK/nml/nml-wrf $CASEWORK/namelist.input

cp -p $CASEWORK/config/var_output.set $CASEWORK/io_fields_twh.txt

echo "Running real.exe ..."
$CASEWORK/real.exe
cp -p rsl.out.0000 real.log

echo "Modifying WRF initial condition and boundary condition files ..."
#$BckgProcDir/modify_bckg.py $Background $CASEWORK
$BckgProcDir/modify_bckg.py $CASENAME $CASEWORK

