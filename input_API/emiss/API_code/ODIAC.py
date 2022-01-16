import datetime as dtm
import numpy as np
import xarray as xr
from pdb import set_trace
'''
Athors: Wenhan TANG - 03/2021
'''
UserDefined_interpolate = False
interpolate_method = "linear"

days_of_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def interface(Time,DataDir,wrfdom):

    DataDir = DataDir.strip().split(":")
    year = Time.year
    ds = xr.open_dataset(DataDir[0].strip() + "/ODIAC_" + str(year) + ".nc")
    #month = Time.month
    #meic_out = ds.isel(time = month - 1)
    lat_s = wrfdom["lat_s"] - 1
    lat_e = wrfdom["lat_n"] + 1
    lon_s = wrfdom["lon_w"] - 1
    lon_e = wrfdom["lon_e"] + 1
    olon = ds.lon.values
    olat = ds.lat.values
    lon_range = olon[ ( olon >= lon_s ) & ( olon <= lon_e ) ]
    lat_range = olat[ ( olat >= lat_s ) & ( olat <= lat_e ) ]
    odiac_out = ds.sel(time = np.datetime64(dtm.datetime(Time.year, Time.month, Time.day, Time.hour)))
    odiac_out = odiac_out.sel( lon = lon_range ).sel( lat = lat_range )
    lon = odiac_out["lon"].values
    lat = odiac_out["lat"].values
    LON, LAT = np.meshgrid(lon, lat)
    emiss = odiac_out["ffe"].values
    #set_trace()
    # convert kgC/m2/s --> mol/km^2/hour
    #dx_long = np.gradient(LON)[1] * np.cos(np.deg2rad(LAT)) * 111.320
    #dy_long = np.gradient(LAT)[0] * 110.574
    #area_div = np.absolute(dx_long * dy_long) 
    #total_hours = days_of_month[month - 1] * 24
    #emiss = emiss / area_div / total_hours
    mass_C = 12.
    emiss = emiss * 1000. / mass_C * 1000000 * 3600
    lonlist = LON.flatten()
    latlist = LAT.flatten()
    emisslist = emiss.flatten()
    valid_ind = np.where(~np.isnan(emisslist))

    return {"lon":lonlist[valid_ind], "lat":latlist[valid_ind], "value":emisslist[valid_ind]}

