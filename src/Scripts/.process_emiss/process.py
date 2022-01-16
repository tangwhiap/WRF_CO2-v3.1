#!/usr/bin/env python
# Authors:
#   Wenhan TANG - 12/2020
#   ...


import numpy as np
from scipy import interpolate
from API_code import *

def process(EmissType, fluxtime, wrfdom):
    #EmissDir = "/home/tangwh/wrf-latlon/input_API/Emiss/data_link"
    EmissTypeList = EmissType.split("/")

    flux = np.zeros((len(wrfdom['latwrf'][:,0]),len(wrfdom['latwrf'][0])))
    for iemiss in EmissTypeList:
        iemiss = iemiss.strip()
        #iemissDir = EmissDir + "/" + iemiss
        loc = locals()
        exec("iemissDir = _config." + iemiss + "_Dir")
        iemissDir = loc["iemissDir"]
        exec("spec_int = " + iemiss + ".UserDefined_interpolate")
        spec_int = loc["spec_int"]
        if spec_int:
            exec("iemissFlux = " + iemiss + ".interface(fluxtime, iemissDir, wrfdom)")
            iemissFlux = loc["iemissFlux"]
        else:
            exec("int_method = " + iemiss + ".interpolate_method")
            int_method = loc["int_method"]
            assert int_method in ["linear", "nearest", "cubic"],"" 
            exec("iemissFlux_dic = " + iemiss + ".interface(fluxtime, iemissDir, wrfdom)")
            iemissFlux_dic=loc["iemissFlux_dic"]
            flon = iemissFlux_dic["lon"]
            flat = iemissFlux_dic["lat"]
            fiemissValue = iemissFlux_dic["value"]
            iemissFlux = interpolate.griddata((flon.flatten(),flat.flatten()),fiemissValue.flatten(),(wrfdom['lonwrf'],wrfdom['latwrf']),method = int_method)
        
        flux = np.where(np.isnan(iemissFlux), flux, iemissFlux)

    return flux
    
