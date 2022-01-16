#!/bin/bash
Me=$( readlink -m $( type -p $0 ))
MyDir=`dirname $Me`
linksList=`ls ${MyDir}/tracers_input*.py 2> /dev/null`

for link in $linksList;
do
    echo "unlink $link"
    unlink $link
done

