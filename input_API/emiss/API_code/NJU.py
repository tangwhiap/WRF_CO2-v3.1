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

    DataDir = DataDir.strip().split(":")
    ds = xr.open_dataset(DataDir[0].strip() + "/NJU_2016_CO2_hourly.nc")
    wrf_weekday = Time.weekday()
    Time = Time.replace(year=2016) # new FFDAS is from 2015 
    time_first = dtm.datetime(2016,1,1,0,0)
    time_last = dtm.datetime(2016,12,31,23,0)
    nju_weekday = Time.weekday()
    dtday = wrf_weekday - nju_weekday
    if dtday > 3:
        dtday = dtday - 7
    elif dtday < -3:
        dtday = dtday + 7
    Time = Time + dtm.timedelta( days = dtday )
    if Time > time_last:
        Time = Time - dtm.timedelta( days = 7 )
    if Time < time_first:
        Time = Time + dtm.timedelta( days = 7 )

    nju_out = ds.sel(time = np.datetime64(Time))
    lon = nju_out["lon"].values
    lat = nju_out["lat"].values
    LON, LAT = np.meshgrid(lon, lat)
    emiss = nju_out["emiss"].values
    #set_trace()
    # convert MtCO2/cell/hour --> mol/km^2/hour
    dx_long = np.gradient(LON)[1] * np.cos(np.deg2rad(LAT)) * 111.320
    dy_long = np.gradient(LAT)[0] * 110.574
    area_div = np.absolute(dx_long * dy_long) 
    #total_hours = days_of_month[month - 1] * 24
    emiss = emiss / area_div
    mass_CO2 = 44.
    emiss = emiss * 1000000. * 1000000./ mass_CO2
    lonlist = LON.flatten()
    latlist = LAT.flatten()
    emisslist = emiss.flatten()
    valid_ind = np.where(~np.isnan(emisslist))

    return {"lon":lonlist[valid_ind], "lat":latlist[valid_ind], "value":emisslist[valid_ind]}

