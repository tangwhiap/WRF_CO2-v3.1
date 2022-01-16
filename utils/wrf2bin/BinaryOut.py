#!/usr/bin/env python
#
import netCDF4 as nc
import datetime as dtm
import f90nml as nml
import numpy as np
from pdb import set_trace
import xarray as xr
import sys

restart = sys.argv[-1].lower() == "true"
first = False if restart else True
print(restart)
if first:
    '''
    str_Start = "2020-01-01_00:00:00"
    str_End = "2020-01-02_00:00:00"
    dom_id = 1
    DataDir = "../data"
    Data_id = 23
    OutDir = "../binary_output"
    NmlDir = "."
    prefix = "wrfco2"
    ResDir = "."
    und = -9999.0
    OrigOut = True
    HourlyOut = True
    DailyOut = True
    MonthlyOut = True
    '''
    str_Start = sys.argv[1]
    str_End = sys.argv[2]
    dom_id = int(sys.argv[3])
    DataDir = sys.argv[4]
    Data_id = int(sys.argv[5])
    OutDir = sys.argv[6]
    NmlDir = sys.argv[7]
    prefix = "wrfco2"
    ResDir = sys.argv[8]
    und = -9999.0
    OrigOut = sys.argv[9].lower() == "true"
    HourlyOut = sys.argv[10].lower() == "true"
    DailyOut = sys.argv[11].lower() == "true"
    MonthlyOut = sys.argv[12].lower() == "true"

    str_initial = str_Start
else:
    '''
    str_Start = "2020-01-03_12:00:00"
    # str_initial from restart file.
    str_End = "2020-01-05_00:00:00"
    dom_id = 1
    DataDir = "../data"
    Data_id = 23
    OutDir = "../binary_output"
    NmlDir = "."
    prefix = "wrfco2"
    ResDir = "."
    '''
    str_Start = sys.argv[1]
    # str_initial from restart file.
    str_End = sys.argv[2]
    dom_id = int(sys.argv[3])
    DataDir = sys.argv[4]
    Data_id = int(sys.argv[5])
    OutDir = sys.argv[6]
    NmlDir = sys.argv[7]
    prefix = "wrfco2"
    ResDir = sys.argv[8]

    # und from restart file.
    # OrigOut from restart file.
    # HourlyOut from restart file.
    # DailyOut from restart file.
    # MonthlyOut from restart file.

#print("Output directory:", OutDir)
#print("Original output = ", OrigOut)
#print("Hourly output = ", HourlyOut)
#print("Daily output = ", DailyOut)
#print("Monthly output = ", MonthlyOut)


dom_name = "d" + str(dom_id).zfill(2)

Start = dtm.datetime.strptime(str_Start, "%Y-%m-%d_%H:%M:%S")
End = dtm.datetime.strptime(str_End, "%Y-%m-%d_%H:%M:%S")

if restart:
    # "ds_res" refers the restart file to read, and "ds_rst" refers the restart file to write
    ds_res = xr.open_dataset(ResDir + "/Binary_restart_" + dom_name + "_" + str_Start + ".nc")
    und = ds_res.attrs["und"]
    str_initial = ds_res.attrs["initial"]
    OrigOut = ds_res.attrs["OrigOut"].lower() == "true"
    HourlyOut = ds_res.attrs["HourlyOut"].lower() == "true"
    DailyOut = ds_res.attrs["DailyOut"].lower() == "true"
    MonthlyOut = ds_res.attrs["MonthlyOut"].lower() == "true"
    #set_trace()

initial = dtm.datetime.strptime(str_initial, "%Y-%m-%d_%H:%M:%S")

VarRequaire = ["CO2_TOT", "CO2_BCK", "CO2_FFE", "E_CO2_FFE", "E_CO2_FFE1", "E_CO2_FFE2","E_CO2_FFE3", "CO2_VEGAS", "E_BIO_VEGAS","E_BIO_VEGAS1", "E_BIO_VEGAS2", "E_BIO_VEGAS3", "U", "V", "T", "PH", "PHB", "W", "PBLH", "HGT", "U10", "V10"]

