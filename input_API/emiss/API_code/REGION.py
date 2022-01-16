#!/usr/bin/env python

from . import MEIC
from . import NDRC
from ._mask_tools import Maskout

import numpy as np
from scipy import interpolate

from pdb import set_trace

UserDefined_interpolate = True
interpolate_method = "linear"

regionToShpname = {
    "BJ": "Beijing", "TJ": "Tianjin", "HB": "Hebei",
}

maskArray_dic = { region: None for region in regionToShpname }
maskArray_dic["OUTER"] = None
maskArray_LON = None
maskArray_LAT = None
maskCreated = False

def _isSame(LON, LAT):
    global maskArray_LON, maskArray_LAT

    if LON.shape != maskArray_LON.shape or LAT.shape != maskArray_LAT.shape:
        return False

    if np.sum(np.abs(LON - maskArray_LON)) <= 1e-6 and np.sum(np.abs(LAT - maskArray_LAT)) <= 1e-6:
        return True
    else:
        return False

def interface(Time,DataDir,wrfdom, region = None):
    NDRC_DataDir = DataDir.strip().split(":")[0]
    MEIC_DataDir = DataDir.strip().split(":")[1]
    global maskArray_dic, maskCreated, maskArray_LON, maskArray_LAT
    region = region.upper()
    assert region in regionToShpname or region == "OUTER"

    makeNew = False
    if maskCreated is False:
        makeNew = True
    else:
        LON = wrfdom["lonwrf"]
        LAT = wrfdom["latwrf"]
        if not _isSame(LON, LAT):
            print("Find difference: " + wrfdom["dom"] + " on " + Time.strftime("%Y-%m-%d_%H:%M:%S"))
            makeNew = True

    if makeNew:
        print("Make new shape for " + wrfdom["dom"] + " on " + Time.strftime("%Y-%m-%d_%H:%M:%S"))
        LON = wrfdom["lonwrf"]
        LAT = wrfdom["latwrf"]
        assert LON.shape == LAT.shape
        maskTotal = np.zeros_like(LON)

        for iRegion in regionToShpname:
            shpName = regionToShpname[iRegion]
            objMask = Maskout(LON = LON, LAT = LAT, Region_list = [shpName])
            maskArray = objMask.mask_array_out()
            maskArray_dic[iRegion] = maskArray.copy()
            maskTotal += maskArray

        maskArray_dic["OUTER"] = np.where(maskTotal == 0, 1, 0)
        maskCreated = True 
        maskArray_LON = LON.copy()
        maskArray_LAT = LAT.copy()

    if region == "OUTER":
        emiss_dic = MEIC.interface(Time, MEIC_DataDir, wrfdom)
        emiss_field = interpolate.griddata((emiss_dic["lon"], emiss_dic["lat"]), emiss_dic["value"], (wrfdom["lonwrf"], wrfdom["latwrf"]), method = MEIC.interpolate_method)
    else:
        print("Use old shape for " + wrfdom["dom"] + " on " + Time.strftime("%Y-%m-%d_%H:%M:%S"))
        emiss_field = NDRC.interface(Time, NDRC_DataDir, wrfdom)

    assert maskArray_dic[region] is not None
    emiss_field = emiss_field * maskArray_dic[region]
    return emiss_field

