#!/bin/bash

# Authors:
#   Wenhan TANG - 08/2021
#   ...

Me=$( readlink -m $( type -p $0 ))
MYDIR=`dirname $Me`
cd $MYDIR

source .model_def_dir.sh

#CLEANALL=false


FileType=registry_chem 
OutDir=$WRFRegDir
$TracersSrc/mksrc.py $TracersDir $TracersSrcDemo $OutDir $FileType

FileType=module_ghg_fluxes
OutDir=$WRFchemDir
$TracersSrc/mksrc.py $TracersDir $TracersSrcDemo $OutDir $FileType

FileType=var_output
OutDir=$MKCASEDCDIR
$TracersSrc/mksrc.py $TracersDir $TracersSrcDemo $OutDir $FileType

FileType=input_dft
OutDir=$MKCASEDCDIR
$TracersSrc/mksrc.py $TracersDir $TracersSrcDemo $OutDir $FileType


