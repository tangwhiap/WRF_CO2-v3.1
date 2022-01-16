#!/usr/bin/env python
# Authors:
#    Wenhan TANG - 12/2020
#    ...

import numpy as np
from scipy import interpolate
from API_code import *
def process(cftaType, fluxtime, wrfdom):
    #cftaDir = "/home/tangwh/wrf-latlon/input_API/cfta/data_link"
    cftaTypeList = cftaType.split("/")

    flux = np.zeros((len(wrfdom['latwrf'][:,0]),len(wrfdom['latwrf'][0])))
    for icfta in cftaTypeList:
        icfta = icfta.strip()
        #icftaDir = cftaDir + "/" + icfta
        loc = locals()
        exec("icftaDir = _config." + icfta + "_Dir")
        icftaDir = loc["icftaDir"]
        exec("spec_int = " + icfta + ".UserDefined_interpolate")
        spec_int = loc["spec_int"]
        if spec_int:
            exec("icftaFlux = " + icfta + ".interface(fluxtime, icftaDir, wrfdom)")
            icftaFlux = loc["icftaFlux"]
        else:
            exec("int_method = " + icfta + ".interpolate_method")
            int_method = loc["int_method"]
            assert int_method in ["linear", "nearest", "cubic"],"" 
            exec("icftaFlux_dic = " + icfta + ".interface(fluxtime, icftaDir, wrfdom)")
            icftaFlux_dic=loc["icftaFlux_dic"]
            flon = icftaFlux_dic["lon"]
            flat = icftaFlux_dic["lat"]
            ficftaValue = icftaFlux_dic["value"]
            icftaFlux = interpolate.griddata((flon.flatten(),flat.flatten()),ficftaValue.flatten(),(wrfdom['lonwrf'],wrfdom['latwrf']),method = int_method)
        
        flux = np.where(np.isnan(icftaFlux), flux, icftaFlux)

    return flux
    
