#!/usr/bin/env python
# Caculating the column co2 concentration.
# Authors:
#  Wenhan TANG - 02/2021
#  ...
########################

import numpy as np
import xarray as xr
import datetime as dtm
from pdb import set_trace


str_Start = "2019-01-13_05:30:00"
str_End = "2019-01-21_00:00:00"
dtMins = 15
DomID = 2
InDir = "/home/tangwh/modeling/WRFs/WRF-CO2-v3.0_sectors/WRF-CO2-v3.0-secFFE/cases/sec_20190101_3/output/wrfco2"
OutDir = "../output"
InPrefix = "wrfco2"
OutPrefix = "wrfxco2"


# Eta value of each layer in OCO data.
eta_oco = [0.0005263158, 0.05263158, 0.1052632, 0.1578947,0.2105263,0.2631579, 0.3157895, 0.368421, 0.4210526, 0.4736842,0.5263158, 0.5789474, 0.6315789, 0.6842105, 0.7368421, 0.7894737,0.8421053, 0.8947368, 0.9473684, 1.0 ]

# Weight of each eta layer in OCO data.
oco_mean_knl = [0.3292, 0.4560, 0.6234, 0.7403, 0.8209, 0.8790, 0.9254, 0.9556, 0.9853, 1.0013, 1.0103, 1.0180, 1.0219, 1.0215, 1.0180, 1.0121, 1.0039, 0.9981, 0.9935, 0.9870]

VarList = ["CO2_TOT", "CO2_BCK", "CO2_VEGAS", "CO2_FFE", "CO2_FFE_INDUS", "CO2_FFE_RESID", "CO2_FFE_MOBILE", "CO2_FFE_CEMENT", "CO2_FFE_HEAT", "CO2_FFE_INDUSP", "CO2_FFE_OTHER", "CO2_FFE_POWER"]

DomName = "d" + str(DomID).zfill(2)
eta_oco = np.array(eta_oco)
oco_mean_knl = np.array(oco_mean_knl)



def build_interp_dict(old_coord):
    global eta_oco, oco_mean_knl
    old_coord.sort()
    old_coord_min = old_coord.min()
    old_coord_max = old_coord.max()
    valid_ind = np.where( (eta_oco >= old_coord_min) & (eta_oco <= old_coord_max) )[0]
    eta_oco_valid = eta_oco[valid_ind]
    oco_mean_knl_valid = oco_mean_knl[valid_ind]
    oco_mean_knl_valid = oco_mean_knl_valid / np.sum(oco_mean_knl_valid)

    interp_list = []
    
    eye = 0
    for ind, new in enumerate(eta_oco_valid):
        while True:
            if old_coord[eye] > new:
                assert old_coord[eye - 1] <= new
                break
            else:
                eye = eye + 1
        ia = eye - 1
        ib = eye
        rate = (new - old_coord[ia]) / (old_coord[ib] - old_coord[ia])
        interp_list.append({"ia": ia, "ib": ib, "rate": rate})

    assert len(interp_list) == len(eta_oco_valid)

    return interp_list, eta_oco_valid, oco_mean_knl_valid

def interp_3D_chglev(array_3D, old, new, interp_list):
    array_3D = array_3D[::-1]
    new_length = len(new)
    orig_shape = array_3D.shape
    new_shape = (new_length, orig_shape[1], orig_shape[2])
    array_3D_new = np.full(new_shape, np.nan)
    for ilayer in range(new_length):
        ia = interp_list[ilayer]["ia"]
        ib = interp_list[ilayer]["ib"]
        rate = interp_list[ilayer]["rate"]
        yb = array_3D[ib]
        ya = array_3D[ia]
        array_3D_new[ilayer] = (yb - ya) * rate + ya
    return array_3D_new

def xco2(array_3D_new, knl):
    assert array_3D_new.shape[0] == len(knl)
    array_3D_new_swap = np.swapaxes(array_3D_new, 0, 1)
    array_3D_new_swap = np.swapaxes(array_3D_new_swap, 1, 2)
    xco2 = np.sum(array_3D_new_swap * knl, axis = 2)
    return xco2

if __name__ == "__main__":
    Start = dtm.datetime.strptime(str_Start, "%Y-%m-%d_%H:%M:%S")
    End = dtm.datetime.strptime(str_End, "%Y-%m-%d_%H:%M:%S")
    dt = dtm.timedelta(minutes = dtMins)
    Current = Start
    while(Current <= End):
        print("Processing ", Current.strftime("%Y-%m-%d_%H:%M:%S"), " ...")
        dsIn = xr.open_dataset(InDir + "/" + InPrefix + "_" + DomName + "_" + Current.strftime("%Y-%m-%d_%H:%M:%S"))
        time = dsIn["XTIME"][0].values
        lon = dsIn["XLONG"][0,0,:].values
        lat = dsIn["XLAT"][0,:,0].values
        eta_old = dsIn["ZNU"][0].values
        interp_list, eta_oco_valid, oco_mean_knl_valid = build_interp_dict(eta_old)

        dsOut = xr.Dataset()
        dsOut.coords["time"] = (("time"), np.array([time]))
        dsOut.coords["lat"] = (("lat"), lat)
        dsOut.coords["lon"] = (("lon"), lon)
        for ivar in VarList:
            print("  ==> " + ivar)
            var_data = dsIn[ivar][0].values
            assert var_data.shape[0] == len(eta_old)
            co2_new_lev = interp_3D_chglev(var_data, eta_old, eta_oco_valid, interp_list)
            col_data = xco2(co2_new_lev, oco_mean_knl_valid)
            col_data = col_data.reshape(1, col_data.shape[0], col_data.shape[1])
            dsOut[ivar] = (("time", "lat", "lon"), col_data)
            dsOut[ivar].attrs["units"] = "ppm"
            dsOut[ivar].attrs["long_name"] = "Column concentration of " + ivar
        dsOut["time"].attrs["axis"] = "T"
        dsOut["lat"].attrs["axis"] = "Y"
        dsOut["lon"].attrs["axis"] = "X"
        dsOut["lat"].attrs["units"] = "degrees_north"
        dsOut["lon"].attrs["units"] = "degress_east"
        dsOut.to_netcdf(OutDir + "/" + OutPrefix + "_" + DomName + "_" + Current.strftime("%Y-%m-%d_%H:%M:%S"))

        Current += dt

