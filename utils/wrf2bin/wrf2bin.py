#!/usr/bin/env python

# 1. extract vars from wrf 
# 2. destagger 
# 3. calauate monmean, daymean, hourmean 
# 4. convert to GrADS format(use Numpy: tofile)
# No circulation, extremely fast
# Yang RuQi & Tang WenHan 2020 Sep
print('importing ...')
import numpy as np
from pdb import set_trace as stc
import datetime as dtm
import xarray as xr 

import os
import sys
import f90nml as nml

Start = sys.argv[1]
End = sys.argv[2]
Dom_id = sys.argv[3]
DataDir = sys.argv[4]
OutDir = sys.argv[5]
WrfNmlDir = sys.argv[6]
TempDir = sys.argv[7]
hourly = sys.argv[8]
daily = sys.argv[9]
monthly = sys.argv[10]
print(TempDir)
hourly = True if hourly.lower() == "true" else False
daily = True if daily.lower() == "true" else False
monthly = True if monthly.lower() == "true" else False

fnml = nml.read(WrfNmlDir + "/namelist.input")
domains_dtmins = fnml["time_control"]["auxhist23_interval"]
dtmins = domains_dtmins[int(Dom_id) - 1]
#pwd = os.getcwd()
#PDir = pwd + "/.."
Data_name = 'wrfco2'
Dom_name = "d" + Dom_id.zfill(2)
#dtmins = 15
#Start = "2020-01-01_00:00:00"
#End = "2020-02-19_06:00:00"
VarRequaire = {"CO2_TOT":(1,38),"CO2_BCK":(1,38),"CO2_FFE":(1,38),"CO2_VEGAS":(1,38),"U":(1,38),"V":(1,38),"T":(1,38),"PH":(1,39),"PHB":(1,39),"W":(1,39),"PBLH":(1,1),"HGT":(1,1),"U10":(1,1),"V10":(1,1)}
#hourly = True
#daily = True
#monthly = True

#DataDir = PDir + "/data"
#OutDir = PDir + "/output"
#TempDir = PDir + "/temp"
start = dtm.datetime.strptime(Start,"%Y-%m-%d_%H:%M:%S")
end = dtm.datetime.strptime(End,"%Y-%m-%d_%H:%M:%S")
dt = dtm.timedelta(minutes=dtmins)
#var_list_4 = ['CO2_TOT', 'CO2_BCK', 'CO2_FFDAS', 'CO2_VEGAS']#'CO2_TOT,CO2_BCK,CO2_FFDAS,CO2_VEGAS'
#var_list_1 = ['U', 'V']
#VarRequaire = {"CO2_TOT":(1,4),"U":(1,1)}
for ivar in VarRequaire:
    #print(type(VarRequaire[ivar][0]))
    assert int(VarRequaire[ivar][0]) == VarRequaire[ivar][0] and int(VarRequaire[ivar][1]) == VarRequaire[ivar][1]
    assert VarRequaire[ivar][1] >= VarRequaire[ivar][0]

def d_array(array,integer=False):
    #compute dx, dy, dz ...
    d=(array[1:]-array[:-1]).mean()
    if integer:
        d=int(d)
    return d

def FilesQuiry(string):
    lscmd = "ls " + string
    files = os.popen(lscmd)
    files = files.read().strip().split("\n")
    return files

def nc_cat(FileNameList,TempDir,OutName):
    def cdo_cat_each_batch(TempDir,file_id,FileNameList):
        #os.chdir(TempDir)
        command = "cdo mergetime " + FileNameList + " " + TempDir + "/_cat_" + str(file_id) +".tmpnc"
        os.system(command)

    Nfile = len(FileNameList)
    BatchSize = 1020
    file_id = 1
    FileList_each_batch = np.arange(0,Nfile,BatchSize)
    for ibatch in range(len(FileList_each_batch)-1):
        fs = FileList_each_batch[ibatch]
        fe = FileList_each_batch[ibatch+1]
        #stc()
        #print(ibatch)
        FileList2concat = " ".join(FileNameList[fs:fe])
        cdo_cat_each_batch(TempDir, file_id, FileList2concat)
        file_id += 1
    fs = FileList_each_batch[-1]
    fe = Nfile
    FileList2concat = " ".join(FileNameList[fs:fe])
    cdo_cat_each_batch(TempDir, file_id, FileList2concat)
    command = "cdo -mergetime " + TempDir + "/_cat_*.tmpnc " + TempDir + "/" + OutName
    print(command)
    os.system(command)
    command = "rm -f " + TempDir + "/_cat_*.tmpnc "
    print(command)
    os.system(command) 

