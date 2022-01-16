#!/bin/bash
# Authors:
#  Wenhan Tang - 12/2020 (Original Version)
#  ...

source ./config/configure.sh
source ./config/wps_input.sh

# Special setting for namelist.input, defined by users.
# Prepared for some special requests of options on namelist.input, in some special conditions.
# For example, if the meteorology data is NARR, the variable "p_top_requested" in namelist.input should be set to more than 10000, you can add:

if [[ $Met == "NARR" ]]; then
    echo "Meteorology data is NARR, set p_top_requested = 10000"
    $NGSDir/NLO "mod &: p_top_requested = 10000 | $CASEWORK/nml/nml-wrf"
fi

# So, if you find other special requests like that, write here below:
