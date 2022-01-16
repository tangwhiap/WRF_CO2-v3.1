#!/usr/bin/env python

import datetime as dtm
import netCDF4 as nc
import numpy as np
import xarray as xr
from pdb import set_trace
from ._utils import areaS

'''
Athors: Wenhan TANG - 03/2021
'''
UserDefined_interpolate = False
interpolate_method = "linear"

#days_of_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def interface(Time, DataDir, wrfdom, sector = None):

    if sector is None:
        sector = "total"
    else:
        assert sector in ["total", "agriculture", "industry", "power", "residential", "transportation"]

    DataDir = DataDir.strip().split(":")
    #ds = xr.open_dataset(DataDir[0].strip() + "/MEIC_2016_CO2_hourly.nc")
    ncf = nc.Dataset(DataDir[0].strip() + "/MEIC_2016_CO2_hourly.nc")
    wrf_weekday = Time.weekday()
    Time = Time.replace(year=2016) # new FFDAS is from 2015 
    time_first = dtm.datetime(2016,1,1,0,0)
    time_last = dtm.datetime(2016,12,31,23,0)
    meic_weekday = Time.weekday()
    dtday = wrf_weekday - meic_weekday
    if dtday > 3:
        dtday = dtday - 7
    elif dtday < -3:
        dtday = dtday + 7
    Time = Time + dtm.timedelta( days = dtday )
    if Time > time_last:
        Time = Time - dtm.timedelta( days = 7 )
    if Time < time_first:
        Time = Time + dtm.timedelta( days = 7 )

    ncf_time = ncf.variables["time"][:].filled(np.nan)
    tunit = ncf.variables["time"].units
    tcalendar = ncf.variables["time"].calendar
    tnum = nc.date2num(Time, units = tunit, calendar = tcalendar)
    tindex = int(np.where(ncf_time == tnum)[0])

    #meic_out = ds.sel(time = np.datetime64(Time))
    #lon = meic_out["lon"].values
    #lat = meic_out["lat"].values
    lon = ncf.variables["lon"][:].filled(np.nan)
    lat = ncf.variables["lat"][:].filled(np.nan)
    LON, LAT = np.meshgrid(lon, lat)
    
    emiss = ncf.variables[sector][tindex, :, :].filled(np.nan)
    #print("V3.1: ", np.nanmean(emiss))
    #set_trace()
    # convert tCO2/cell/hour --> mol/km^2/hour
    #dx_long = np.gradient(LON)[1] * np.cos(np.deg2rad(LAT)) * 111.320
    #dy_long = np.gradient(LAT)[0] * 110.574
    #area_div = np.absolute(dx_long * dy_long) 
    area_div = areaS(LON, LAT)
    #total_hours = days_of_month[month - 1] * 24
    emiss = emiss / area_div
    mass_CO2 = 44.
    emiss = emiss * 1000000. / mass_CO2
    lonlist = LON.flatten()
    latlist = LAT.flatten()
    emisslist = emiss.flatten()
    valid_ind = np.where(~np.isnan(emisslist))
    #print("V3.1: ", emisslist[valid_ind].mean())
    return {"lon":lonlist[valid_ind], "lat":latlist[valid_ind], "value":emisslist[valid_ind]}