def StagQuiry(VarName):
    VarName = VarName.upper()
    Xstag = False
    Ystag = False
    Zstag = False
    if VarName in ["U"]:
        Xstag = True
    if VarName in ["V"]:
        Ystag = True
    if VarName in ["ZNW","W","PH","PHB"]:
        Zstag = True
    return Xstag,Ystag,Zstag

def destag_2bin(ds_dict,lon_center,lat_center,lev_center,time,ftype):
    global OutDir, Data_name, Dom_name, VarRequaire
    assert ftype.lower() in ["orig","hourly","daily","monthly"]
        #print(allvars_nz_dict)
    nx = len(lon_center)
    ny = len(lat_center)
    nz = len(lev_center)
    nt = len(time)
    xs = lon_center[0]
    ys = lat_center[0]
    zs = lev_center[0]
    dx = d_array(lon_center)
    dy = d_array(lat_center)
    dz = d_array(lev_center)
    if ftype.lower() == "orig":
        fout_name = Data_name + "_" + Dom_name
    elif ftype.lower() == "hourly":
        fout_name = Data_name + "_" + Dom_name + "_hourly"
    elif ftype.lower() == "daily":
        fout_name = Data_name + "_" + Dom_name + "_daily"
    elif ftype.lower() == "monthly":
        fout_name = Data_name + "_" + Dom_name + "_monthly"
    else:
        assert False
    varout_dict = {}
    with open(OutDir + "/" + fout_name + ".gdat","wb") as fout:
        for itime in range(len(time)):
            print('Time = ',itime)
            for ivar in VarRequaire:
                print('Write variable: ', ivar) 
                Xstag, Ystag, Zstag = StagQuiry(ivar)
                vzs = VarRequaire[ivar][0]
                vze = VarRequaire[ivar][1]
                key = "z" + str(vzs).zfill(2) + "-" + str(vze).zfill(2)
                values_out = ds_dict[key][ivar].isel(XTIME=itime).values
                if Xstag:
                    values_out = (values_out[:,:,:-1] + values_out[:,:,1:])/2
                if Ystag:
                    values_out = (values_out[:,:-1,:] + values_out[:,1:,:])/2
                if Zstag:
                    values_out = (values_out[:-1,:,:] + values_out[1:,:,:])/2
                values_out.tofile(fout)
                if itime == 0:
                    zlist = list(np.arange(vzs,vze+1).astype(str))
                    varout_dict[ivar] = [str(vze - vzs + 1 - (1 if Zstag else 0)),"99",ivar+" Z: " + ",".join(zlist)]
        print("Make CTL file for " + ftype +" data ...")
        ctl_write(varout_dict,ftype,nx,xs,dx,ny,ys,dy,nz,zs,dz,nt)

def ctl_write(varout_dict,ftype,nx,xs,dx,ny,ys,dy,nz,zs,dz,nt):
    global DataDir, OutDir, Data_name, Dom_name, start,dt
    assert ftype.lower() in ["orig","hourly","daily","monthly"]
    nvar=len(varout_dict)
    if ftype.lower() == "orig":
        fout_name = Data_name + "_" + Dom_name
        strdtime = str(int(dt.total_seconds()/60)) + "mn"
    elif ftype.lower() == "hourly":
        fout_name = Data_name + "_" + Dom_name + "_hourly"
        strdtime = "1hr"
    elif ftype.lower() == "daily":
        fout_name = Data_name + "_" + Dom_name + "_daily"
        strdtime = "1dy"
    elif ftype.lower() == "monthly":
        fout_name = Data_name + "_" + Dom_name + "_monthly"
        strdtime = "1mo"
    else:
        assert False
    #write ctl files for physical variables in center grid
    with open(OutDir + '/' + fout_name + '.ctl', 'w') as f:
        #f.write("dset " + OutDir + "/" + fout_name + ".gdat\n")
        f.write("dset ^" + fout_name + ".gdat\n")
        f.write("undef -888\n")
        f.write("TITLE WRF-CO2 output in binary format\n")
        f.write("xdef "+str(nx)+" linear "+str(xs)+" "+str(dx)+"\n")
        f.write("ydef "+str(ny)+" linear "+str(ys)+" "+str(dy)+"\n")
        f.write("zdef "+str(nz)+" linear "+str(zs)+" "+str(dz)+"\n")
        f.write("tdef "+str(nt)+" linear "+start.strftime("%H:%SZ%d%b%Y")+" " + strdtime + "\n")
        f.write("vars "+str(nvar)+"\n")
        for ivar in varout_dict:
            f.write(ivar)
            for iw in varout_dict[ivar]:
                f.write(" " + iw)
            f.write("\n")
        f.write("endvars\n") 

