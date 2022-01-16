#!/bin/bash
# Authors:
#    Wenhan TANG - 02/2021
#    ...

Me=$( readlink -m $( type -p $0 ))
MyDir=`dirname $Me`
cd $MyDir


if [ ! -f .model_def_dir.sh ]; then
    echo "Can't find .model_def_dir.sh!"
    echo "Please execute \$ROOTDIR/ini/init.sh first!" 
    exit
fi
source .model_def_dir.sh
source $Trashrc $ROOTDIR

if_clear_cases=$1
echo "!!!     Do you really want to restore this model     !!!"
echo "!!! Please confirm that there isn't any running case !!!"
echo "!!!             Enter \"yes\" to go on               !!!"
read confirm
if [[ ! $confirm == "yes" ]]; then
    echo "Exit!"
    exit
fi

echo "Running clear.sh in MAKE CASE module ..."
cd $MKCASEDIR
$MKCASEDIR/clear.sh

echo "Running unRegistry.sh in Input Data API Registry module ..."
cd $APIRegDir
$APIRegDir/unRegistry.sh

echo "Running clear.sh in Initialization module ..."
cd $INIDIR
$INIDIR/clear.sh

#rm $InputProcDir/__pycache__ 2> /dev/null
#rm $BckgProcDir/__pycache__ 2> /dev/null
#$InputProcDir/test/clear.sh

if [[ $if_clear_cases == "clear_cases" ]]; then
    echo ""
    echo "=============  CASES LIST ================="
    ls -all $CASESDIR
    echo "==========================================="
    echo ""
    echo "!!! Do you really want to delete all cases !!!"
    echo "If sure, please enter \"Yes_clear_them!\" to go on."
    read confirm
    if [[ $confirm == "Yes_clear_them!" ]]; then
        echo "Removing cases ..."
        rm $CASESDIR
        mkdir -p $CASESDIR
        echo "Done."
        $InputProcConfigDir/clean.sh
        rm $InputProcConfigDir/__pycache__ 2> /dev/null
        $BckgProcConfigDir/clean.sh
        rm $BckgProcConfigDir/__pycache__ 2> /dev/null
        $XCO2ConfigDir/clean.sh
        rm $XCO2ConfigDir/__pycache__ 2> /dev/null
    else
        echo "Exit!"
        exit
    fi
fi
