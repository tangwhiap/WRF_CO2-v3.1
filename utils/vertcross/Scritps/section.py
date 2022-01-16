#!/usr/bin/env python
import numpy as np
import netCDF4 as nc
import xarray as xr
import datetime as dtm
import time
import vertcross as vtc
from pdb import set_trace

str_StartDT = "2021-01-03_00:00:00"
str_EndDT = "2021-01-26_00:00:00"
#str_EndDT = "2018-12-01_00:01:00"
dtMins = 15
Domid = 1
in_prefix = "wrfco2"
out_prefix = "wrfvtc"
DataDir = "../data/1"
OutDir = "../output"
sections_dic = {
        "BJ_TJ": {"start": (114.27, 41.74), "end": (117.6, 38.86), "Nbins": 150},
        "BTS": {"start": (116.26, 40), "end": (117.52, 38.93), "Nbins": 100},
        "BH": {"start": (116.7, 40.27), "end": (114.19, 36.57), "Nbins": 200},
        "N397": {"start": (116.08, 39.7), "end": (119.25, 39.7), "Nbins": 80} }

#varlist = ["CO2_TOT", "CO2_FFE", "CO2_FFE_INDUS", "CO2_FFE_RESID", "CO2_FFE_MOBILE", "CO2_FFE_INDUSP", "CO2_FFE_CEMENT", "CO2_FFE_HEAT", "CO2_FFE_OTHER", "CO2_FFE_POWER"]
varlist = ["CO2_TOT", "CO2_FFE"]

# Specific relative height layers.
#z_spec = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1500, 1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000]#, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 9000, 10000]

z_spec = np.arange(50, 5050, 50)


Start = dtm.datetime.strptime(str_StartDT, "%Y-%m-%d_%H:%M:%S")
End = dtm.datetime.strptime(str_EndDT, "%Y-%m-%d_%H:%M:%S")
dt = dtm.timedelta(minutes = dtMins)
DomName = "d" + str(Domid).zfill(2)
N_sections = len(sections_dic)
N_vars = len(varlist)
N_vert = len(z_spec)


def GetDomInfo(SampleFile):
    global nx, ny, nz
    sf = SampleFile
    lonlist = sf.variables["XLONG"][0,0].filled(np.nan)
    latlist = sf.variables["XLAT"][0,:,0].filled(np.nan)
    nx = sf.dimensions["west_east"].size
    ny = sf.dimensions["south_north"].size
    nz = sf.dimensions["bottom_top"].size
    assert nx == len(lonlist)
    assert ny == len(latlist)
    lon_s = lonlist[0]
    lat_s = latlist[0]
    lon_e = lonlist[-1]
    lat_e = latlist[-1]
    dlon = (lonlist[1:] - lonlist[:-1]).mean()
    dlat = (latlist[1:] - latlist[:-1]).mean()
    return {"lon_s": lon_s, "lon_e": lon_e, "lat_s": lat_s, "lat_e": lat_e, "dlon": dlon, "dlat": dlat, "nx": nx, "ny": ny, "nz": nz}

ds_sample = nc.Dataset(DataDir + "/" + in_prefix + "_" + DomName + "_" + Start.strftime("%Y-%m-%d_%H:%M:%S"))
wrfdom = GetDomInfo(ds_sample)

