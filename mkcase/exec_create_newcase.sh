#!/bin/bash
# Top-level script of MAKE CASE module for users.
# Authors:
#   Wenhan Tang - 12/2020
#   ...

# Name of case, for example:
# CASENAME=test1
CASENAME=SEC_DJF2019

# Running type, choose one from "normal" and "cronjob"
RUNTYPE=cronjob

# Restart option, "true" for restart run, while "false" for initial run.
RESTART=false

# User's specific directory for this case. Null for default case directory ($ROOTDIR/cases)
#SPECDIR=
SPECDIR=/home/tangwh/modeldata/WRFCO2_cases

./create_newcase.sh $CASENAME $RUNTYPE $RESTART $SPECDIR
