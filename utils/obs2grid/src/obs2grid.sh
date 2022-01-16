#!/bin/bash
# The top-level script of the OBS2GRID system.
# Used to convert the SENSE data to binary grid data, with the time and spatial dimensions as same as wrfout data with specific domain.

# Authors:
#  TangWenhan 09/2020 (Original version)
#  TangWenhan 09/2020 (Add the hourly, daily, monthly averaging function)
#  ...

# Main Steps:
# 1. Set start and end datetime, domain and time interval of WRF etc.
# 2. Source defdir.sh to load the internal directory.
# 3. Call the GetSense.py to load the data from SENSE dataset, and write it to station.dat in $PDir/temp.
# 4. Call the nml_make.py to make "namelist.o2g" for fortran program，refering to the wrfout ctl file with specific domain
# 5. Compile the fortran code (*.f90), if the executable file o2g.exe is not exit.
# 6. Run the o2g.exe to do the main work of OBS2GRID.

# Previous preparations:
# 1. Link the SENSE data directory to $PDir/data/SENSE
# 2. Link the wrfout ctl directory to $PDir/data/WRF
# 3. Write or check the stations_info.txt $PDir/data/station_info
# 4. If the fortran source code have been modified, or you want to return the whole system to initial state, it's better to ./all-init.sh

# Step1: Set start and end datetime, domain and time interval of WRF etc.
#########################

start="2020-01-01_00:00:00" # Start datetime "YYYY-MM-DD_hh:mm:ss"

end="2020-02-01_00:00:00"   # End datetime "YYYY-MM-DD_hh:mm:ss"

dom=1                       # WRF domain num, select from 1/2/3

dtMin=30                    # Time interval in minute, better to be consist with it of wrfout. 
                            # i.e. dom=1 => dtMin=30; dom=2 => dtMin=15; dom=3 => dtMin=15

ifWriteNum=False            # If it is True, the number of data averaged in each grid point will be write.

OutputSplit=False           # If it is True, the output will consist of multiple files, one file contains data in same time, 
                            # which is shown in name of the file.

hourly=True                 # If it is True, the hourly averaged data will be caculated and writed in a separate file.

daily=True                  # If it is True, the daily averaged data will be caculated and writed in a separate file.

monthly=True                # If it is True, the monthly averaged data will be caculated and writed in a separate file.

#########################

# Step 2: Source defdir.sh to load the internal directory.
source ./defdir.sh

# Step 3: Call the GetSense.py to load the data from SENSE dataset, and write it to station.dat in $PDir/temp.
python GetSense.py $start $end $dtMin $WRFDir $SENSEDir $InfoDir $TempDir

# Step 4: Call the nml_make.py to make namelist.o2g for fortran program，refering to the wrfout ctl file with specific domain
python nml_make.py $WRFDir $DataDir $TempDir $OutDir $ifWriteNum $dtMin $dom $OutputSplit $hourly $daily $monthly

# Step 5: Compile the fortran code (*.f90), if the executable file o2g.exe is not exit.
if [ ! -f "o2g.exe" ]; then
    ./compile
fi

# Step 6: Run the o2g.exe to do the main work of OBS2GRID.
./o2g.exe

