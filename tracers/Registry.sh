#!/bin/bash



BUILD=true

CLEANALL=true

COMPILEWPS=true


Me=$( readlink -m $( type -p $0 ))
MYDIR=`dirname $Me`
cd $MYDIR

./mksrc.sh

if [[ $BUILD == "true" ]];then
    nohup ./build.sh $CLEANALL $COMPILEWPS &> build.log &
fi
