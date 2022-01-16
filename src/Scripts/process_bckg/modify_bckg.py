#!/usr/bin/env python
# bg_GEOS-Chem.py
#    modify WRF intial / boundary conditions
#    with input from GEOS-Chem netCDF files
#       adapted from bg_CarbonTracker.py (C. Martin - 2/2017)
#       Zheng Ke - 9/2019
#       Wenhan TANG - 12/2020
#       Wenhan TANG - 09/2021 - compatible to V3.1 and later

from scipy import interpolate
import numpy as np
import netCDF4 as nc
import sys
import glob
import datetime as dt
import matplotlib.pyplot as plt
from bckg_API import *
from pdb import set_trace

import warnings
warnings.filterwarnings("ignore")

def modify_bckg(CaseName, RunDir):

    loc = locals()
    exec("from config.tracers_input_" + CaseName + " import FFE_dic, FTA_dic, BCK_dic")
    FFE_dic = loc["FFE_dic"]
    FTA_dic = loc["FTA_dic"]
    BCK_dic = loc["BCK_dic"]
    #bg_Dir = loc["bg_Dir"]
    #print(bg_Dir)
    
    # function to read in WRFbdy/WRFinput files
    # find appropriate GEOS-Chem data
    # interpolate and save

    # GEOS-Chem data dir
    # GCDir = InDir+'/GEOS-Chem'
    ### get list of WRF input and boundary files
    # get all wrfinput files in array
    wrfinf = glob.glob(RunDir+'/wrfinput_*')
    # get all wrfbdy files in array
    wrfbdyf = glob.glob(RunDir+'/wrfbdy_*')
    Z_initial = {}
    Mu_initial = {}
    WRFLat = {}
    WRFLon = {}
 
    wrf_lev  =   [1.0, 0.99, 0.985, 0.98, 0.975, 0.97,
                  0.965, 0.96, 0.955, 0.95, 0.945, 0.94,
                  0.935, 0.93, 0.92, 0.91, 0.90, 0.89,
                  0.88, 0.87, 0.86, 0.85, 0.80, 0.75,
                  0.70, 0.65, 0.60, 0.55, 0.50, 0.45,
                  0.40, 0.35, 0.30, 0.25, 0.20, 0.15,
                  0.10, 0.05, 0.0]
# NARR eta is different from GFS    ZQ.Liu/ZK  2/2020
#  wrf_lev  = [1.0, 0.998, 0.996, 0.994, 0.992, 0.99,
#               0.988, 0.986, 0.984, 0.982, 0.980,
#               0.978, 0.976, 0.974, 0.972, 0.970, 0.968, 0.965,
#               0.96, 0.955, 0.95, 0.945, 0.94, 0.935,
#               0.93, 0.92, 0.91, 0.90, 0.89, 0.88, 0.87,
#               0.86, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60,
#               0.55, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25,
#               0.20, 0.15, 0.10, 0.05, 0.0]

 ## CO2 is on levels, but Z is level+1/2 , so need to average to get eta at CO2 level
    wrf_lev  =  [ "%.6f" %((wrf_lev[i]+wrf_lev[i+1])/2) for i in range(len(wrf_lev)-1)]
  
    bndrys = ['XS','XE','YS','YE']
    slices2d = {'XS':'[:,0]', 'XE':'[:,-1]', 'YS':'[0,:]','YE':'[-1,:]'}
    slices3d = {'XS':'[:,:,0]', 'XE':'[:,:,-1]', 'YS':'[:,0,:]','YE':'[:,-1,:]'}
    doms = ['1','2','3']

    for wrfin in wrfinf:
        print("Modifying " + wrfin)
        # get info from WRF file
        wrfnc   = nc.Dataset(wrfin,'r+')
        wrflat  = wrfnc.variables['XLAT'][0][:]
        wrflon  = wrfnc.variables['XLONG'][0][:]
        WRFLat[str(wrfnc.getncattr('GRID_ID'))] = wrfnc.variables['XLAT'][0][:]
        WRFLon[str(wrfnc.getncattr('GRID_ID'))] = wrfnc.variables['XLONG'][0][:]
        wrftime = wrfnc.variables['Times'][0][:]
        wrftime = ''.join([i.decode("UTF-8") for i in wrftime])
        wrftime = dt.datetime.strptime(wrftime,"%Y-%m-%d_%H:%M:%S")

        # get CO2 from GEOS-Chem out
