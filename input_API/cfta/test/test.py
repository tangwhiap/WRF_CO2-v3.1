#!/usr/bin/env python
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import datetime as dtm
from scipy import interpolate
from API_code import *
from pdb import set_trace

#cfta = "cfta_0p5x0p5_v2"
#cfta = "cfta_daily"
cfta = "cfta_1x1"
#cfta = "zero"

strTime = "2020-08-03_00:00:00"
time = dtm.datetime.strptime(strTime, "%Y-%m-%d_%H:%M:%S")
lat_s = 35
lat_n = 43
lon_w = 110
lon_e = 121
nx = 200
ny = 200

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
loc = locals()
exec("int_method = " + cfta + ".interpolate_method")
int_method = loc["int_method"]
assert int_method in ["linear", "nearest", "cubic"],"" 
exec("icftaFlux_dic = " + cfta + ".interface(time, _config." + cfta + "_Dir, wrfdom)")
icftaFlux_dic=loc["icftaFlux_dic"]
flon = icftaFlux_dic["lon"]
flat = icftaFlux_dic["lat"]
ficftaValue = icftaFlux_dic["value"]
icftaFlux = interpolate.griddata((flon.flatten(),flat.flatten()),ficftaValue.flatten(),(wrfdom['lonwrf'],wrfdom['latwrf']),method = int_method)
ds = xr.Dataset({"cfta": (["lat", "lon"], icftaFlux)}, coords = {"lon": (["lon"],wrflon_list), "lat": (["lat"], wrflat_list)})
set_trace()
ds.cfta.plot()
plt.show()


