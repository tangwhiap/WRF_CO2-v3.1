#!/bin/bash
# WRF-CO2 version 3.0
# Published on 12/2020

# Main Script of WRF-CO2, prepared for beginners.
# You can just execute this script to run the whole model,
# or, run the model step by step.

# Authors:
#   Wenhan Tang - 12/2020
#   ...

# To make sure the current directory is the ROOTDIR of model
Me=$( readlink -m $( type -p $0 ))
MyDir=`dirname $Me`
cd $MyDir

#
####################  SIMULATION OPTIONS  #######################

#== CASE OPTIONS ==#
# CASE name
CASENAME=test1
# Running type, choose one from "normal" and "cronjob"
RUNTYPE=normal
# Restart option, "true" for restart run, while "false" for initial run.
RESTART=false
# User's specific directory for this case. Null for default case directory ($ROOTDIR/cases)
#SPECDIR=
SPECDIR=/home/tangwh/modeldata/WRFCO2_cases
#SPECDIR=/home/tangwh/modeling/WRF-CO2-cases/ffec

#== RUN OPTIONS ==#
# Start date of simulation
StartDate='2019-01-01' 
# Start time of simulation
StartTime='00:00'
# Run hours
RunHrs=120
# Hours of ffe and cfta inputing period.
CycleHrs=1

# Simulation region
Region=BTH_d01 # You can set to "BTH", "BTH_d01", "Maryland", "Maryland_d01", or "User_defined"
if [[ $Region == "User_defined" ]]; then
# If you choose "User_defined", you should set domain options in the namelist-like-script below.
    cat > $MyDir/.setdom.udf << EOF

&User_defined

 ! domain numbers
 max_dom = 3

 ! longitude start (d01, d02, d03, ...)
 xs = 109, 113, 115.5

 ! longitude end (d01, d02, d03, ...)
 xe = 122, 120, 117.5

 ! latitude start (d01, d02, d03, ...)
 ys = 35, 37.5, 39.3

 ! latitude end (d01, d02, d03, ...)
 ye = 43, 42.5, 41.3

 ! longitude resolution (d01, d02, d03, ...)
 dx = 0.106, 0.0353334, 0.0117778

 ! latitude resolution (d01, d02, d03, ...)
 dy = 0.08, 0.0266667, 0.0088889
/
EOF
fi

# mpirun -np $NTASTS
NTASKS=12

#== Input Data OPTIONS ==#
# Fossil fuel emission
Emiss=MEIC
# Cfta from vegas
Cfta=constant
# CO2 background
Background=constant
# Geogrophy data
Geog=WRF_GEOG
# Meteorology data
Met=GFS
# Sea surface temperature data
SST=SST

#== Output Data OPTIONS ==#
OrigSave=false  # true if you want to save the original wrfout files
OrigCtlOut=false  # true if you want to write ctl files for wrfco2* nc files. 
BinaryOut=false   # true if you want to convert output nc files to binary files.
BinHourlyOut=false # true if you want to have hourly mean data.
BinDailyOut=false # true if you want to have daily mean data.
BinMonthlyOut=false # true if you want to have monthly mean data.
XCO2Out=false # true if you want to caculate XCO2.

#=== Special options for cronjob ===#
if [[ $RUNTYPE == "cronjob" ]]; then
    FileType=shell #Type of cronjob file, you can choose "cronfile" or "shell"(recommanded).
# "cronfile": Add the cronjob command at the end of cron table file, then execute "crontab [your cronfile]"
# "shell": Just add the cronjob command at the end of a shell script without executing "crontab [your cronfile]"
#          If you have a shell script which is being executed by another cron table file, you can choose this option.

    CronFile=/home/tangwh/cronjob/wrfco2_cron.sh # Directory of a cron table file (if $FileType == cronfile) or a specific shell script executed by another cron table file (if $FileType == shell)
    #CronFile=/home/tangwh/cronjob/01minute.sh
    PerMin=1 # Minites of interval time for cronjob, being valid if $FileType == cronfile
fi
##################################################################