#        GCt    = wrftime
#        GCFile = GCDir+'/'+GCt.strftime("%Y%m")+'.nc'
#        GCData = nc.Dataset(GCFile)
#        simday  = GCt.day
#        simhour = GCt.hour
#        tindex  = (simday-1)*24+simhour
#        CO2= GCData.variables['co2'][tindex,:,:,:]
#        GClat = GCData.variables['lat']
#        GClon = GCData.variables['lon']
#        GClons, GClats = np.meshgrid(GClon,GClat)
        # first interpolate in the horizontal

        for varName in BCK_dic:
            print("Processing input background " + varName + " ...")
            ConcName = BCK_dic[varName]["ConcName"]
            bckg_type = BCK_dic[varName]["input"]
            input_kwargs = BCK_dic[varName]["input_kwargs"]
            offset = float(BCK_dic[varName]["offset"])

            exec("from bckg_API import " + bckg_type + " as bg")
            bg = loc["bg"]
            exec("bg_Dir = _config." + bckg_type + "_Dir")
            bg_Dir = loc["bg_Dir"]
            bg_lev_type = bg.bg_lev_type
            assert bg_lev_type in ["eta"], "Can not recognize vertical coordinate type: " + bg_lev_type

            dic = bg.interface(wrftime, bg_Dir, **input_kwargs)
            bg_lon_2D = dic["lon"]
            bg_lat_2D = dic["lat"]
            bg_lev_3D = dic["lev"]
            bg_CO2_3D = dic["value"]
            CO2regrid1 = []  
            bg_lev_3D_wrflatlon = []
            for z in range(len(bg_CO2_3D[:,0,0])):
                CO2regrid1.append(interpolate.griddata((bg_lon_2D.flatten(),bg_lat_2D.flatten()),bg_CO2_3D[z].flatten(),(wrflon,wrflat),method='linear'))
                bg_lev_3D_wrflatlon.append(interpolate.griddata((bg_lon_2D.flatten(),bg_lat_2D.flatten()),bg_lev_3D[z].flatten(),(wrflon,wrflat),method='linear'))
            # now interpolate in the vertical
            CO2regrid1 = np.array(CO2regrid1)
            bg_lev_3D_wrflatlon = np.array(bg_lev_3D_wrflatlon)
           # set_trace()
            CO2regrid2 = []
            for i in range(len(wrflon[0])):
                #lat2d , bg_lev_2D = np.meshgrid(wrflat[:,i],bg_lev_3D[:,0,0].flatten())
                lat2d = np.tile(wrflat[:,i],(len(bg_lev_3D_wrflatlon[:,0,0]),1))
                bg_lev_2D_wrflatlon = bg_lev_3D_wrflatlon[:,:,i]
                lat2dnew , WRFetas = np.meshgrid(wrflat[:,i],wrf_lev)
                CO2touse = CO2regrid1[:,:,i]
                #set_trace()
                CO2regrid2.append(interpolate.griddata((lat2d.flatten(),bg_lev_2D_wrflatlon.flatten()),CO2touse.flatten(),(lat2dnew,WRFetas),method='linear'))
            CO2regrid2 = np.array(CO2regrid2)
             ##### index = [lon(x), vertical(z), lat(y)],we need index = [vertical(z), lat(y), lon(x)]
             ##### so we change the order of the array and insert it into the netCDF file
            CO2regrid2 = np.swapaxes(CO2regrid2,0,1)
            CO2regrid2 = np.swapaxes(CO2regrid2,1,2)
             #replace nan with 400
            nanindex   = np.array(np.where(np.isnan(CO2regrid2)))
            for i in range(nanindex.shape[1]):
                CO2regrid2[nanindex[0,i],nanindex[1,i],nanindex[2,i]] = 400
            #print(CO2regrid2)
            wrfnc.variables[ConcName][0] = CO2regrid2

         #### other tracers we initialize with either a zero or offset
        #for d in doms:
        for varName in FFE_dic:
            ConcName = FFE_dic[varName]["ConcName"]
            offset = float(FFE_dic[varName]["offset"])
            wrfnc.variables[ConcName][0] = 0 + offset

        for varName in FTA_dic:
            ConcName = FTA_dic[varName]["ConcName"]
            offset = float(FTA_dic[varName]["offset"])
            wrfnc.variables[ConcName][0] = 0 + offset

    for wrfbdy in wrfbdyf:
        # get info from WRF file
        print("Modifying " + wrfbdy)
        wrfnc = nc.Dataset(wrfbdy,'r+')
        wrftimes = wrfnc.variables['Times'][:]
        wrftimes = [''.join([i.decode("UTF-8") for i in wrftimes[t]]) for t in range(len(wrftimes))]
        wrftimes = [dt.datetime.strptime(wrftimes[t],"%Y-%m-%d_%H:%M:%S") for t in range(len(wrftimes))]
        if len(wrftimes) == 1:
            wrftimes.append(wrftimes[-1] + dt.timedelta(hours = 6))
            nsecs = (wrftimes[1]-wrftimes[0]).total_seconds()
        else:
            nsecs = (wrftimes[1]-wrftimes[0]).total_seconds()
            wrftimes.append((wrftimes[-1] + dt.timedelta(seconds = nsecs)))

     # empty diGCionary for array of previous values
        prevdata = {}
        nowdata = {}

        for varName in BCK_dic:
            prevdata[varName] = {}
            nowdata[varName] = {}

        for ti in range(len(wrftimes)):
            print("time = " + str(wrftimes[ti]))
            #t = ti
            if ti == (len(wrftimes)-1):
                #t = ti - 1
                isLast = True
            else:
                isLast = False

            if ti == 0:
                isFirst = True
            else:
                isFirst = False
            
            for varName in BCK_dic:
                ConcName = BCK_dic[varName]["ConcName"]
                bckg_type = BCK_dic[varName]["input"]
                input_kwargs = BCK_dic[varName]["input_kwargs"]
                offset = float(BCK_dic[varName]["offset"])

                exec("from bckg_API import " + bckg_type + " as bg")
                bg = loc["bg"]
                exec("bg_Dir = _config." + bckg_type + "_Dir")
                bg_Dir = loc["bg_Dir"]
                bg_lev_type = bg.bg_lev_type
                assert bg_lev_type in ["eta"], "Can not recognize vertical coordinate type: " + bg_lev_type

                # get CO2 from GEOS-Chem out
                dic = bg.interface(wrftimes[ti], bg_Dir, **input_kwargs)
                #GCt    = wrftimes[ti]
                #GCFile = GCDir+'/'+GCt.strftime("%Y%m")+'.nc'
                #GCData = nc.Dataset(GCFile)
                #simday  = GCt.day
                #simhour = GCt.hour
                #tindex  = (simday-1)*24+simhour
                #CO2= GCData.variables['co2'][tindex,:,:,:]
                #GClat = GCData.variables['lat']
                #GClon = GCData.variables['lon']
                #GClons, GClats = np.meshgrid(GClon,GClat)
                bg_lon_2D = dic["lon"]
                bg_lat_2D = dic["lat"]
                bg_lev_3D = dic["lev"]
                bg_CO2_3D = dic["value"]



                # first interpolate in the horizontal
                CO2regrid1 = []
                bg_lev_3D_wrflatlon = []
                wrflat = WRFLat[str(wrfnc.getncattr('GRID_ID'))]
                wrflon = WRFLon[str(wrfnc.getncattr('GRID_ID'))]
                for z in range(len(bg_CO2_3D[:,0,0])):
                    CO2regrid1.append(interpolate.griddata((bg_lon_2D.flatten(),bg_lat_2D.flatten()),bg_CO2_3D[z].flatten(),(wrflon,wrflat),method='linear'))
                    bg_lev_3D_wrflatlon.append(interpolate.griddata((bg_lon_2D.flatten(),bg_lat_2D.flatten()),bg_lev_3D[z].flatten(),(wrflon,wrflat),method='linear'))
                # now interpolate in the vertical
                CO2regrid1 = np.array(CO2regrid1)
                bg_lev_3D_wrflatlon = np.array(bg_lev_3D_wrflatlon)
                
                for bndry in bndrys:
               # if this isn't the first time, save prevdata for tendencis
                    #if ti != 0:
                    if not isFirst:
                        prevdata[varName][bndry] = nowdata[varName][bndry]

                    slice2d = slices2d[bndry]
                    slice3d = slices3d[bndry]
                    loc = locals()
                    #print("latside = wrflat"+slice2d)
                    #print("lonside = wrflon"+slice2d)
                    exec("latside = wrflat"+slice2d)
                    latside = loc["latside"]
                    exec("lonside = wrflon"+slice2d)
                    lonside = loc["lonside"]
                    #latside = wrflat[:,0]
                    #lonside = wrflon[:,0]
                    exec("CO2sub = CO2regrid1"+slice3d)
                    CO2sub = loc["CO2sub"]
                    #exec("latside = 1")
                    #print([i for i in loc])
                    if bndry[0] == 'X':
                        coord2dprev = latside
                    else:
                        coord2dprev = lonside
                    #coord2dBG , _  = np.meshgrid(coord2dprev, bg_lev_3D_new[0,:,:])
                    coord2dBG = np.tile(coord2dprev, (len(bg_lev_3D_wrflatlon[:,0,0]), 1))
                    exec("bg_lev_2D_wrflatlon = bg_lev_3D_wrflatlon" + slice3d)
                    bg_lev_2D_wrflatlon = loc["bg_lev_2D_wrflatlon"]
                    coord2dWRF, WRFetas = np.meshgrid(coord2dprev,wrf_lev)

                    #print("coord2dBG.flatten().shape = ", coord2dBG.flatten().shape)
                    #print("bg_lev_2D_wrflatlon.flatten().shape = ",bg_lev_2D_wrflatlon.flatten().shape)
                    #set_trace()

                    CO2regrid2 = interpolate.griddata((coord2dBG.flatten(),bg_lev_2D_wrflatlon.flatten()),CO2sub.flatten(),(coord2dWRF,WRFetas),method='linear')
                    CO2out = []
                    for w in range(len(wrfnc.dimensions['bdy_width'])):
                        CO2out.append(CO2regrid2)
                    CO2out = np.array(CO2out)
                    nowdata[varName][bndry] = CO2out

                    if not isLast: # last time is to calculate the tendency, so don't write this out
                        wrfnc.variables[ConcName + '_B' + bndry][ti] = CO2out 
                        #for d in doms:
                        #    wrfnc.variables['CO2_VEGAS'+d+'_B'+bndry][t] = subval
                        #    wrfnc.variables['CO2_FFE'+d+'_B'+bndry][t] = 0 
               #wrfnc.variables['CH4_EPA'+d+'_B'+bndry][t] = 0 
           ### now calculate tendencies
           # skip the first time
                    if not isFirst:
                        wrfnc.variables[ConcName + '_BT' + bndry][ti - 1] = (nowdata[varName][bndry] - prevdata[varName][bndry])/nsecs 
                        #for d in doms:
                        #    wrfnc.variables['CO2_VEGAS'+d+'_BT'+bndry][ti-1] = 0 
                        #    wrfnc.variables['CO2_FFE'+d+'_BT'+bndry][ti-1] = 0 
                       #wrfnc.variables['CH4_EPA'+d+'_BT'+bndry][ti-1] = 0 

            for varName in FFE_dic:
                ConcName = FFE_dic[varName]["ConcName"]
                offset = float(FFE_dic[varName]["offset"])
                for bndry in bndrys:
                    if not isLast:
                        wrfnc.variables[ConcName + "_B" + bndry][ti] = 0 + offset
                    if not isFirst:
                        wrfnc.variables[ConcName + "_BT" + bndry][ti - 1] = 0

            for varName in FTA_dic:
                ConcName = FTA_dic[varName]["ConcName"]
                offset = float(FTA_dic[varName]["offset"])
                for bndry in bndrys:
                    if not isLast:
                        wrfnc.variables[ConcName + "_B" + bndry][ti] = 0 + offset
                    if not isFirst:
                        wrfnc.variables[ConcName + "_BT" + bndry][ti - 1] = 0

        # close the file
        wrfnc.close()

#### if script is called from the command line
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('wrong usage:')
        print('bg_GEOS-Chem.py RunDir InDir CaseName')
        sys.exit()

    CaseName = sys.argv[1]
    RunDir = sys.argv[2]
    modify_bckg(CaseName, RunDir)

