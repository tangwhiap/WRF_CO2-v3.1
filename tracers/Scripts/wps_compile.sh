#!/bin/bash
# Authors:
#     Wenhan TANG - 05/2021
#     ...
source ../.model_def_dir.sh
cd $WPSDir

FCID=1 # Linux x86_64, gfortran    (serial)

# Clean the WPS.
./clean -a

echo -e "${FCID}\n" | ./configure

# Modify configure.wps
# Add option: "-lgomp" for ${FC}
sed -i "/SFC                 = gfortran/cSFC                 = gfortran -lgomp" configure.wps

# Compile wps
./compile #&> wps_compile.log

