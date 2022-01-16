#!/bin/bash
Me=$( readlink -m $( type -p $0 ))
MyDir=`dirname $Me`
cd $MyDir

if [ ! -f .model_def_dir.sh ]; then
    echo "Please execute \$ROOTDIR/ini/init.sh first"
    exit
fi
source .model_def_dir.sh
source $Trashrc $ROOTDIR

cd $MKCASEDIR
if [ -f $MKCASEDIR/.mkcase.err ]; then
    rm $MKCASEDIR/.mkcase.err
fi

if [ -f $MKCASEDIR/tools/.mkcase.err ]; then
    rm $MKCASEDIR/tools/.mkcase.err
fi

rm $MKCASEDIR/.case_*_created_successfully 2> /dev/null

#if [ -f $MKCASEDIR/.case_*_created_successfully ]; then
#    rm $MKCASEDIR/.case_*_created_successfully
#fi

if [ -d $MKCASEDIR/tools/.get_maxdom ]; then
    rm $MKCASEDIR/tools/.get_maxdom
fi
