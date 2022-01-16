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
year_data = 2015
def interface(Time,DataDir,wrfdom):

    DataDir = DataDir.strip().split(":")
    ds = xr.open_dataset(DataDir[0].strip() + "/FFDAS_China_" + str(year_data) + "_CO2_hourly.nc")
    wrf_weekday = Time.weekday()
    try:
        Time = Time.replace(year=year_data) # new FFDAS is from 2015 
    except ValueError: # if Time is on 2/29
        Time.replace(year=year_data,month=3,day=1)  

    time_first = dtm.datetime(year_data,1,1,0,0)
    time_last = dtm.datetime(year_data,12,31,23,0)
    edgar_weekday = Time.weekday()
    dtday = wrf_weekday - edgar_weekday
    if dtday > 3:
        dtday = dtday - 7
    elif dtday < -3:
        dtday = dtday + 7
    Time = Time + dtm.timedelta( days = dtday )
    if Time > time_last:
        Time = Time - dtm.timedelta( days = 7 )
    if Time < time_first:
        Time = Time + dtm.timedelta( days = 7 )

    edgar_out = ds.sel(time = np.datetime64(Time))
    lon = edgar_out["lon"].values
    lat = edgar_out["lat"].values
    LON, LAT = np.meshgrid(lon, lat)
    emiss = edgar_out["emiss"].values
    #set_trace()
    # convert KgC/m^2/hour --> mol/km^2/hour
    mass_C = 12.
    emiss = emiss * 1000. * 1000000./ mass_C
    lonlist = LON.flatten()
    latlist = LAT.flatten()
    emisslist = emiss.flatten()
    valid_ind = np.where(~np.isnan(emisslist))

    return {"lon":lonlist[valid_ind], "lat":latlist[valid_ind], "value":emisslist[valid_ind]}

