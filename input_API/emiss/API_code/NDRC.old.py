import datetime as dtm
import numpy as np
import xarray as xr
from pdb import set_trace

UserDefined_interpolate = False
interpolate_method = "linear"

def interface(Time,DataDir,wrfdom):

    DataDir = DataDir.strip().split(":")
    wrf_weekday = Time.weekday()
    ndrc_time = Time.replace(year=2016) # NDRC data in 2016    
    ndrc_weekday = ndrc_time.weekday()
    daydt = wrf_weekday - ndrc_weekday
    if daydt > 3:
       daydt = daydt - 7
    elif daydt < -3:
       daydt = daydt + 7
    ndrc_time = ndrc_time + dtm.timedelta(days=daydt)
    ds = xr.open_dataset(DataDir[0].strip() + "/NDRC_total_hourly.nc")
    ndrc_out = ds.sel(time = ndrc_time)
    lon = ndrc_out["lon"].values
    lat = ndrc_out["lat"].values
    LON, LAT = np.meshgrid(lon, lat)
    emiss = ndrc_out["emiss"].values
    #set_trace()
	# convert tCO2/cell/hour --> mol/km^2/hour
    dx_long = np.gradient(LON)[1] * np.cos(np.deg2rad(LAT)) * 111.320
    dy_long = np.gradient(LAT)[0] * 110.574
    area_div = np.absolute(dx_long * dy_long) 
    emiss = emiss / area_div
    mass_CO2 = 44.
    emiss = emiss * 1000000. / mass_CO2

    return {"lon":LON.flatten(), "lat":LAT.flatten(), "value":emiss.flatten()}

