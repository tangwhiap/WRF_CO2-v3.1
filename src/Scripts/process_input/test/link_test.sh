#!/bin/bash

Me=$( readlink -m $( type -p $0 ))
MYDIR=`dirname $Me`

CASENAME=t4
inputType=FFE
PROCDIR=$MYDIR/..
WORKDIR=$MYDIR/work
ORIGDIR=$MYDIR/output

$PROCDIR/make_tracers_input.py $CASENAME $inputType --rundir $WORKDIR --link true --origdir $ORIGDIR