###########################################
#         Running WRF-CO2 model           #
###########################################

echo "############################################"
echo "#              WRF-CO2 model               #"
echo "#          ->   version 3.0   <-           #"
echo "# PLEASE REPORT ANY BUGS TO WENHAN TANG at #"
echo "#          tangwh@mail.iap.ac.cn           #"
echo "############################################"

echo "Running the initialization programs ..."
cd ini
./init.sh
cd $MyDir
source .model_def_dir.sh
source $Trashrc $ROOTDIR

cd $MKCASEDIR/set_config

echo "Writing the simulation options files *.set ..."
# Add select_input.set
cat > $MKCASEDIR/set_config/select_input.set << EOF
#=== from input_select.set ===#
#=== created by main.sh ===#
# Fossil fuel emission
Emiss=${Emiss}
# Cfta from vegas
Cfta=${Cfta}
# CO2 background
Background=${Background}
# Geogrophy data
Geog=${Geog}
# Meteorology data
Met=${Met}
# Sea surface temperature data
SST=${SST}
EOF

if [[ $Region == "User_defined" ]]; then
    # Add set_domain.set
    cat $MyDir/.setdom.udf > $MKCASEDIR/set_config/set_domain.set
    rm $MyDir/.setdom.udf
fi

# Add set_run.set
cat > $MKCASEDIR/set_config/set_run.set << EOF
#=== from set_runtime.set  ===#
#=== created by main.sh ===#
# Start date of simulation
StartDate='${StartDate}'
# Start time of simulation
StartTime='${StartTime}'
# Run hours
RunHrs=${RunHrs}
# Hours of ffe and cfta inputing period.
CycleHrs=${CycleHrs}
# Simulation region
Region=${Region}
# mpirun -np \$NTASTS
NTASKS=${NTASKS}
# Whether time_step in namelist.input is set by user 
set_time_step_by_user=false # If set to true, time_step_set.py will not be executed and time_step in nml-wrf_demo will be used, one can change the value of time_step in nml-wrf_demo before starting the simulation.
# The execution entrance of this simulation program is main.sh, therefore, modification of this variable is not supported.
EOF

cat > $MKCASEDIR/set_config/file_output.set << EOF
#=== from file_output.set ===#
#=== created by main.sh ===#
OrigSave=${OrigSave}
OrigCtlOut=${OrigCtlOut}
BinaryOut=${BinaryOut}
BinHourlyOut=${BinHourlyOut}
BinDailyOut=${BinDailyOut}
BinMonthlyOut=${BinMonthlyOut}
XCO2Out=${XCO2Out}
EOF

echo "Creating a new case named: $CASENAME ..."
cd $MKCASEDIR
$MKCASEDIR/create_newcase.sh $CASENAME $RUNTYPE $RESTART $SPECDIR
if [ ! -f $MKCASEDIR/.case_${CASENAME}_created_successfully ]; then
    echo ""
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "*** Failed to create the case: ${CASENAME}. Exit! *** "
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit
fi

cd $CASESDIR/$CASENAME
source $CASESDIR/$CASENAME/configure
cd $CASERUN
if [[ $RUNTYPE == "normal" ]]; then
    echo "Start simulation with \"normal\" mode."
    $CASERUN/nohuprun.sh
    echo ""
    echo "====================================================================="
    echo "      The program is running in the background on the computer."
    echo "    You can use the \"ps ux\" command to view the running status."
    echo "====================================================================="
    echo ""
    exit
fi
if [[ $RUNTYPE == "cronjob" ]]; then
    echo "Start simulation with \"cronjob\" mode."
    $CASERUN/start_cronjob.sh $CronFile $FileType $PerMin
    echo ""
    echo "==================================================================================="
    echo "            The program is running in the background on the computer."
    echo "    The cronjob command of this simulation has been added to the crontab script."
    echo "        You can use the \"ps ux\" command to view the running status."
    echo "You can use the \"crontab -l\" command to check the contents of the crontab script."
    echo "==================================================================================="
    echo ""
    exit
fi
