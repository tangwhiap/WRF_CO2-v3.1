#!/bin/bash
# Authors:
#    Wenhan TANG - 02/2021
#    ...
Me=$( readlink -m $( type -p $0 ))
MYDIR=`dirname $Me`
cd $MYDIR

source .model_def_dir.sh
source $Trashrc $ROOTDIR
unlink_fun()
{
    link_name=$@
    for ilink in $@
    do
        if [ -h $ilink ]; then
            unlink $ilink
        fi
    done
    
}

unlink_fun $ROOTDIR/.model_def_dir.sh $MKCASEDIR/.model_def_dir.sh $APIRegDir/.model_def_dir.sh $MKCASEDIR/.model_env_set.sh $UtilsDir/.model_env_set.sh

rm $MYDIR/.model_def_dir.sh
rm $MYDIR/.model_env_set.sh
