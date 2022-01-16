#!/bin/bash
# Authors:
#    Wenhan TANG - 12/2020
#    ...

source ./config/configure.sh
source ./config/max_dom.sh

if [[ $BinaryOut == "false" ]]; then
    exit
fi

if [[ $RUNTYPE == "normal" ]]; then
    restart=false
fi
if [[ $RUNTYPE == "cronjob" ]]; then
    source $CASERUN/.cronjob_started.sh
    if [[ $StartDate == $first_StartDate ]] && [[ $StartTime == $first_StartTime ]]; then
        first=true
    else
        first=false
    fi

    if [[ $first == "true" ]]; then
        restart=false
    fi
    if [[ $first == "false" ]]; then
        restart=true
    fi
fi

if [[ ! -d $CASEOUT/wrfbin ]]; then
    mkdir -p $CASEOUT/wrfbin
fi
ModelStart=${StartDate}_${StartTime}:00
ModelEnd=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y-%m-%d_%H:%M:%S"`
#echo $restart
#echo $ModelStart
#echo $ModelEnd
#echo $CASEOUT
#echo $CASEWORK
#echo $CASERES

if [[ $restart == "false" ]]; then
    for (( dom=1;dom<=${max_dom};dom++ )); do
        $WRF2BINDir/BinaryOut.py $ModelStart $ModelEnd $dom $CASEOUT/wrfco2 23 $CASEOUT/wrfbin $CASEWORK $CASERES $BinaryOut $BinHourlyOut $BinDailyOut $BinMonthlyOut $restart
    done
elif [[ $restart == "true" ]]; then
    for (( dom=1;dom<=${max_dom};dom++ )); do
        $WRF2BINDir/BinaryOut.py $ModelStart $ModelEnd $dom $CASEOUT/wrfco2 23 $CASEOUT/wrfbin $CASEWORK $CASERES $restart
    done
else
    echo "Fatal Error!!! Invalid value of \"restart\" (= $restart)"
    exit
fi
