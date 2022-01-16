#!/bin/bash
# Authors:
#    Wenhan TANG - 12/2020
#    ...

Me=$( readlink -m $( type -p $0 ))
MYDIR=`dirname $Me`
cd $MYDIR

if [ ! -f .model_def_dir.sh ]; then
    echo "Please execute \$ROOTDIR/ini/init.sh first!"
    exit
fi

source .model_def_dir.sh
source $Trashrc $ROOTDIR

cd $APIBckgDir/API_code
rm $APIBckgDir/API_code/_config.py
rm $APIBckgDir/API_code/__init__.py
if [ -d $APIBckgDir/API_code/__pycache__ ]; then
    rm $APIBckgDir/API_code/__pycache__
fi
sleep 1

cd $APICftaDir/API_code
rm $APICftaDir/API_code/_config.py
rm $APICftaDir/API_code/__init__.py
if [ -d $APICftaDir/API_code/__pycache__ ]; then
    rm $APICftaDir/API_code/__pycache__
fi
sleep 1

cd $APIEmissDir/API_code
rm $APIEmissDir/API_code/_config.py
rm $APIEmissDir/API_code/__init__.py
if [ -d $APIEmissDir/API_code/__pycache__ ]; then
    rm $APIEmissDir/API_code/__pycache__
fi

cd $APIMetDir
rm $APIMetDir/_*_config.sh

cd $APIGeogDir
rm $APIGeogDir/_*_config.sh

cd $APISSTDir
rm $APISSTDir/_*_config.sh

cd $BckgProcDir
if [ -h $BckgProcDir/bckg_API ]; then
    unlink $BckgProcDir/bckg_API
fi

cd $CftaProcDir
if [ -h $CftaProcDir/cfta_API ]; then
    unlink $CftaProcDir/cfta_API
fi
if [ -d $CftaProcDir/__pycache__ ]; then
    rm $CftaProcDir/__pycache__
fi
sleep 1

cd $EmissProcDir
if [ -h $EmissProcDir/emiss_API ]; then
    unlink $EmissProcDir/emiss_API
fi
if [ -d $EmissProcDir/__pycache__ ]; then
    rm $EmissProcDir/__pycache__
fi
