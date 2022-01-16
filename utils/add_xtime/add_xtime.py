#!/usr/bin/env python
# Authors:
#   Wenhan TANG - 12/2020
#   ...

import xarray as xr
import datetime as dtm
import glob
import sys

InputDir = sys.argv[1]
OutputDir = sys.argv[2]
StartDate = sys.argv[3]
StartTime = sys.argv[4]
input_prefix = "wrfco2"

print("InputDir:", InputDir)
print("OutputDir:", OutputDir)
print("StartDate:", StartDate)
print("StartTime:", StartTime)

def add_xtime(InputDirName, OutputDirName):
    global StartDate, StartTime
    print("Processing " + InputDirName + " ...")
    ds = xr.open_dataset(InputDirName, decode_times = False)
    Name = InputDirName.strip().split("/")[-1]
    #str_date = Name.split("_")[2]
    #str_time = Name.split("_")[3]
    str_datetime = StartDate + " " + StartTime
    ds["XTIME"].attrs["description"] = "minutes since " + str_datetime
    ds["XTIME"].attrs["units"] = "minutes since " + str_datetime
    print("Writing " + OutputDirName + " ...")
    ds.to_netcdf(OutputDirName)

if __name__ == "__main__":
    FileList = glob.glob(InputDir + "/" + input_prefix + "*")
    print("FileList:", FileList)
    for InputDirName in FileList:
        Name = InputDirName.strip().split("/")[-1]
        OutputDirName = OutputDir + "/" + Name
        add_xtime(InputDirName, OutputDirName)