assert len(set(VarRequaire)) == len(VarRequaire), "Variables in the \"VarRequaire\" list are repeated."
VarZ = {}
VarDesc = {}
#Checking dimensions of variables you selected using: first sample file
nx_smp = None
ny_smp = None
nz_smp = None
print("Checking dimensions of variables you selected using: " + prefix + "_" + dom_name + "_" + str_Start)
SampleFile = nc.Dataset(DataDir + "/" + prefix + "_" + dom_name + "_" + str_Start)
for ivar in VarRequaire:
    #print(ivar)
    assert ivar in SampleFile.variables, "Variable: " + ivar + " not found!"
    vardim = SampleFile.variables[ivar].dimensions
    varshape = SampleFile.variables[ivar].shape
    varstag = SampleFile.variables[ivar].stagger
    VarDesc[ivar] = SampleFile.variables[ivar].description

    if "bottom_top" in vardim:
        zdim = True
        zind = vardim.index("bottom_top")
    elif "bottom_top_stag" in vardim:
        zdim = True
        zind = vardim.index("bottom_top_stag")
    else:
        zdim = False

    if "south_north" in vardim:
        ydim = True
        yind = vardim.index("south_north")
    elif "south_north_stag" in vardim:
        ydim = True
        yind = vardim.index("south_north_stag")
    else:
        ydim = False

    if "west_east" in vardim:
        xdim = True
        xind = vardim.index("west_east")
    elif "west_east_stag" in vardim:
        xdim = True
        xind = vardim.index("west_east_stag")
    else:
        xdim = False

    if xdim:
        varnx = varshape[xind]
    if ydim:
        varny = varshape[yind]
    if zdim:
        varnz = varshape[zind]

    if xdim:
        _nx = (varnx - 1) if varstag== "X" else varnx
        if nx_smp == None:
            nx_smp = _nx
        else:
            assert nx_smp == _nx
    if ydim:
        _ny = (varny - 1) if varstag== "Y" else varny
        if ny_smp == None:
            ny_smp = _ny
        else:
            assert ny_smp == _ny
    if zdim:
        _nz = (varnz - 1) if varstag== "Z" else varnz
        if nz_smp == None:
            nz_smp = _nz
        else:
            assert nz_smp == _nz
        VarZ[ivar] = nz_smp
    else:
        VarZ[ivar] = 1
    
assert nx_smp != None and ny_smp != None and nz_smp != None, "There isn't any variable can let me know the whole 3D dimensions (nx,ny,nz)."
print("nx = ", nx_smp, ",", "ny = ", ny_smp, ",", "nz = ", nz_smp)
print("nx_stag = ", nx_smp + 1, ",", "ny_stag = ", ny_smp + 1, ",", "nz_stag = ", nz_smp + 1)
print("PASS!")

# Get xs, dx, ys, dy, zs, dz
lon = SampleFile.variables["XLONG"][0,0,:].filled(np.nan)
lat = SampleFile.variables["XLAT"][0,:,0].filled(np.nan)
xs_smp = lon[0]
ys_smp = lat[0]
dx_smp = np.mean(lon[1:] - lon[:-1])
dy_smp = np.mean(lat[1:] - lat[:-1])
zs_smp = 0
dz_smp = 1

if first:
    nx = nx_smp
    ny = ny_smp
    nz = nz_smp
    xs = xs_smp
    ys = ys_smp
    zs = zs_smp
    dx = dx_smp
    dy = dy_smp
    dz = dz_smp
else: # if restart
    nx = ds_res.attrs["nx"]
    ny = ds_res.attrs["ny"]
    nz = ds_res.attrs["nz"]
    xs = ds_res.attrs["xs"]
    ys = ds_res.attrs["ys"]
    zs = ds_res.attrs["zs"]
    dx = ds_res.attrs["dx"]
    dy = ds_res.attrs["dy"]
    dz = ds_res.attrs["dz"]
    assert nx == nx_smp
    assert ny == ny_smp
    assert nz == nz_smp
    assert xs == xs_smp
    assert ys == ys_smp
    assert zs == zs_smp
    assert dx == dx_smp
    assert dy == dy_smp
    assert dz == dz_smp

fnml = nml.read(NmlDir + "/namelist.input")
if Data_id == 1:
    nml_interval_var = history_interval
else:
    nml_interval_var = "auxhist" + str(Data_id) + "_interval"
print("interval:")
print(fnml["time_control"][nml_interval_var])
interval_smp = fnml["time_control"][nml_interval_var][dom_id - 1]

if first:
    interval = interval_smp