if __name__ == "__main__":

    print("mkdir -p "+TempDir)
    os.system("mkdir -p "+TempDir)
    var_zr_dict = {}
    for var in VarRequaire:
        vzs = VarRequaire[var][0]
        vze = VarRequaire[var][1]
        key = "z" + str(vzs).zfill(2) + "-" + str(vze).zfill(2)
        #vzl = list(np.arange(vzs,vze+1).astype(str))
        #vzlstr = ",".join(vzl)
        if key in var_zr_dict:
            var_zr_dict[key].append(var)
        else:
            var_zr_dict[key] = [var]

    allvars_nz_dict = {}
#    for zlist in var_zr_dict:
#        for ivar in var_zr_dict[zlist]:
#            allvars_nz_dict[ivar] = zlist[-1]
    for var in VarRequaire:
        allvars_nz_dict[var] = int(VarRequaire[var][1]) - int(VarRequaire[var][0]) + 1
    print(var_zr_dict)
    print(allvars_nz_dict)
#    exit()
    #extract var -- cdo
    print('start extract vars from files')
    now = start
    temp_prefix_list = []
    while(now<=end):
        file_now = Data_name + '_' + Dom_name + '_' + now.strftime("%Y-%m-%d_%H:%M:%S")
        print(file_now)
        for zrange in var_zr_dict:
            vzs = int(zrange[1:3])
            vze = int(zrange[4:6])
            zlist = list(np.arange(vzs,vze+1).astype(str))
            command = "cdo -sellevidx," + ",".join(zlist) + " -selname," + ",".join(var_zr_dict[zrange]) + " " + DataDir + "/" + file_now + " " + TempDir+'/temp_' + zrange + '_'+file_now
            print(command)
            os.system(command)
            #if not(zlist[-1].zfill(2) in temp_prefix_list):
            #    temp_prefix_list.append(zlist[-1].zfill(2))
        now += dt
    print('cat files')
#cat file -- cdo
    for prefix_id in var_zr_dict:
        print(prefix_id)
        nc_cat(FilesQuiry(TempDir + '/temp_'+prefix_id+'*'),TempDir,prefix_id+"_temp.nc")
        print('/bin/rm -f '+TempDir+'/temp_'+prefix_id+'*')
        os.system('/bin/rm -f '+TempDir+'/temp_'+prefix_id+'*')
    print('to daymean, monmean and hr mean')
    for prefix_id in var_zr_dict:
        if hourly:
            command = 'cdo hourmean '+TempDir+'/'+prefix_id+'_temp.nc '+TempDir+'/hr_'+prefix_id+'_temp.nc'
            print(command)
            os.system(command)
        if daily:
            command = 'cdo daymean '+TempDir+'/'+prefix_id+'_temp.nc '+TempDir+'/day_'+prefix_id+'_temp.nc'
            print(command)
            os.system(command)
        if monthly:
            command = 'cdo monmean '+TempDir+'/'+prefix_id+'_temp.nc '+TempDir+'/mon_'+prefix_id+'_temp.nc'
            print(command)
            os.system(command)

    file_sample =  Data_name + '_' + Dom_name + '_' + start.strftime("%Y-%m-%d_%H:%M:%S")
    ds_sample = xr.open_dataset(DataDir + "/" + file_sample)
    lon = ds_sample.XLONG.values[0,0]
    lat = ds_sample.XLAT.values[0,:,0]
    lev = ds_sample.bottom_top.values

    #Original data output
    ds_dict = {}
    for prefix_id in var_zr_dict:
        ds_dict[prefix_id] = xr.open_dataset(TempDir + "/" + prefix_id + "_temp.nc")
    time = ds_dict[prefix_id].XTIME.values
    destag_2bin(ds_dict,lon,lat,lev,time,"orig")
    
    #Hourly data output
    if hourly:
        ds_dict = {}
        for prefix_id in var_zr_dict:
            ds_dict[prefix_id] = xr.open_dataset(TempDir + "/hr_" + prefix_id + "_temp.nc")
        time = ds_dict[prefix_id].XTIME.values
        destag_2bin(ds_dict,lon,lat,lev,time,"hourly")

    #Daily data output
    if daily:
        ds_dict = {}
        for prefix_id in var_zr_dict:
            ds_dict[prefix_id] = xr.open_dataset(TempDir + "/day_" + prefix_id + "_temp.nc")
        time = ds_dict[prefix_id].XTIME.values
        destag_2bin(ds_dict,lon,lat,lev,time,"daily")

    #Monthly data output
    if monthly:
        ds_dict = {}
        for prefix_id in var_zr_dict:
            ds_dict[prefix_id] = xr.open_dataset(TempDir + "/mon_" + prefix_id + "_temp.nc")
        time = ds_dict[prefix_id].XTIME.values
        destag_2bin(ds_dict,lon,lat,lev,time,"monthly")

    #print("/bin/rm -fr "+TempDir)
    #os.system("rm -fr "+TempDir)
    print("=================================")
    print("!!!    Successful Complete    !!!")
    print("=================================")

