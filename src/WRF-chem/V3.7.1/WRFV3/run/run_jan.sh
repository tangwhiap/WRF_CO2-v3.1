#!/bin/bash

 #SBATCH -N 2
 #SBATCH -t 2:00:00
 #SBATCH --mail-user=showe@umd.edu
 #SBATCH --mail-type=BEGIN
 #SBATCH --mail-type=END
 module load netcdf-fortran/intel/2015.0.3.032/intelmpi-mt/netcdf/4.3.3.1/4.4.2
 module load netcdf-fortran/intel/2015.0.3.032/intelmpi-mt/netcdf/4.3.3.1/4.4.2
 module load ncview
 module load hdf5/intel/2015.0.3.032/intelmpi-mt/shared/1.8.15p1

 mpirun /lustre/showe/modeling/WRF/WRFV3/run/wrf.exe
