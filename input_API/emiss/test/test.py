#!/usr/bin/env python
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import datetime as dtm
from scipy import interpolate
from API_code import *
from pdb import set_trace

#emiss = "FFDAS"
emiss = "NDRC"
#emiss = "MEIC"
#emiss = "ODIAC"
#emiss = "REGION"
#emiss = "NJU"
#emiss = "PKU"
#emiss = "EDGAR"
#kwargs = {"region": "BJ"}
kwargs = {"sector": "indusp"}

strTime = "2019-07-01_00:00:00"
time = dtm.datetime.strptime(strTime, "%Y-%m-%d_%H:%M:%S")
lat_s = 35
lat_n = 43
lon_w = 110
lon_e = 121
nx = 200
ny = 200
dLon = (lon_e - lon_w) / nx
dLat = (lat_n - lat_s) / ny

wrflon_list = np.linspace(lon_w, lon_e, nx)
wrflat_list = np.linspace(lat_s, lat_n, ny)
wrflon, wrflat = np.meshgrid(wrflon_list, wrflat_list)
wrfdom = {}
wrfdom['lonwrf'] = wrflon
wrfdom['latwrf'] = wrflat
wrfdom['lat_s'] = lat_s
wrfdom['lat_n'] = lat_n
wrfdom['lon_w'] = lon_w
wrfdom['lon_e'] = lon_e
wrfdom["dLon"] = dLon
wrfdom["dLat"] = dLat

loc = locals()
exec("spec_int = " + emiss + ".UserDefined_interpolate")
spec_int = loc["spec_int"]

if spec_int:
    exec("iemissFlux = " + emiss + ".interface(time, _config." + emiss + "_Dir, wrfdom, **kwargs)") 
    iemissFlux = loc["iemissFlux"]
else:
    exec("int_method = " + emiss + ".interpolate_method")
    int_method = loc["int_method"]
    assert int_method in ["linear", "nearest", "cubic"],"" 
    exec("iemissFlux_dic = " + emiss + ".interface(time, _config." + emiss + "_Dir, wrfdom, **kwargs)")
    iemissFlux_dic=loc["iemissFlux_dic"]
    flon = iemissFlux_dic["lon"]
    flat = iemissFlux_dic["lat"]
    fiemissValue = iemissFlux_dic["value"]
    iemissFlux = interpolate.griddata((flon.flatten(),flat.flatten()),fiemissValue.flatten(),(wrfdom['lonwrf'],wrfdom['latwrf']),method = int_method)
ds = xr.Dataset({"emiss": (["lat", "lon"], iemissFlux)}, coords = {"lon": (["lon"],wrflon_list), "lat": (["lat"], wrflat_list)})
emiss_mean = ds["emiss"].mean().values
np.log10(ds.emiss).plot()
#ds.emiss.plot()
print(emiss + " emiss_mean =  ", float(emiss_mean))
plt.show()