else:
    interval = ds_res.attrs["interval"]
    assert interval == interval_smp, "interval = " + str(interval) + ", interval_smp = " + str(interval_smp)

dt = dtm.timedelta(minutes = int(interval))
if first:
    if OrigOut:
        forig = open(OutDir + "/wrfco2_" + dom_name + ".gdat","wb")
        nt_orig = 0
    if HourlyOut:
        fhr = open(OutDir + "/wrfco2_" + dom_name + "_hourly.gdat","wb")
        hr_dict = {}
        for ivar in VarRequaire:
            hr_dict[ivar] = 0
        hr_count = 0
        nt_hr = 0
    if DailyOut:
        fdy = open(OutDir + "/wrfco2_" + dom_name + "_daily.gdat","wb")
        dy_dict = {}
        for ivar in VarRequaire:
            dy_dict[ivar] = 0
        dy_count = 0
        nt_dy = 0
    if MonthlyOut:
        fmon = open(OutDir + "/wrfco2_" + dom_name + "_monthly.gdat","wb")
        mon_dict = {}
        for ivar in VarRequaire:
            mon_dict[ivar] = 0
        mon_count = 0
        nt_mon = 0
else: # if restart
    if OrigOut:
        forig = open(OutDir + "/wrfco2_" + dom_name + ".gdat","ab")
        nt_orig = ds_res.attrs["nt_orig"]
    if HourlyOut:
        fhr = open(OutDir + "/wrfco2_" + dom_name + "_hourly.gdat","ab")
        hr_dict = {}
        for ivar in VarRequaire:
            hr_dict[ivar] = ds_res["hr_" + ivar].values
        hr_count = ds_res.attrs["hr_count"]
        nt_hr = ds_res.attrs["nt_hr"]
    if DailyOut:
        fdy = open(OutDir + "/wrfco2_" + dom_name + "_daily.gdat","ab")
        dy_dict = {}
        for ivar in VarRequaire:
            dy_dict[ivar] = ds_res["dy_" + ivar].values
        dy_count = ds_res.attrs["dy_count"]
        nt_dy = ds_res.attrs["nt_dy"]
    if MonthlyOut:
        fmon = open(OutDir + "/wrfco2_" + dom_name + "_monthly.gdat","ab")
        mon_dict = {}
        for ivar in VarRequaire:
            mon_dict[ivar] = ds_res["mon_" + ivar].values
        mon_count = ds_res.attrs["mon_count"]
        nt_mon = ds_res.attrs["nt_mon"]

def np2bin(array,f):
    array.tofile(f)

if first:
    CurTime = Start
else:
    CurTime = dtm.datetime.strptime(ds_res.attrs["CurTime"], "%Y-%m-%d_%H:%M:%S")

