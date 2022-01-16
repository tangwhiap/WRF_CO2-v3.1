import datetime as dtm
import numpy as np
import xarray as xr
from pdb import set_trace
'''
Athors: Wenhan TANG - 04/2021
'''
UserDefined_interpolate = False
interpolate_method = "linear"

#days_of_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def interface(Time,DataDir,wrfdom):
    year = 2014
    DataDir = DataDir.strip().split(":")
    ds = xr.open_dataset(DataDir[0].strip() + "/PKU_China_" + str(year) + "_CO2_hourly.nc")
    wrf_weekday = Time.weekday()
    try:
        Time = Time.replace(year=year) # new FFDAS is from 2015 
    except ValueError: # if Time is on 2/29
        Time.replace(year=year,month=3,day=1)  

    time_first = dtm.datetime(year,1,1,0,0)
    time_last = dtm.datetime(year,12,31,23,0)
    pku_weekday = Time.weekday()
    dtday = wrf_weekday - pku_weekday
    if dtday > 3:
        dtday = dtday - 7
    elif dtday < -3:
        dtday = dtday + 7
    Time = Time + dtm.timedelta( days = dtday )
    if Time > time_last:
        Time = Time - dtm.timedelta( days = 7 )
    if Time < time_first:
        Time = Time + dtm.timedelta( days = 7 )

    pku_out = ds.sel(time = np.datetime64(Time))
    lon = pku_out["lon"].values
    lat = pku_out["lat"].values
    LON, LAT = np.meshgrid(lon, lat)
    emiss = pku_out["emiss"].values
    #set_trace()
    # convert gCO2/km^2/hour --> mol/km^2/hour
    mass_CO2 = 44.
    emiss = emiss / mass_CO2
    lonlist = LON.flatten()
    latlist = LAT.flatten()
    emisslist = emiss.flatten()
    valid_ind = np.where(~np.isnan(emisslist))

    return {"lon":lonlist[valid_ind], "lat":latlist[valid_ind], "value":emisslist[valid_ind]}

