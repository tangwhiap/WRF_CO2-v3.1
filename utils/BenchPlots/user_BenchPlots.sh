#!/bin/bash

# Using liuzq's GrADS software
export PATH=/home/liuzq/software/grads-2.0.2.oga.2/Classic/bin:$PATH
export GADDIR=/home/liuzq/software/grads-2.0.2.oga.2/Contents/Resources/SupportData
export GASCRP=/home/liuzq/software/grads-2.0.2.oga.2/Contents/Resources/Scripts
export GA2UDXT=/home/liuzq/software/grads-2.0.2.oga.2/Classic/bin/gex/udxt
export LD_LIBRARY_PATH=/home/liuzq/software/grads-2.0.2.oga.2/Classic/bin/gex:$LD_LIBRARY_PATH

#StartDate='2020-01-01'
#StartTime='00:00'
#RunHrs=48
#max_dom=1
#CASENAME=exp
#DataDir=/home/tangwh/WRF-CO2-v3.0/cases/exp/output/wrfbin
#PlotDir=/home/tangwh/WRF-CO2-v3.0/cases/exp/plot/plotwork

StartDate='2020-01-07'
StartTime='00:00'
RunHrs=168
max_dom=1
CASENAME=run_ndrc
DataDir=/home/tangwh/WRF-CO2-v3.0/cases/$CASENAME/output/wrfbin
PlotDir=/home/tangwh/public_html/WRF-CO2-grBench/$CASENAME
BENCHDir=.
OBSInDir=/home/tangwh/WRF-CO2-v3.0/cases/$CASENAME/plot/PLOT_2020-01-01_01/plot_work/obs

mkdir -p $PlotDir

StartDT=`date -ud "$StartDate $StartTime UTC" +"%H:%SZ%d%b%Y"`
EndDT=`date -ud "$StartDate $StartTime UTC +$RunHrs hour" +"%H:%SZ%d%b%Y"`
#%H:%SZ%d%b%Y
for (( dom=1;dom<=${max_dom};dom++ )); do

    cat > .gs_input << EOF
${CASENAME}
${StartDT}
${EndDT}
${DataDir}
${PlotDir}
${dom}
${BENCHDir}
${OBSInDir}
EOF
    grads -pbcx $BENCHDir/Bench_co2_cpn.gs
    grads -pbcx $BENCHDir/Bench_co2_met.gs
    if [ $dom -eq 1 ]; then
        echo "do"
#        grads -pbcx $BENCHDir/Bench_stations.gs
    fi
done
cd $PlotDir
tar -zcvf PRINT.tar.gz *.ps