while( CurTime <= End ):
    #print(hr_count)
    print("Processing: data on " + CurTime.strftime("%Y-%m-%d_%H:%M:%S"))
    FileName = prefix + "_" + dom_name + "_" + CurTime.strftime("%Y-%m-%d_%H:%M:%S")
    ncfile = nc.Dataset(DataDir + "/" + FileName)
    if OrigOut:
        nt_orig += 1
    for ivar in VarRequaire:
        array = ncfile.variables[ivar][0].filled(und)
        if ncfile.variables[ivar].dimensions[1] == "emissions_zdim":
            array = array[0]
        if ncfile.variables[ivar].dimensions[1] == "one":
            array = array[0]
        varstag = ncfile.variables[ivar].stagger
        if varstag == "Z":
            array = (array[1:] + array[:-1])/2
        if varstag == "Y":
            if len(array.shape) == 2:
                array = (array[:,1:] + array[:,:-1])/2
            elif len(array.shape) == 3:
                array = (array[:,1:] + array[:,:-1])/2
            else:
                assert False, "Fatal Error! Variable: " + ivar + "is neither 4D nor 3D."
        if varstag == "X":
            if len(array.shape) == 2:
                array = (array[:,1:] + array[:,:-1])/2
            elif len(array.shape) == 3:
                array = (array[:,:,1:] + array[:,:,:-1])/2
            else:
                assert False, "Fatal Error! Variable: " + ivar + "is neither 4D nor 3D."
        if len(array.shape) == 2:
            assert array.shape[0] == ny
            assert array.shape[1] == nx
        if len(array.shape) == 3:
            assert array.shape[0] == nz
            assert array.shape[1] == ny
            assert array.shape[2] == nx

        if OrigOut:
            print("Writing variable: " + ivar + " to original binary data  on " + CurTime.strftime("%Y-%m-%d %H:%M:%S"))
            np2bin(array,forig)
        if HourlyOut:
            hr_dict[ivar] += array
        if DailyOut:
            dy_dict[ivar] += array
        if MonthlyOut:
            mon_dict[ivar] += array
    if HourlyOut:
        hr_count += 1
    if DailyOut:
        dy_count += 1
    if MonthlyOut:
        mon_count += 1

    NextTime = CurTime + dt
    str_CurTime = CurTime.strftime("%Y%m%d%H%M%S")
    str_NextTime = NextTime.strftime("%Y%m%d%H%M%S")
    if HourlyOut:
        if str_CurTime[:10] != str_NextTime[:10]:
            nt_hr += 1
            for ivar in VarRequaire:
                array = hr_dict[ivar]
                #if ivar == "CO2_TOT":
                    #set_trace()
                if hr_count == 0:
                    print("WARNING !!! hr_count = 0, All field = undefined")
                    array = array * 0 + und
                else:
                    array = array / hr_count
                print("Writing variable: " + ivar + " to hourly binary data on " + CurTime.strftime("%Y-%m-%d %H:%M:%S"))
                np2bin(array,fhr)
                hr_dict[ivar] = 0 * hr_dict[ivar]
            hr_count = 0
    
    if DailyOut:
        if str_CurTime[:8] != str_NextTime[:8]:
            nt_dy += 1
            #print("Writing daily gdat on " + CurTime.strftime("%Y-%m-%d %H:%M:%S"))
            for ivar in VarRequaire:
                array = dy_dict[ivar]
                if dy_count == 0:
                    print("WARNING !!! dy_count = 0, All field = undefined")
                    array = array * 0 + und
                else:
                    array = array / dy_count
                print("Writing variable: " + ivar + " to daily binary data on " + CurTime.strftime("%Y-%m-%d %H:%M:%S"))
                np2bin(array,fdy)
                dy_dict[ivar] = 0 * dy_dict[ivar]
            dy_count = 0
    if MonthlyOut:
        if str_CurTime[:6] != str_NextTime[:6]:
            nt_mon += 1
            #print("Writing monthly gdat on " + CurTime.strftime("%Y-%m-%d %H:%M:%S"))
            for ivar in VarRequaire:
                array = mon_dict[ivar]
                if mon_count == 0:
                    print("WARNING !!! mon_count = 0, All field = undefined")
                    array = array * 0 + und
                else:
                    array = array / mon_count
                print("Writing variable: " + ivar + " to monthly binary data on " + CurTime.strftime("%Y-%m-%d %H:%M:%S"))
                np2bin(array,fmon)
                mon_dict[ivar] = 0 * mon_dict[ivar]
            mon_count = 0
    CurTime = NextTime

if OrigOut:
    forig.close()
if HourlyOut:
    fhr.close()
if DailyOut:
    fdy.close()
if MonthlyOut:
    fmon.close()

# Wrinting ctl files
def ctl_write(ftype):
    global VarRequaire, VarZ, VarDesc
    global DataDir, OutDir, prefix, dom_name, initial, dt, und
    global nx, xs, dx, ny, ys, dy, nz, zs, dz
    assert ftype.lower() in ["orig","hourly","daily","monthly"]
    nvar=len(VarRequaire)
    if ftype.lower() == "orig":
        fout_name = prefix + "_" + dom_name
        strdtime = str(int(dt.total_seconds()/60)) + "mn"
        global nt_orig
        nt = nt_orig
    elif ftype.lower() == "hourly":
        fout_name = prefix + "_" + dom_name + "_hourly"
        strdtime = "1hr"
        global nt_hr
        nt = nt_hr
    elif ftype.lower() == "daily":
        fout_name = prefix + "_" + dom_name + "_daily"
        strdtime = "1dy"
        global nt_dy
        nt = nt_dy
    elif ftype.lower() == "monthly":
        fout_name = prefix + "_" + dom_name + "_monthly"
        strdtime = "1mo"
        global nt_mon
        nt = nt_mon
    else:
        assert False, "\"ftype\" must be one of \"orig\". \"hourly\", \"daily\" and \"monthly\""
    #write ctl files for physical variables in center grid
    with open(OutDir + '/' + fout_name + '.ctl', 'w') as f:
        #f.write("dset " + OutDir + "/" + fout_name + ".gdat\n")
        f.write("dset ^" + fout_name + ".gdat\n")
        f.write("undef " + str(und) + "\n")
        f.write("TITLE WRF-CO2 output in binary format\n")
        f.write("xdef "+str(nx)+" linear "+str(xs)+" "+str(dx)+"\n")
        f.write("ydef "+str(ny)+" linear "+str(ys)+" "+str(dy)+"\n")
        f.write("zdef "+str(nz)+" linear "+str(zs)+" "+str(dz)+"\n")
        f.write("tdef "+str(nt)+" linear "+initial.strftime("%H:%SZ%d%b%Y")+" " + strdtime + "\n")
        f.write("vars "+str(nvar)+"\n")
        for ivar in VarRequaire:
            f.write(ivar + " " + str(VarZ[ivar]) + " 99 " + VarDesc[ivar] + "\n")
        f.write("endvars\n") 

