import datetime as dtm
from datetime import datetime
import numpy as np
import netCDF4 as nc
from netCDF4 import Dataset
from pdb import set_trace
'''
Authors: Wenhan TANG - 12/2020
'''
UserDefined_interpolate = False
interpolate_method = "linear"

def interface(Time,DataDir,wrfdom):

    DataDir = DataDir.strip().split(":")
    infile = DataDir[0].strip() + "/VEGAS_CFtaS_hr_Jan1990_Dec2021.nc"
    datain = Dataset(infile,'r')
    gtimes = datain.variables['time']
    glons = datain.variables['lon'][:]
    glons = ((glons+180)%360)-180
    glats = datain.variables['lat'][:]

    tindex = nc.date2index(Time,gtimes)

    gcfta = datain.variables['cftas'][tindex,:,:].filled(np.nan)

    #To march the dims of gcfta with glons and glats
    #gcfta = gcfta.reshape(1,gcfta.shape[0],gcfta.shape[1]) 

    ## convert CFta units from KgC/m2/sec to mol/km2/hr for WRF
    gcfta = gcfta * 1000./12.*1000000.*3600. ## 1000g/kg, 12g/mol, 1e6 m2/km2, 3600 sec/hr

    glons,glats=np.meshgrid(glons,glats)

    return {"lon" : glons.flatten(), "lat" : glats.flatten(), "value" : gcfta.flatten()}
