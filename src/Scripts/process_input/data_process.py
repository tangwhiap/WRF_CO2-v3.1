#!/usr/bin/env python
# Authors:
#   Wenhan TANG - 12/2020
#   ...


import numpy as np
from scipy import interpolate
#from API_code import *
import emiss_API
import cfta_API

def process(inputType, fluxDataList, fluxtime, wrfdom, input_kwargs, offsetList, scaleList):
    #EmissDir = "/home/tangwh/wrf-latlon/input_API/Emiss/data_link"
    inputType = inputType.upper()
    assert inputType in ["FFE", "FTA"]
    if inputType == "FFE":
        #from FFE_API import *
        API = emiss_API
    elif inputType == "FTA":
        #from FTA_API import *
        API = cfta_API

    fluxDataList = [iFlux.strip() for iFlux in fluxDataList.strip().split("/")]
    offsetList = [offset.strip() for offset in offsetList.strip().split("/")]
    scaleList = [scale.strip() for scale in scaleList.strip().split("/")]

    if len(fluxDataList) > 1 and len(offsetList) == 1:
        offsetList = offsetList * len(fluxDataList)

    if len(fluxDataList) > 1 and len(scaleList) == 1:
        scaleList = scaleList * len(fluxDataList)

    assert len(fluxDataList) == len(offsetList)
    assert len(fluxDataList) == len(scaleList)

    if len(fluxDataList) == 1:
        input_kwargs = {fluxDataList[0]: input_kwargs}
    #    offsetList = [offsetList]

    flux = np.zeros((len(wrfdom['latwrf'][:,0]), len(wrfdom['latwrf'][0])))

    for iFlux, offset, scale in zip(fluxDataList, offsetList, scaleList):
        iFlux = iFlux.strip()
        #iFluxDir = EmissDir + "/" + iFlux

        scale_4doms = [scale.strip() for scale in scale.strip().split(",")]
        #offset_4doms = [offset.strip() for offset in offset.strip().split(",")]

        if wrfdom["dom"] != "d01" and len(scale_4doms) != 1:
            scale = scale_4doms[int(wrfdom["dom"]) - 1]
        else:
            scale = scale_4doms[0]

        #if wrfdom["dom"] != "d01" and len(offset_4doms) != 1:
        #    offset = offset_4doms[int(wrfdom["dom"][1:]) - 1]
        #else:
        #    offset = offset_4doms[0]

        scale = float(scale)
        #offset = float(offset)

        loc = locals()
        exec("iFluxDir = API._config." + iFlux + "_Dir")
        iFluxDir = loc["iFluxDir"]
        exec("spec_int = API." + iFlux + ".UserDefined_interpolate")
        spec_int = loc["spec_int"]

        iFlux_kwargs = input_kwargs[iFlux]
        if spec_int:
            exec("iFluxData = API." + iFlux + ".interface(fluxtime, iFluxDir, wrfdom, **iFlux_kwargs)")
            iFluxData = loc["iFluxData"]
        else:
            exec("int_method = API." + iFlux + ".interpolate_method")
            int_method = loc["int_method"]
            assert int_method in ["linear", "nearest", "cubic"],"" 
            exec("iFluxData_dic = API." + iFlux + ".interface(fluxtime, iFluxDir, wrfdom, **iFlux_kwargs)")
            iFluxData_dic=loc["iFluxData_dic"]
            flon = iFluxData_dic["lon"]
            flat = iFluxData_dic["lat"]
            fiFluxValue = iFluxData_dic["value"]
            iFluxData = interpolate.griddata((flon.flatten(),flat.flatten()),fiFluxValue.flatten(),(wrfdom['lonwrf'],wrfdom['latwrf']),method = int_method)

   
        #iFluxData = iFluxData * scale + offset
        iFluxData = iFluxData * scale
        
        flux = np.where(np.isnan(iFluxData), flux, iFluxData)

    return flux
    
