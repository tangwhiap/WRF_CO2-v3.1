import datetime as dtm
import numpy as np
import xarray as xr
from pdb import set_trace

UserDefined_interpolate = False
interpolate_method = "linear"

days_of_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def interface(Time,DataDir,wrfdom):

    DataDir = DataDir.strip().split(":")
    ds = xr.open_dataset(DataDir[0].strip() + "/MEIC_2016_CO2.nc")
    month = Time.month
    meic_out = ds.isel(time = month - 1)
    lon = meic_out["lon"].values
    lat = meic_out["lat"].values
    LON, LAT = np.meshgrid(lon, lat)
    emiss = meic_out["total"].values
    #set_trace()
    # convert tCO2/cell/hour --> mol/km^2/hour
    dx_long = np.gradient(LON)[1] * np.cos(np.deg2rad(LAT)) * 111.320
    dy_long = np.gradient(LAT)[0] * 110.574
    area_div = np.absolute(dx_long * dy_long) 
    total_hours = days_of_month[month - 1] * 24
    emiss = emiss / area_div / total_hours
    mass_CO2 = 44.
    emiss = emiss * 1000000. / mass_CO2
    lonlist = LON.flatten()
    latlist = LAT.flatten()
    emisslist = emiss.flatten()
    valid_ind = np.where(~np.isnan(emisslist))

    return {"lon":lonlist[valid_ind], "lat":latlist[valid_ind], "value":emisslist[valid_ind]}

