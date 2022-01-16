import numpy as np
import netCDF4 as nc
#from . import _config
'''
Authors:
    C. Martin - 2017
    Ke Zheng - 2019
    Wenhan TANG - 12/2020
    ...
'''
eta_geos =   [1.0, 0.977456, 0.962370, 0.947285,0.932200,
                  0.917116, 0.902031, 0.886948, 0.871864, 0.856781,
                  0.841698, 0.826616, 0.809021, 0.786400, 0.761265, 
                  0.736134, 0.711006, 0.685878, 0.654471, 0.616790,
                  0.579115, 0.541449, 0.503795, 0.466153, 0.428528,
                  0.390927, 0.353349, 0.309854, 0.263587, 0.223772,
                  0.190061, 0.161513, 0.137287, 0.116695, 0.099191,
                  0.084313, 0.066559, 0.047641, 0.033814, 0.023755,
                  0.014342, 0.006588, 0.002816, 0.001109, 0.000399,
                  0.000127, 0.000028]

bg_lev_type = "eta"
def interface(Time, DataDir):
    global eta_geos
    # get CO2 from GEOS-Chem out
    GCt    = Time
    GCFile = DataDir + '/' + GCt.strftime("%Y%m")+'.nc'
    GCData = nc.Dataset(GCFile)
    simday  = GCt.day
    simhour = GCt.hour
    tindex  = (simday-1)*24+simhour
    CO2= GCData.variables['co2'][tindex,:,:,:] * 1e6
    GClat = GCData.variables['lat']
    GClon = GCData.variables['lon']
    GClons, GClats = np.meshgrid(GClon,GClat)
    shape = CO2.shape
    nlev = CO2.shape[0]
    nlat = CO2.shape[1]
    nlon = CO2.shape[2]
    assert len(eta_geos) == nlev
    GCetas = np.tile(np.array(eta_geos),(nlon,nlat,1))
    GCetas = np.swapaxes(GCetas, 0, 2)
    return {"lon" : GClons.filled(np.nan), "lat" : GClats.filled(np.nan), "lev" : GCetas, "value" : CO2.filled(np.nan)}
