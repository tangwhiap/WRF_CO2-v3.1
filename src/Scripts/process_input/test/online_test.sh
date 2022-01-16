#!/bin/bash

Me=$( readlink -m $( type -p $0 ))
MYDIR=`dirname $Me`

CASENAME=test_bckg
inputType=FTA
PROCDIR=$MYDIR/..
WORKDIR=$MYDIR/work

$PROCDIR/make_tracers_input.py $CASENAME $inputType --rundir $WORKDIR --core 10
