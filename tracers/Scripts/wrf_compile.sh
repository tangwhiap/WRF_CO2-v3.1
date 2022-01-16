#!/bin/bash
# Authors:
#  Wenhan TANG - 01/2021 - Original version
#  Wenhan TANG - 08/2021 - Modified for tracers registry
#  ...

source ../.model_def_dir.sh
cd $WRFDir

CLEANALL=$1

FCID=35 # GNU (gfortran/gcc) (dm+sm)
NEST=1 # basic
NTASK=8

# clean the WRF-chem model.
if [[ $CLEANALL == "true" ]]; then
    ./clean -a
fi

# configure.
echo -e "${FCID}\n${NEST}\n" | ./configure

# Parallel compiling.
./compile -j $NTASK em_real #&> $TracersSrc/wrf_compile.log1

# Run compile script again without parallel compiling option to solve the problems in compiling the real.exe.
./compile em_real #&> $TracersSrc/wrf_compile.log2
