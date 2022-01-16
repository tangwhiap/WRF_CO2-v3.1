#!/bin/bash
#  Shell scripts for running xco2.py (utils/XCO2/Scripts/xco2_2.py)
#  Authors:
#    Wenhan TANG - 04/2021
#    ....

source ./config/configure.sh
source ./config/max_dom.sh
source $Trashrc $ROOTDIR
Start=$1
End=$2
dtMins=15
InDir=$CASEOUT/wrfco2
OutDir=$CASEOUT/wrfxco2
if [ ! -d $OutDir ]; then
    mkdir $OutDir
fi
for (( dom=1;dom<=${max_dom};dom++ )); do
    echo "Caculating XCO2 for domain ${dom} ..."
    $XCO2Dir/Scripts/xco2_2.py "$Start" "$End" $dtMins $dom $InDir $OutDir $CASENAME
done