def init_files(sections_dic):
    global  N_sections, N_vars, N_vert, OutDir, DomName, wrfdom, z_spec, ds_sample
    outfile = nc.Dataset(OutDir + "/" + out_prefix + "_" + DomName + "_" + Start.strftime("%Y-%m-%d_%H:%M:%S"), "w", format = "NETCDF3_64BIT")
    outvars = {}
    outfile.createDimension("time", None)
    outfile.createDimension("wrf_eta", wrfdom["nz"])
    outfile.createDimension("z_spec", N_vert)
    outfile.createDimension("VarName", N_vars)
    outfile.createDimension("StringLength", 50)
    for section in sections_dic:
        outfile.createDimension("section_" + section, sections_dic[section]["Nbins"])
        outfile.createVariable("crosslon_" + section, "f", ("section_" + section))[:] = sections_dic[section]["vtc"].crosslon
        outfile.createVariable("crosslat_" + section, "f", ("section_" + section))[:] = sections_dic[section]["vtc"].crosslat
        outvars["VTC_o_" + section] = outfile.createVariable("VTC_o_" + section, "f", ("time", "VarName", "wrf_eta", "section_" + section))
        outvars["VTC_o_" + section].units = "ppm"
        outvars["VTC_z_" + section] = outfile.createVariable("VTC_z_" + section, "f", ("time", "VarName", "z_spec", "section_" + section))
        outvars["VTC_z_" + section].units = "ppm"
        outvars["Surface_z_" + section] = outfile.createVariable("Surface_z_" + section, "f", ("time", "section_" + section))
        outvars["Surface_z_" + section].units = "meter"
        outvars["PBLH_" + section] = outfile.createVariable("PBLH_" + section, "f", ("time", "section_" + section))
        outvars["PBLH_" + section].units = "meter"

    outvars["time"] = outfile.createVariable("time", "f", ("time"))
    outvars["time"].units = ds_sample.variables["XTIME"].units
    outfile.createVariable("wrf_eta", "f", ("wrf_eta"))[:] = ds_sample.variables["ZNU"][0].filled(np.nan)
    outfile.createVariable("z_spec", "f", ("z_spec"))[:] = np.array(z_spec)
    outfile.createVariable("VarName", "S1", ("VarName", "StringLength"))[:] = nc.stringtochar(np.array(varlist, "S50"))
    outfile.setncattr("Description", "Vertical cross sections computed from WRF-CO2 output on domain " + DomName)
    outfile.setncattr("History", "Created " + time.ctime(time.time()))
    outfile.setncattr("Source", "section.py - Wenhan TANG - LASG IAP - 03/2021")
    return outfile, outvars



#set_trace()
if __name__ == "__main__":
    for section in sections_dic:
        sections_dic[section]["vtc"] = vtc.vertcross(wrfdom, sections_dic[section]["start"], sections_dic[section]["end"], sections_dic[section]["Nbins"], name = section)

    outfile, outvars = init_files(sections_dic)

    itime = 0
    Current = Start
    while(Current <= End):
        print("Processing: ", Current.strftime("%Y-%m-%d_%H:%M:%S"))
        infile = nc.Dataset(DataDir + "/" + in_prefix + "_" + DomName + "_" + Current.strftime("%Y-%m-%d_%H:%M:%S"))
        model_time = infile.variables["XTIME"][0].filled(np.nan)
        Z_3D = ( infile.variables["PH"][0].filled(np.nan) + infile.variables["PHB"][0].filled(np.nan) ) / 9.8
        Z_3D = (Z_3D[1:] + Z_3D[:-1]) / 2
        P_3D = infile.variables["P"][0].filled(np.nan) + infile.variables["PB"][0].filled(np.nan)
        P_3D = P_3D / 100 # Convert unit from Pa to hPa
        HGT_2D = infile.variables["HGT"][0].filled(np.nan)
        #Z = (Z_3D + HGT_2D)
        Z = Z_3D
        PBLH = infile.variables["PBLH"][0].filled(np.nan)
        PBLH_alt = PBLH + HGT_2D

        outvars["time"][itime] = model_time
        for section in sections_dic:
            print(" -- ", section)
            array1 = np.full( (N_vars, wrfdom["nz"], sections_dic[section]["Nbins"]), np.nan)
            array2 = np.full( (N_vars, N_vert, sections_dic[section]["Nbins"]), np.nan)
            Z_ = np.swapaxes(Z, 0, 1)
            Z_ = np.swapaxes(Z_, 1, 2)
            Z_ = sections_dic[section]["vtc"].belinear(Z_)
            outvars["Surface_z_" + section][itime] = Z_[0]
            #PBLH_alt_ = np.swapaxes(PBLH_alt, 0, 1)
            #PBLH_alt_ = np.swapaxes(PBLH_alt_, 1, 2)
            PBLH_alt_ = sections_dic[section]["vtc"].belinear(PBLH_alt[:, :, np.newaxis])
            PBLH_alt_ = PBLH_alt_[0]
            #set_trace()
            #outvars["PBLH_" + section][itime] = 
            for ivar, VarName in enumerate(varlist):
                print(" ==> ", VarName)
                data = infile.variables[VarName][0].filled(np.nan)
                data = np.swapaxes(data, 0, 1)
                data = np.swapaxes(data, 1, 2)
                data_ = sections_dic[section]["vtc"].belinear(data)
                array1[ivar] = data_.copy()
                data_ = vtc.chg_vert_coords(data_, Z_, np.array(z_spec))
                array2[ivar] = data_.copy()
            outvars["VTC_o_" + section][itime] = array1
            outvars["VTC_z_" + section][itime] = array2
            outvars["PBLH_" + section][itime] = PBLH_alt_

        itime += 1
        Current += dt
    outfile.close()
