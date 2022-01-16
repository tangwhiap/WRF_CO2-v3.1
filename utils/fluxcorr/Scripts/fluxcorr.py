#!/usr/bin/env python

import netCDF4 as nc
import xarray as xr
import numpy as np
import os
import sys
import datetime as dtm

str_StartDT = "2019-01-01_01:00:00"
str_EndDT = "2019-02-01_00:00:00"
dtMin = 15
DataDir = "/home/tangwh/modeling/WRF-CO2-cases/exp_data/exp6/output/wrfco2"
OutDir = "../output"
InPrefix = "wrfco2"
DomName = "d01"
StaDir = "/home/tangwh/wrf-latlon/plane/output"
StaPrefix = "wrfsta_exp6"
StaSuffix = "744Hrs.nc"
StaTime = "2019-01-01_00:00:00"
N_layers = 10
ResearchVar = "CO2_FFE"
OutName = "corr96_co2_ffe_jan2019_1mo.nc"
TimeLag = 96

Start = dtm.datetime.strptime(str_StartDT, "%Y-%m-%d_%H:%M:%S")
End = dtm.datetime.strptime(str_EndDT, "%Y-%m-%d_%H:%M:%S")
dt = dtm.timedelta(minutes = dtMin)
InletList = [
    "XiangHe_h1",
    "XiangHe_h2",
    "IAPtower_h1",
    "IAPtower_h2",
    "XingLong_h1",
    "XingLong_h2",
    "ShangDianZi_h1",
    "ShangDianZi_h2",
    "TJtower_h1",
    "TJtower_h2",
    "LuanCheng_h1",
    "LuanCheng_h2"
]
StationDic = {}
for inlet in InletList:
    station = inlet.split("_")[0]
    if station in StationDic:
        StationDic[station].append(inlet)
    else:
        StationDic[station] = [inlet]

ds_StaFile_dic = {}
## for example:
## "XiangHe": ["XiangHe_h1", "XiangHe_h2"]
for station in StationDic:
    StaFile = StaPrefix + "_" + DomName + "_" + station + "_" + StaTime + "_" + StaSuffix
    ds_StaFile_dic[station] = xr.open_dataset(StaDir + "/" + StaFile)

station_co2_dic = {}
for inlet in InletList:
    station_co2_dic[inlet] = {}

def get_real_time_data(Current, ds_StaFile_dic, TimeLag):
    global StationDic, N_layers, InPrefix, DomName, DataDir
    str_Current = Current.strftime("%Y-%m-%d_%H:%M:%S")
    str_Current_Lag = (Current - dt * TimeLag).strftime("%Y-%m-%d_%H:%M:%S")
    #print("Current: ", str_Current)
    #print("Current Lag: ", str_Current_Lag)
    InFile = InPrefix + "_" + DomName + "_" + str_Current_Lag
    ds_InFile = nc.Dataset(DataDir + "/" + InFile)
    co2_inobs = {}
    for station in StationDic:
        ds = ds_StaFile_dic[station]
        for inlet in StationDic[station]:
            #print(ds["CO2_TOT_inobs"].sel(time = Current, observatory = inlet.encode("UTF-8")).values)
            co2_sta = float( ds[ResearchVar + "_inobs"].sel(time = Current, observatory = inlet.encode("UTF-8")).values )
            co2_inobs[inlet] = co2_sta
    WRFdata = ds_InFile.variables[ResearchVar][0,:N_layers,:,:].filled(np.nan)
    return co2_inobs, WRFdata



SampleInFile = xr.open_dataset(DataDir + "/" + InPrefix + "_" + DomName + "_" + str_StartDT)
lon = SampleInFile.XLONG[0,0].values
lat = SampleInFile.XLAT[0,:,0].values
layer = np.arange(N_layers)
nx = len(lon)
ny = len(lat)
nz = N_layers

# Loop 1: compute average of WRF domain array and WRF inobs data
WRFdataAVE = np.full((nz, ny, nx), 0)
WRFdataNUM = np.full((nz, ny, nx), 0)
InobsAVE = {}
InobsNUM = {}
for inlet in InletList:
    InobsAVE[inlet] = 0
    InobsNUM[inlet] = 0

