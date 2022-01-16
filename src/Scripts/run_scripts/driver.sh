#!/bin/bash
# Authors:
#    C. Martin - 03/2017
#    Wenhan TANG - 11/2020
#    ...

source ./config/configure.sh
source ./config/wps_input.sh
source $Trashrc $ROOTDIR

cd $CASEWORK
#EndDate=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y-%m-%d"`
#EndTime=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%H:%M"`

max_dom=`ls -l wrfinput_d* | grep "^-" | wc -l`
check_link_restart()
{
    datetime=$1
    islink=$2
    date=`date -ud "$datetime" +"%Y-%m-%d"`
    time=`date -ud "$datetime" +"%H:%M:%S"`
    haverst=true
#rstfiles1=`ls $CASEWORK/wrfrst_d*_${date}_${time}`
#rstfiles2=`ls $CASERES/wrfrst_d*_${date}_{$time}`
#rstfiles="$rstfiles1 $rstfiles2"
    for (( i=1;i<=${max_dom};i++ )); do
        dom=`python -c "print(\"d\" + str($i).zfill(2))"`
        echo "Searching wrfrst_${dom}_${date}_${time} ..."
        if [[ ! -f $CASEWORK/wrfrst_${dom}_${date}_${time} ]]; then
            if [[ ! -f $CASERES/wrfrst_${dom}_${date}_${time} ]]; then
                echo "Fatal Error! wrfrst_${dom}_${date}_${time} not found!"
                haverst=false
            else
                if [[ $islink == "true" ]]; then
                    echo "wrfrst_${dom}_${date}_${time} is found in ${CASERES}, link it to ${CASEWORK}"
                    ln -sf $CASERES/wrfrst_${dom}_${date}_${time} $CASEWORK/wrfrst_${dom}_${date}_${time}
                fi
            fi
        else
            echo "wrfrst_${dom}_${date}_${time} is found in ${CASEWORK}"
        fi
    done
}

mv_wrfco2_prevent_recovery()
{
    files=$@
    if [[ $wrfco2Dir == "" ]]; then
        echo "Error, unsigned variable: \"wrfco2Dir\""
        exit
    fi
    for ifile in $files
    do
        if [ ! -f $wrfco2Dir/$ifile ]; then
            mv $ifile $CASEWORK/temp_wrfco2
        fi
    done
}

ModelStart="$StartDate $StartTime"
ModelEnd=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y-%m-%d %H:%M"`
ModelStartInt=`date -ud "$ModelStart" +"%Y%m%d%H"`
ModelEndInt=`date -ud "$ModelEnd" +"%Y%m%d%H"`
echo $ModelEnd
echo  "*******************************************************" 
echo `logt`':WRF-CO2: now running a simulation...'
echo "ModelStartInt:"$ModelStartInt
echo "ModelEndInt:"$ModelEndInt

CurrentTime=$ModelStart
CurrentTimeInt=$ModelStartInt

while [[ $CurrentTimeInt -lt $ModelEndInt ]]; do
    isFirst=false
    if [[ $CurrentTimeInt -eq $ModelStartInt ]]; then
      if [ "$RestartRun" = false ] ; then
            isFirst=true
      fi
    fi
    CycleStart=$CurrentTime
    CycleEnd=`date -ud "$CycleStart UTC +$CycleHrs hour" +"%Y-%m-%d %H:%M"`
    echo ""
    echo  `logt`":WRF-CO2: running cycle start "    
    echo "Cycle start: $CycleStart"
    echo "Cycle end:   $CycleEnd"

    if [[ $isFirst == "false" ]]; then
        check_link_restart "$CycleStart" true
        if [[ $haverst == "false" ]]; then
            echo "!!! --------- Fatal Error --------- !!!"
            echo "!!!  Restart files are not complete !!!"
            echo "!!!      Fail to run WRF-Chem       !!!"
            echo "!!! ------------------------------- !!!"
            echo "Check the restart files in $CASEWORK or $CASERES"
            exit
        fi
    fi
    #Run WRF
    echo "Start running WRF-Chem"
    $RunScriptsDir/run_WRF.sh "$CycleStart" "$CycleEnd" $isFirst

    CTI=`date -ud "$CycleStart" +"%Y%m%d%H"`
    mkdir $CASEWORK/${CTI}.log
    cp $CASEWORK/namelist.input $CASEWORK/${CTI}.log/
    cp $CASEWORK/rsl.out.* $CASEWORK/${CTI}.log/
    cp $CASEWORK/rsl.error.* $CASEWORK/${CTI}.log/
    echo  `logt`":WRF-CO2: running cycle end "    
    check_link_restart "$CycleEnd" true
    if [[ $haverst == "false" ]]; then
        echo "!!! --------- Fatal Error --------- !!!"
        echo "!!!  Restart files are not created  !!!"
        echo "!!!      Fail to run WRF-Chem       !!!"
        echo "!!! ------------------------------- !!!"
        echo "Check the log files to find where the bug is."
        echo "If you don't know what caused this error,"
        echo "please contact Wenhan Tang (tangwh@mail.iap.ac.cn)"
        exit
    fi

    # Moving and Moditying wrfco2 output files
    # I used to do it after the end of the whole period, but I found WRF-chem will output the first time wrfco2* file which can recover the last one, letting some variables like E_CO2_FFE become zeros.
    # write_hist_at_0h_rst = .false. doesn't work for auxhist output such as wrfco2*.
    # So I do these by the end of each cycle, use the function "mv_wrfco2_prevent_recovery" to prevent recovery.
    wrfco2Dir=$CASEOUT/wrfco2
    if [ ! -d $wrfco2Dir ]; then
        mkdir -p $wrfco2Dir
    fi
    if [ ! -d $CASEWORK/temp_wrfco2 ]; then
        mkdir -p $CASEWORK/temp_wrfco2
    fi
    cd $CASEWORK
    mv_wrfco2_prevent_recovery wrfco2*
    if [[ $RUNTYPE == "normal" ]]; then
