#!/bin/bash
# Make .tar.gz file for WRF-CO2 modeling package
# Authors:
#     Wenhan TANG - 04/2021
#     ...

# To make sure the current directory is the ROOTDIR of model
Me=$( readlink -m $( type -p $0 ))
MyDir=`dirname $Me`
RootDir=$MyDir
cd $MyDir

#TarDir=$MyDir/..
TarDir=/home/tangwh/packages
Prefix=WRF-CO2-v3.1
Author=TWH
Tnow=`date +%Y-%m-%d_%H-%M`
Suffix=TAR.gz

TarName=${Prefix}.${Author}.${Tnow}.${Suffix}

if [ -d $MyDir/.trash ]; then
    mkdir $MyDir/.remove
    mv $MyDir/.trash/* $MyDir/.remove
    mkdir $MyDir/.trash
    /bin/rm -fr $MyDir/.remove
fi

cd $TarDir

tar -zcvf $TarDir/$TarName $RootDir/