iTime = 1
Current = Start
while(Current <= End):
    print("Loop 1: Current time: ", Current) 
    if iTime <= TimeLag:
        print("Loop 1: TimeLag = ", TimeLag, "iTime = ", iTime, ", PASS ...")
        Current = Current + dt
        iTime = iTime + 1
        continue
    co2_inobs, WRFdata = get_real_time_data(Current, ds_StaFile_dic, TimeLag)
    masked_domain = ~np.isnan(WRFdata)
    WRFdataAVE = WRFdataAVE + np.where(masked_domain, WRFdata, 0)
    WRFdataNUM = WRFdataNUM + np.where(masked_domain, 1, 0)
    for inlet in InletList:
        if not(np.isnan(co2_inobs[inlet])):
            InobsAVE[inlet] = InobsAVE[inlet] + co2_inobs[inlet]
            InobsNUM[inlet] = InobsNUM[inlet] + 1

    Current = Current + dt
    iTime = iTime + 1

WRFdataAVE = WRFdataAVE / WRFdataNUM
WRFdataAVE = np.where(np.isinf(WRFdataAVE), np.nan, WRFdataAVE)
for inlet in InletList:
    if InobsNUM[inlet] == 0:
        InobsAVE[inlet] = np.nan
    else:
        InobsAVE[inlet] = InobsAVE[inlet] / InobsNUM[inlet]

#print(WRFdataAVE)
#print(InobsAVE)
#print(WRFdataNUM)
#print(InobsNUM)

# Loop2: compute secA, secB, secC for the calculation of correlation.
# secA: sum( (xi - x_) * (yi - y_) )
# secB: sum( (xi - x_) ** 2 )
# secC: sum( (yi - y_) ** 2 )
# corr = secA / (sqrt( secB * secC ))

secA_SUM_dic = {}
secB_SUM_dic = {}
secC_SUM_dic = {}

for inlet in InletList:
    secA_SUM_dic[inlet] = np.full((nz, ny, nx), 0)
    secB_SUM_dic[inlet] = np.full((nz, ny, nx), 0)
    secC_SUM_dic[inlet] = np.full((nz, ny, nx), 0)

iTime = 1
Current = Start
while(Current <= End):
    print("Loop 2: Current time: ", Current) 
    if iTime <= TimeLag:
        print("Loop 2: TimeLag = ", TimeLag, "iTime = ", iTime, ", PASS ...")
        Current = Current + dt
        iTime = iTime + 1
        continue
    
    co2_inobs, WRFdata = get_real_time_data(Current, ds_StaFile_dic, TimeLag)
    for inlet in InletList:
        if np.isnan(co2_inobs[inlet]):
            continue
        secA = (WRFdata - WRFdataAVE) * (co2_inobs[inlet] - InobsAVE[inlet])
        secB = (WRFdata - WRFdataAVE) ** 2
        secC = (co2_inobs[inlet] - InobsAVE[inlet]) ** 2
        masked_domain = ~np.isnan(secA)
        secA = np.where(masked_domain, secA, 0)
        secB = np.where(masked_domain, secB, 0)
        secC = np.full((nz, ny, nx), secC)
        secC = np.where(masked_domain, secC, 0)
        secA_SUM_dic[inlet] = secA_SUM_dic[inlet] + secA
        secB_SUM_dic[inlet] = secB_SUM_dic[inlet] + secB
        secC_SUM_dic[inlet] = secC_SUM_dic[inlet] + secC
    Current = Current + dt
    iTime = iTime + 1

corr_dic = {}
for inlet in InletList:
    secA = secA_SUM_dic[inlet]
    secB = secB_SUM_dic[inlet]
    secC = secC_SUM_dic[inlet]
    corr = secA / np.sqrt( secB * secC )
    corr_dic[inlet] = corr.copy()

dsout = xr.Dataset()
for inlet in InletList:
    #dsout["Corr_" + inlet] = ( ("z", "lat", "lon"), corr_dic[inlet] )
    dsout[inlet] = ( ("z", "lat", "lon"), corr_dic[inlet] )
dsout.coords["z"] = ( ("z"), layer )
dsout.coords["lat"] = ( ("lat"), lat )
dsout.coords["lon"] = ( ("lon"), lon )
dsout["lon"].attrs["axis"] = "X"
dsout["lon"].attrs["units"] = "degrees_east"
dsout["lat"].attrs["axis"] = "Y"
dsout["lat"].attrs["units"] = "degrees_north"
dsout["z"].attrs["axis"] = "Z"
dsout.to_netcdf(OutDir + "/" + OutName)
#dsout.to_netcdf("test.nc")