#mv $CASEWORK/wrfco2_* $wrfco2Dir
        $ADDTMDir/add_xtime.py $CASEWORK/temp_wrfco2 $wrfco2Dir $StartDate $StartTime &> add_xtime.log
    fi
    if [[ $RUNTYPE == "cronjob" ]]; then
        source $CASERUN/.cronjob_started.sh
        $ADDTMDir/add_xtime.py $CASEWORK/temp_wrfco2 $wrfco2Dir $first_StartDate $first_StartTime &> add_xtime.log
    fi
    rm $CASEWORK/temp_wrfco2   

    # Caculating XCO2 
    if [[ $XCO2Out == "true" ]]; then
        XCO2Start=`date -ud "$CycleStart" +"%Y-%m-%d_%H:%M:%S"`
        XCO2End=`date -ud "$CycleEnd" +"%Y-%m-%d_%H:%M:%S"`
        $RunScriptsDir/run_XCO2.sh $XCO2Start $XCO2End
    fi
    CurrentTime=$CycleEnd
    CurrentTimeInt=`date -ud "$CurrentTime" +"%Y%m%d%H"`
done

# Sorting log files.
logDir=$CASELOG/`echo $ModelStartInt`
mkdir -p $logDir
mv $CASEWORK/*.log $logDir
#mv $CASELOG/runlog* $logDir

# Sorting and modifying wrfco2 output files.
#wrfco2Dir=$CASEOUT/wrfco2
#mkdir -p $wrfco2Dir
#mkdir -p $CASEWORK/temp_wrfco2
#mv $CASEWORK/wrfco2_* $CASEWORK/temp_wrfco2
#if [[ $RUNTYPE == "normal" ]]; then
##mv $CASEWORK/wrfco2_* $wrfco2Dir
#    $ADDTMDir/add_xtime.py $CASEWORK/temp_wrfco2 $wrfco2Dir $StartDate $StartTime &> add_xtime.log
#fi
#if [[ $RUNTYPE == "cronjob" ]]; then
#    source $CASERUN/.cronjob_started.sh
#    $ADDTMDir/add_xtime.py $CASEWORK/temp_wrfco2 $wrfco2Dir $first_StartDate $first_StartTime &> add_xtime.log
#fi

# Creating ctl files for wrfco2.
if [[ $OrigCtlOut == "true" ]]; then
    $CRCTLDir/create_ctl_for_wrfco2.py $CASEOUT/wrfco2 $CASEWORK
fi

# Converting output files from netCDF to binary, computing hourly/daily/monthly mean at same time.
if [[ $BinaryOut == "true" ]]; then
    # There are two versions of wrf2bin program (run_wrf2bin_v1.sh & run_wrf2bin_v2.sh), you can choose one.
    # For cronjob run, version 2 is better.

# version 1:
    # $RunScriptsDir/run_wrf2bin_v1.sh &> wrf2bin.log
# version 2:
    $RunScriptsDir/run_wrf2bin_v2.sh #&> wrf2bin.log
fi

# Saving 
if [[ $OrigSave == "true" ]]; then
    wrfoutDir=$CASEOUT/wrfout
    mkdir -p $wrfoutDir
    mv $CASEWORK/wrfout_* $wrfoutDir
fi
if [[ $RUNTYPE == "cronjob" ]]; then
    if [[ $RestartRun == "false" ]]; then
        sed -i "/RestartRun=/cRestartRun=true" config/configure.sh
    fi
fi

interval=`python -c "import f90nml as nml;f=nml.read(\"$CASEWORK/namelist.input\");print(str(f[\"time_control\"][\"auxhist23_interval\"])[1:-1])"`
echo "interval : $interval"
ModelEndDate=`date -ud "$ModelEnd" +"%Y-%m-%d"`
ModelEndTime=`date -ud "$ModelEnd" +"%H:%M:%S"`
mv $CASEWORK/wrfrst_d*_${ModelEndDate}_${ModelEndTime} $CASERES
cd $CASEDIR
$CASEDIR/clear_casework.sh

# Start post processing programs.
#$RunScriptsDir/postproc.sh $StartDate $StartTime $RunHrs $max_dom $CASENAME $CASEOUT $CASEPLOT $RUNTYPE $BENCHDir $OBS2GRIDDir $Trashrc $ROOTDIR $RestartRun "$interval" $WebCaseDir
