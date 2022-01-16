#!/usr/bin/env python


import numpy as np
from pdb import set_trace

def areaS(LON, LAT):
    # LON, LAT unit: degree
    # S unit: km^2
    R = 6371
    dlon = (LON[0, 1:] - LON[0, :-1]).mean()
    dlat = (LAT[1:, 0] - LAT[:-1, 0]).mean()
    S = (R**2) * np.deg2rad(dlon) * (np.sin(np.deg2rad(LAT + dlat/2 )) - np.sin(np.deg2rad(LAT - dlat/2 )))
    assert S.shape == LON.shape
    assert S.shape == LAT.shape
    return S


def resample_points(pData, pLon, pLat, wrfdom):

    wrfLON = wrfdom["lonwrf"]
    wrfLAT = wrfdom["latwrf"]

    lon_s = wrfdom["lon_w"]
    lon_e = wrfdom["lon_e"]
    lat_s = wrfdom["lat_s"]
    lat_e = wrfdom["lat_n"]
    dlon = wrfdom["dLon"]
    dlat = wrfdom["dLat"]

    indexWithin = (pLon >= lon_s) & (pLon <= lon_e) & (pLat >= lat_s) & (pLat <= lat_e)
    indexWithout = ~indexWithin
    if np.sum(indexWithout) > 0:
        print("Warning! There are " + str(np.sum(indexWithout)) + " point source is out of range")
    
    pLon = pLon[indexWithin]
    pLat = pLat[indexWithin]
    pData = pData[indexWithin]
    
    ixList = (pLon - lon_s + dlon/2)/dlon
    iyList = (pLat - lat_s + dlat/2)/dlat
    ixList = ixList.astype(np.int)
    iyList = iyList.astype(np.int)

    emissField = np.zeros_like(wrfLON)
    for ix, iy, iData in zip(ixList, iyList, pData):
        emissField[iy, ix] += iData

    return emissField