if OrigOut:
    print("Writing ctl file for original binary data ...")
    ctl_write("orig")
if HourlyOut:
    print("Writing ctl file for hourly binary data ...")
    ctl_write("hourly")
if DailyOut:
    print("Writing ctl file for daily binary data ...")
    ctl_write("daily")
if MonthlyOut:
    print("Writing ctl file for monthly binary data ...")
    ctl_write("monthly")


# Writing restart file
print("Writing restart file ...")
ds_rst = xr.Dataset()
ds_rst.coords["z"] = (["z"], np.arange(nz))
ds_rst.coords["y"] = (["y"], np.arange(ny))
ds_rst.coords["x"] = (["x"], np.arange(nx))
if OrigOut:
    ds_rst.attrs["nt_orig"] = nt_orig

if HourlyOut:
    for ivar in hr_dict:
        #print(hr_dict[ivar].shape)
        if len(hr_dict[ivar].shape) == 2:
            dimlist = ["y","x"]
        elif len(hr_dict[ivar].shape) == 3:
            dimlist = ["z","y","x"]
        ds_rst["hr_" + ivar] = (dimlist, hr_dict[ivar])
    ds_rst.attrs["nt_hr"] = nt_hr
    ds_rst.attrs["hr_count"] = hr_count

if DailyOut:
    for ivar in dy_dict:
        if len(dy_dict[ivar].shape) == 2:
            dimlist = ["y","x"]
        elif len(dy_dict[ivar].shape) == 3:
            dimlist = ["z","y","x"]
        ds_rst["dy_" + ivar] = (dimlist, dy_dict[ivar])
    ds_rst.attrs["nt_dy"] = nt_dy
    ds_rst.attrs["dy_count"] = dy_count

if MonthlyOut:
    for ivar in mon_dict:
        if len(mon_dict[ivar].shape) == 2:
            dimlist = ["y","x"]
        elif len(mon_dict[ivar].shape) == 3:
            dimlist = ["z","y","x"]
        ds_rst["mon_" + ivar] = (dimlist, mon_dict[ivar])
    ds_rst.attrs["nt_mon"] = nt_mon
    ds_rst.attrs["mon_count"] = mon_count

ds_rst.attrs["nx"] = nx
ds_rst.attrs["ny"] = ny
ds_rst.attrs["nz"] = nz
ds_rst.attrs["xs"] = xs
ds_rst.attrs["ys"] = ys
ds_rst.attrs["zs"] = zs
ds_rst.attrs["dx"] = dx
ds_rst.attrs["dy"] = dy
ds_rst.attrs["dz"] = dz
ds_rst.attrs["CurTime"] = CurTime.strftime("%Y-%m-%d_%H:%M:%S")
ds_rst.attrs["OrigOut"] = str(OrigOut)
ds_rst.attrs["HourlyOut"] = str(HourlyOut)
ds_rst.attrs["DailyOut"] = str(DailyOut)
ds_rst.attrs["MonthlyOut"] = str(MonthlyOut)
ds_rst.attrs["initial"] = str_initial
ds_rst.attrs["interval"] = interval
ds_rst.attrs["und"] = und
ds_rst.to_netcdf(ResDir + "/Binary_restart_" + dom_name + "_" + (CurTime - dt).strftime("%Y-%m-%d_%H:%M:%S") + ".nc") 
