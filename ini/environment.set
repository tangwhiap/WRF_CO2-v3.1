#!/bin/bash
# Set environment to run WRF-CO2
# Only works on iark.cc, by loading the environment set on /home/tangwh.
# If you are running on another computer, you must install and configure the required environment


#export PATH=/opt/modules/Ferret/Ferret-7.5.0-RHEL7-64/bin:/opt/modules/opengrads:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin

# Reset $PATH and LI_LIBRARY_PATH
export PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
export LD_LIBRARY_PATH=

# Loading basic setting
source /etc/bashrc



export DIR=/home/tangwh/Library/Build_WRF/LIBRARIES


#====== for netcdf =======
export NETCDF=$DIR/netcdf
export PATH=$NETCDF/bin:$PATH
export LD_LIBRARY_PATH=${NETCDF}/lib

#====== for Jasperlib =======

 export JASPERLIB=$DIR/grib2/lib 
 export JASPERINC=$DIR/grib2/include
 export LDFLAGS=-L$DIR/grib2/lib
 export CPPFLAGS=-I$DIR/grib2/include
 export LD_LIBRARY_PATH=${JASPERLIB}:${LD_LIBRARY_PATH}

#======for mpich===========
 export PATH=$DIR/mpich/bin:$PATH

#======= openmp =========
export OMP_NUM_THREADS=1
export OMP_STACKSIZE=500000000

#======== for WRF =========
  export WRFIO_NCD_LARGE_FILE_SUPPORT=1
  export WRF_CHEM=1
  export EM_CORE=1
  export MPI_LIB=
  ulimit -s unlimited

#=========== anaconda3 =============
# added by Anaconda3 5.3.0 installer
# >>> conda init >>>
# !! Contents within this block are managed by 'conda init' !!
#__conda_setup="$('/home/tangwh/software/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
#if [ $? -eq 0 ]; then
#    eval "$__conda_setup"
#else
#    if [ -f "/home/tangwh/software/anaconda3/etc/profile.d/conda.sh" ]; then
#        . "/home/tangwh/software/anaconda3/etc/profile.d/conda.sh"
#    else
#        export PATH="/home/tangwh/software/anaconda3/bin:$PATH"
#    fi
##fi
#unset __conda_setup
# <<< conda initialize <<<
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!

__conda_setup="$('/mnt/gugong/tangwh/software/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/mnt/gugong/tangwh/software/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/mnt/gugong/tangwh/software/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/mnt/gugong/tangwh/software/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

conda activate wrfco2
echo "set PATH=$PATH"
echo "set LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
