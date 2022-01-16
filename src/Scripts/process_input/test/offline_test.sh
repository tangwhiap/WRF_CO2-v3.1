#!/bin/bash

Me=$( readlink -m $( type -p $0 ))
MYDIR=`dirname $Me`

CASENAME=SEC_DJF2019
inputType=FFE
PROCDIR=$MYDIR/..
GEODIR=$MYDIR/work
OUTDIR=$MYDIR/output

Start="2019-01-01_00:00:00"
End="2019-01-02_00:00:00"
nCores=20

$PROCDIR/make_tracers_input.py $CASENAME $inputType --runtype offline --start $Start --end $End --geodir $GEODIR --output $OUTDIR --core $nCores
