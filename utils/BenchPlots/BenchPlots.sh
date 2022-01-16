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

StartDate=$1
StartTime=$2
RunHrs=$3
max_dom=$4
CASENAME=$5
DataDir=$6
PlotDir=$7
BENCHDir=$8
OBSInDir=$9

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
        grads -pbcx $BENCHDir/Bench_stations.gs
    fi
done
