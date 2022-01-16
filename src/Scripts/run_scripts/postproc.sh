#!/bin/bash
# Post processing script for WRF-CO2
# Authors:
#  Wenhan Tang - 12/2020
#  ...
#source ./config/configure.sh
#cd $CASSEWORK

SENSEDIR=/home/tangwh/datasets/SENSE-BB/data/min/L2.0

#StartDate='2020-01-01'
#StartTime='00:00'
#RunHrs=48
#max_dom=1
#CASENAME=exp
#CASEOUT=/home/tangwh/WRF-CO2-v3.0/cases/exp/output
#CASEPLOT=/home/tangwh/WRF-CO2-v3.0/cases/exp/plot
#RUNTYPE=normal
#
#BENCHDir=/home/tangwh/WRF-CO2-v3.0/utils/BenchPlots
#OBS2GRIDDir=/home/tangwh/WRF-CO2-v3.0/utils/obs2grid
#Trashrc=/home/tangwh/WRF-CO2-v3.0/.trashrc
#ROOTDIR=/home/tangwh/WRF-CO2-v3.0

StartDate=$1
StartTime=$2
RunHrs=$3
max_dom=$4
CASENAME=$5
CASEOUT=$6
CASEPLOT=$7
RUNTYPE=$8

BENCHDir=$9
OBS2GRIDDir=${10}
Trashrc=${11}
ROOTDIR=${12}
RestartRun=${13}
interval=${14}
WebCaseDir=${15}

echo "1: $StartDate"
echo "2: $StartTime"
echo "3: $RunHrs"
echo "4: $max_dom"
echo "5: $CASENAME"
echo "6: $CASEOUT"
echo "7: $CASEPLOT"
echo "8: $RUNTYPE"
echo "9: $BENCHDir"
echo "10: $OBS2GRIDDir"
echo "11: $Trashrc"
echo "12: $ROOTDIR"
echo "13: $RestartRun"
echo "14: $interval"
echo "15: $WebCaseDir"

source $Trashrc $ROOTDIR
link_sense()
{
    dir=$1
    if [ -h $dir/SENSE ]; then
        unlink $dir/SENSE
    fi
    ln -sf $SENSEDIR $dir/SENSE
}
unlink_sense()
{
    dir=$1
    if [ -h $dir/SENSE ]; then
        unlink $dir/SENSE
    fi
}
link_sense $BENCHDir

EndDate=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%Y-%m-%d"`
EndTime=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%H:%M"`

if [[ $RestartRun == "false" ]]; then
    TempDate=`date -ud "$StartDate $StartTime UTC +1 hour" +"%Y-%m-%d"`
    TempTime=`date -ud "$StartDate $StartTime UTC +1 hour" +"%H:%M"`
    StartDate=$TempDate
    StartTime=$TempTime
fi
RunHrs=`python -c "print(${RunHrs} - 1)"`
PLOTSDT=`date -ud "$StartDate $StartTime UTC" +"%Y-%m-%d_%H"`
PLOTNAME=PLOT_$PLOTSDT
PLOTDIR=$CASEPLOT/$PLOTNAME
PLOTWORK=$PLOTDIR/plot_work

if [ ! -d $PLOTDIR ]; then
    mkdir -p $PLOTDIR
fi

if [ ! -d $PLOTWORK ]; then
    mkdir -p $PLOTWORK
fi

cd $PLOTWORK
# For obs2grid
link_sense $OBS2GRIDDir/data
if [ -h $OBS2GRIDDir/data/WRF ]; then
    unlink $OBS2GRIDDir/data/WRF
fi
ln -sf $CASEOUT/wrfco2 $OBS2GRIDDir/data/WRF
mkdir -p $PLOTWORK/obs
if [ -h $OBS2GRIDDir/output ]; then
    unlink $OBS2GRIDDir/output
fi
ln -sf $PLOTWORK/obs $OBS2GRIDDir/output

IFS=","
interval_arr=($interval)
for (( dom=1;dom<=${max_dom};dom++ )); do
    domind=`python -c "print(${dom} - 1)"`
    echo "prepare for run_obs2grid.sh ${interval_arr[$domind]}"
    echo ${interval_arr[$domind]}
    $OBS2GRIDDir/src/run_obs2grid.sh ${StartDate}_${StartTime}:00 ${EndDate}_${EndTime}:00 ${dom} ${interval_arr[$domind]}
done
unlink $OBS2GRIDDir/data/WRF
unlink_sense $OBS2GRIDDir/data
unlink $OBS2GRIDDir/output
rm $OBS2GRIDDir/temp/eta_out_*
rm $OBS2GRIDDir/temp/station.dat

# For BenchPlots
echo "BenchPlots"
$BENCHDir/BenchPlots.sh $StartDate $StartTime $RunHrs $max_dom $CASENAME $CASEOUT/wrfbin $PLOTDIR $BENCHDir $PLOTWORK/obs

echo "ok"
IFS="
"
# ps to pdf
psfiles=`ls ${PLOTDIR}/*.ps`
for ifile in $psfiles
do
    echo "ifile = $ifile"
    echo "conv = $PLOTDIR/${ifile%.*}.pdf"
    ps2pdf $ifile ${ifile%.*}.pdf
done

# tar -zcvf
cd $PLOTDIR
#rm $PLOTWORK
tar -zcvf PRINT_ps_${CASENAME}_${PLOTSDT}.tgz *.ps
tar -zcvf PRINT_pdf_${CASENAME}_${PLOTSDT}.tgz *.pdf

username=`whoami`
cat > $PLOTDIR/download_command.txt << EOF

echo "Copy this command and execute it on your PC to download the result."
echo "scp ${username}@iark.cc:$PLOTDIR/PRINT_ps_${CASENAME}_${PLOTSDT}.tgz ."
echo "scp ${username}@iark.cc:$PLOTDIR/PRINT_pdf_${CASENAME}_${PLOTSDT}.tgz ."
EOF
chmod +x $PLOTDIR/download_command.txt
cp -p $PLOTDIR/*.pdf $WebCaseDir
