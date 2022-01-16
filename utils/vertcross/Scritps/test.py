#!/usr/bin/env python
import numpy as np
import netCDF4 as nc
import vertcross as vtc
from section import GetDomInfo
ds = nc.Dataset("../data/1/wrfco2_d02_2018-12-01_00:00:00")
wrfdom = GetDomInfo(ds)
a=vtc.vertcross(wrfdom,(115.3,41),(117.5,38.9),50)
arr = ds.variables["CO2_TOT"][0].filled(np.nan)
arrt = np.swapaxes(arr, 0, 1)
arrt = np.swapaxes(arrt, 1, 2)
b=a.belinear(arrt)
