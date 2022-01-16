#!/usr/bin/env python
'''
WRF-CO2 tracers registry module: mksrc.py

Used for creating some import source code files of WRF-chem to add ensemble co2-relavant variables into WRF-CO2 model automatically by given ensemble number: N_ensemble

Authors:
  Wenhan TANG - 08/2021 
  ...
'''
from read_registry import read_registry
from utils import write_dict_info
import os
import re
import sys

from pdb import set_trace

#N_ensemble_ffe = int(sys.argv[1])
#N_ensemble_fta = int(sys.argv[2])
#N_ensemble_bck = int(sys.argv[3])
regisDir = sys.argv[1]
demoDir = sys.argv[2]
OutDir = sys.argv[3]
FileType = sys.argv[4]

assert FileType in ["module_ghg_fluxes", "registry_chem", "var_output", "input_dft"]

regisFile = regisDir + "/registry.tracers"
FFE_dic, FTA_dic, BCK_dic, ANA_dic = read_registry(regisFile)

for varName in FFE_dic:
    ConcName = "CO2_FFE_" + varName.upper()
    ConcName_f90 = ConcName.lower()
    FluxName = "E_CO2_FFE_" + varName.upper()
    FluxName_f90 = FluxName.lower()
    FFE_dic[varName]["ConcName"] = ConcName
    FFE_dic[varName]["ConcName_f90"] = ConcName_f90
    FFE_dic[varName]["FluxName"] = FluxName
    FFE_dic[varName]["FluxName_f90"] = FluxName_f90

for varName in FTA_dic:
    ConcName = "CO2_FTA_" + varName.upper()
    ConcName_f90 = ConcName.lower()
    FluxName = "E_BIO_FTA_" + varName.upper()
    FluxName_f90 = "ebio_fta_" + varName.lower()
    FTA_dic[varName]["ConcName"] = ConcName
    FTA_dic[varName]["ConcName_f90"] = ConcName_f90
    FTA_dic[varName]["FluxName"] = FluxName
    FTA_dic[varName]["FluxName_f90"] = FluxName_f90

for varName in BCK_dic:
    ConcName = "CO2_BCK_" + varName.upper()
    ConcName_f90 = ConcName.lower()
    BCK_dic[varName]["ConcName"] = ConcName
    BCK_dic[varName]["ConcName_f90"] = ConcName_f90

for varName in ANA_dic:
    type_ = ANA_dic[varName]["type"]
    if type_ == "C":
        ConcName = varName.upper()
        ConcName_f90 = ConcName.lower()
        ANA_dic[varName]["ConcName"] = ConcName
        ANA_dic[varName]["ConcName_f90"] = ConcName_f90

    if type_ == "E":
        #FluxName = "E_" + varName.upper()
        FluxName = varName.upper()
        FluxName_f90 = FluxName.lower()
        ANA_dic[varName]["FluxName"] = FluxName
        ANA_dic[varName]["FluxName_f90"] = FluxName_f90

    if type_ == "F":
        #FluxName = "E_BIO_" + varName.upper()
        #FluxName_f90 = "ebio_" + varName.lower()
        FluxName = varName.upper()
        FluxName_f90 = FluxName.lower()
        ANA_dic[varName]["FluxName"] = FluxName
        ANA_dic[varName]["FluxName_f90"] = FluxName_f90

def head_warning(pfout, shp = False):
    hd = "#" if shp else ""
    pfout.write(hd + "!!! --------------------------------------------------------------------------- !!!\n")
    pfout.write(hd + "!!!                               !!! WARNING !!!                               !!!\n")
    pfout.write(hd + "!!! This code is generated automatically by TRACERS REGISTRY MODULE:  mksrc.py  !!!\n")
    pfout.write(hd + "!!!             Don't edit it, your changes to this file will be lost.          !!!\n")
    pfout.write(hd + "!!!            If you have any question, please contact Wenhan TANG at          !!!\n")
    pfout.write(hd + "!!!                             tangwh@mail.iap.ac.cn                           !!!\n")
    pfout.write(hd + "!!! --------------------------------------------------------------------------- !!!\n")


def fortran(varName):
    global FFE_dic, FTA_dic, BCK_dic, ANA_dic
    assert varName in ANA_dic
    formula = ANA_dic[varName]["formula"]
    type_ = ANA_dic[varName]["type"]
    replaceList = list(set(re.findall("<(.*?)>", formula)))
    replaceDic = {}
    for content in replaceList:
        if content.strip() == "ME":
            if type_ == "C":
                content_f90 = "chem(i,k,j,p_" + ANA_dic[varName]["ConcName_f90"] + ")"
            elif type_ == "E":
                content_f90 = "emis_ant(i,k,j,p_" + ANA_dic[varName]["FluxName_f90"] + ")"
            elif type_ == "F":
                content_f90 = "eghg_bio(i,1,j,p_" + ANA_dic[varName]["FluxName_f90"] + ")"
            replaceDic["<" + content + ">"] = content_f90
            continue
        replaceVarName, varGroup, varType = tuple([icon.strip() for icon in content.strip().split(",")])
        replaceVarName = replaceVarName.upper()
        loc = locals()
        exec("var_dic = " + varGroup + "_dic")
        var_dic = loc["var_dic"]
        assert varType in ["C", "F", "E"]
        if varType == "C":
            content_f90 = "chem(i,k,j,p_" + var_dic[replaceVarName]["ConcName_f90"] + ")"
        if varType == "E":
            content_f90 = "emis_ant(i,1,j,p_" + var_dic[replaceVarName]["FluxName_f90"] + ")"
        if varType == "F":
            content_f90 = "eghg_bio(i,1,j,p_" + var_dic[replaceVarName]["FluxName_f90"] + ")"
        replaceDic["<" + content + ">"] = content_f90

    formula_f90 = formula
    for content in replaceDic:
        formula_f90 = formula_f90.replace(content, replaceDic[content])

    return formula_f90



    

def write__module_ghg_fluxes(InDir, OutDir):
    #global N_ensemble_ffe, N_ensemble_fta, N_ensemble_bck
    global FFE_dic, FTA_dic, BCK_dic, ANA_dic

    def write__p_co2_ffe(pf):
        #for ien in range(1, N_ensemble_ffe + 1):
        for varName in FFE_dic:
            ConcName_f90 = FFE_dic[varName]["ConcName_f90"]
            FluxName_f90 = FFE_dic[varName]["FluxName_f90"]
            pf.write(" " * 9 + "chem(i,k,j,p_" + ConcName_f90 + ")=  chem(i,k,j,p_" + ConcName_f90 + ") + conv_rho* emis_ant(i,k,j,p_" + FluxName_f90 + ")\n")

    def write__p_co2_fta(pf):
        #for ien in range(1, N_ensemble_fta + 1):
        for varName in FTA_dic:
#chem(i,1,j,p_co2_fta)= chem(i,1,j,p_co2_fta) + conv_rho* eghg_bio(i,1,j,p_ebio_fta)
            ConcName_f90 = FTA_dic[varName]["ConcName_f90"]
            FluxName_f90 = FTA_dic[varName]["FluxName_f90"]
            pf.write(" " * 12 + "chem(i,1,j,p_" + ConcName_f90 + ")=  chem(i,1,j,p_" + ConcName_f90 + ") + conv_rho* eghg_bio(i,1,j,p_" + FluxName_f90 + ")\n")

    def write__p_co2_ana_C(pf):
        for varName in ANA_dic:
            if ANA_dic[varName]["type"] != "C":
                continue
            strFormula = fortran(varName)
            pf.write(" " * 9 + strFormula + "\n")
        
    def write__p_co2_ana_EF(pf):
        for varName in ANA_dic:
            if ANA_dic[varName]["type"] != "E" and ANA_dic[varName]["type"] != "F":
                continue
            assert False, "The technical problem has not been resolved in current version."
            strFormula = fortran(varName)
            pf.write(" " * 13 + strFormula + "\n")
    #def write__p_co2_tot(pf):
    #    for ien in range(1, N_ensemble + 1):
    #        pf.write(" " * 9 + "chem(i,k,j,p_co2_tot" + str(ien) + ") = chem(i,k,j,p_co2_bck) + chem(i,k,j,p_co2_fta) +  chem(i,k,j,p_co2_ffe" + str(ien) + ") - 800.\n")

    pfin = open(InDir + "/module_ghg_fluxes.F.demo")
    pfout = open(OutDir + "/module_ghg_fluxes.F", "w")
    
    head_warning(pfout)
    
    for rec in pfin:
        pfout.write(rec)
        if rec.strip() == "!$JDAS$-p_co2_ffe":
            write__p_co2_ffe(pfout)

        #if rec.strip() == "!$JDAS$-p_co2_tot":
        #    write__p_co2_tot(pfout)
        if rec.strip() == "!$JDAS$-p_co2_fta":
            write__p_co2_fta(pfout)

        if rec.strip() == "!$JDAS$-p_co2_ana-C":
            write__p_co2_ana_C(pfout)

        if rec.strip() == "!$JDAS$-p_co2_ana-EF":
            write__p_co2_ana_EF(pfout)

    pfin.close()
    pfout.close()
    os.system("chmod +x " + OutDir + "/module_ghg_fluxes.F")

def write__registry_chem(InDir, OutDir):
    #global N_ensemble_ffe, N_ensemble_fta, N_ensemble_bck
    global FFE_dic, FTA_dic, BCK_dic, ANA_dic

    def write__e_co2_ffe(pf):
        #for ien in range(1, N_ensemble_ffe + 1):
        for varName in FFE_dic:
            FluxName = FFE_dic[varName]["FluxName"]
            FluxName_f90 = FFE_dic[varName]["FluxName_f90"]
            desc = "CO2 flux (" + FFE_dic[varName]["description"] + ")"
            pf.write("state    real  " + FluxName_f90 + "      i+jf     emis_ant     1         Z      i5r    \"" +  FluxName + "\"               \"" + desc + "\"          \"mol km^-2 hr^-1\"\n")
    
    def write__co2_ffe(pf):
        #for ien in range(1, N_ensemble_ffe + 1):
        for varName in FFE_dic:
            ConcName = FFE_dic[varName]["ConcName"]
            ConcName_f90 = FFE_dic[varName]["ConcName_f90"]
            desc = "CO2 tracer (" + FFE_dic[varName]["description"] + ")"
            pf.write("state   real    " + ConcName_f90 + "    ikjftb   chem         1         -     i0{12}rhusdf=(bdy_interp:dt)  \"" + ConcName + "\"      \"" + desc + "\"        \"ppmv\"\n")
    
    def write__ebio_fta(pf):
#state    real  ebio_fta      i+jf     eghg_bio     1         Z      i6r    "E_BIO_VEGAS"               "VEGAS C flux to Atm"          "mol km^-2 hr^-1"
        #for ien in range(1, N_ensemble_fta + 1):
        for varName in FTA_dic:
            FluxName = FTA_dic[varName]["FluxName"]
            FluxName_f90 = FTA_dic[varName]["FluxName_f90"]
            desc = "CO2 flux (" + FTA_dic[varName]["description"] + ")"
            pf.write("state    real  " + FluxName_f90 +  "      i+jf     eghg_bio     1         Z      i6r    \"" + FluxName +  "\"               \"" + desc + "\"          \"mol km^-2 hr^-1\"\n")

    def write__co2_fta(pf):
#state   real    co2_fta    ikjftb   chem         1         -     i0{12}rhusdf=(bdy_interp:dt)  "CO2_VEGAS"      "mixing ratio of CO2, VEGAS bio fluxes"        "ppmv"
        #for ien in range(1, N_ensemble_fta + 1):
        for varName in FTA_dic:
            ConcName = FTA_dic[varName]["ConcName"]
            ConcName_f90 = FTA_dic[varName]["ConcName_f90"]
            desc = "CO2 tracer (" + FTA_dic[varName]["description"] + ")"
            pf.write("state   real    " + ConcName_f90 + "    ikjftb   chem         1         -     i0{12}rhusdf=(bdy_interp:dt)  \"" + ConcName + "\"      \"" + desc + "\"        \"ppmv\"\n")

    def write__co2_bck(pf):
#state   real    co2_bck    ikjftb   chem         1         -     i0{12}rhusdf=(bdy_interp:dt)  "CO2_BCK"       "mixing ratio of background CO2"             "ppmv"
        #for ien in range(1, N_ensemble_bck + 1):
        for varName in BCK_dic:
            ConcName = BCK_dic[varName]["ConcName"]
            ConcName_f90 = BCK_dic[varName]["ConcName_f90"]
            desc = "CO2 tracer (" + BCK_dic[varName]["description"] + ")"
            pf.write("state   real    " + ConcName_f90  + "    ikjftb   chem         1         -     i0{12}rhusdf=(bdy_interp:dt)  \"" + ConcName + "\"       \"" + desc + "\"             \"ppmv\"\n")

    #def write__co2_tot(pf):
    #    for ien in range(1, N_ensemble + 1):
    #        pf.write("state   real    co2_tot" + str(ien) + "    ikjftb   chem         1         -     i0{12}rhusdf=(bdy_interp:dt)  \"CO2_TOT" + str(ien) + "\"      \"mixing ratio of CO2, total\"        \"ppmv\"\n")

    def write__co2_tracer(pf):
        strw = "package   co2_tracer        chem_opt==16             -             chem:co2_ant,co2_bio,co2_oce,co_ant,co_bck,co2_bck,co2_fta,co2_ffe"
        #for ien in range(1, N_ensemble_ffe + 1):
        for varName in FFE_dic:
            strw += "," + FFE_dic[varName]["ConcName_f90"] #+ ",co2_fta" + str(ien) + ",co2_bck" + str(ien)
        #for ien in range(1, N_ensemble_fta + 1):
        for varName in FTA_dic:
            strw += "," + FTA_dic[varName]["ConcName_f90"]
        #for ien in range(1, N_ensemble_bck + 1):
        for varName in BCK_dic:
            strw += "," + BCK_dic[varName]["ConcName_f90"]

        for varName in ANA_dic:
            if ANA_dic[varName]["type"] != "C":
                continue
            strw += "," + ANA_dic[varName]["ConcName_f90"]

        pf.write(strw + "\n")
    
    def write__eco2(pf):
        strw = "package   eco2            emiss_opt==16                  -             emis_ant:e_co2,e_co2tst,e_co,e_co2_ffe"
        #for ien in range(1, N_ensemble_ffe + 1):
        for varName in FFE_dic:
            strw += "," + FFE_dic[varName]["FluxName_f90"]
        for varName in ANA_dic:
            if ANA_dic[varName]["type"] != "E":
                continue
            strw += "," + ANA_dic[varName]["FluxName_f90"]

        pf.write(strw + "\n")
    
    def write__ebioco2(pf):
#package   ebioco2       bio_emiss_opt==16            -             vprm_in:vegfra_vprm,evi,evi_min,evi_max,lswi,lswi_max,lswi_min;eghg_bio:ebio_gee,ebio_res,ebio_co2oce,ebio_fta
        strw = "package   ebioco2       bio_emiss_opt==16            -             vprm_in:vegfra_vprm,evi,evi_min,evi_max,lswi,lswi_max,lswi_min;eghg_bio:ebio_gee,ebio_res,ebio_co2oce,ebio_fta"
        #for ien in range(1, N_ensemble_fta + 1):
        for varName in FTA_dic:
            strw += "," + FTA_dic[varName]["FluxName_f90"]
        for varName in ANA_dic:
            if ANA_dic[varName]["type"] != "F":
                continue
            strw += "," + ANA_dic[varName]["FluxName_f90"]

        pf.write(strw + "\n")
   
    def write__co2_ana_C(pf):
        write_dic = {}
        for varName in ANA_dic:
            if ANA_dic[varName]["type"] == "C":
                write_dic[varName] = ANA_dic[varName]

        if len(write_dic) == 0:
            return
        for varName in write_dic:
            ConcName = ANA_dic[varName]["ConcName"]
            ConcName_f90 = ANA_dic[varName]["ConcName_f90"]
            desc = ANA_dic[varName]["description"]
            pf.write("state   real    " + ConcName_f90 + "    ikjftb   chem         1         -     i0{12}rhusdf=(bdy_interp:dt)  \"" + ConcName + "\"      \"" + desc + "\"        \"ppmv\"\n")

    def write__co2_ana_E(pf):
        write_dic = {}
        for varName in ANA_dic:
            if ANA_dic[varName]["type"] == "E":
                write_dic[varName] = ANA_dic[varName]

        if len(write_dic) == 0:
            return
        for varName in write_dic:
            FluxName = ANA_dic[varName]["FluxName"]
            FluxName_f90 = ANA_dic[varName]["FluxName_f90"]
            desc = ANA_dic[varName]["description"]
            pf.write("state    real  " + FluxName_f90 + "      i+jf     emis_ant     1         Z      i5r    \"" +  FluxName + "\"               \"" + desc + "\"          \"mol km^-2 hr^-1\"\n")

    def write__co2_ana_F(pf):
        write_dic = {}
        for varName in ANA_dic:
            if ANA_dic[varName]["type"] == "F":
                write_dic[varName] = ANA_dic[varName]

        if len(write_dic) == 0:
            return

        for varName in write_dic:
            FluxName = ANA_dic[varName]["FluxName"]
            FluxName_f90 = ANA_dic[varName]["FluxName_f90"]
            desc = ANA_dic[varName]["description"]
            pf.write("state    real  " + FluxName_f90 +  "      i+jf     eghg_bio     1         Z      i6r    \"" + FluxName +  "\"               \"" + desc + "\"          \"mol km^-2 hr^-1\"\n")


    pfin = open(InDir + "/registry.chem.demo")
    pfout = open(OutDir + "/registry.chem", "w")
    
    head_warning(pfout, shp = True)
    
    for rec in pfin:
        pfout.write(rec)
        if rec.strip() == "#$JDAS$-e_co2_ffe":
            write__e_co2_ffe(pfout)

        if rec.strip() == "#$JDAS$-ebio_fta":
            write__ebio_fta(pfout)

        if rec.strip() == "#$JDAS$-co2_bck":
            write__co2_bck(pfout)

        if rec.strip() == "#$JDAS$-co2_ffe":
            write__co2_ffe(pfout)

        if rec.strip() == "#$JDAS$-co2_fta":
            write__co2_fta(pfout)

        if rec.strip() == "#$JDAS$-co2_ana-C":
            write__co2_ana_C(pfout)

        if rec.strip() == "#$JDAS$-co2_ana-E":
            write__co2_ana_E(pfout)

        if rec.strip() == "#$JDAS$-co2_ana-F":
            write__co2_ana_F(pfout)

        #if rec.strip() == "#$JDAS$-co2_tot":
        #    write__co2_tot(pfout)

        if rec.strip() == "#$JDAS$-co2_tracer":
            write__co2_tracer(pfout)
        
        if rec.strip() == "#$JDAS$-eco2":
            write__eco2(pfout)

        if rec.strip() == "#$JDAS$-ebioco2":
            write__ebioco2(pfout)
        
    pfin.close()
    pfout.close()
    os.system("chmod +x " + OutDir + "/registry.chem")

def write__var_output(OutDir):
    #global N_ensemble_ffe, N_ensemble_fta, N_ensemble_bck
    global FFE_dic, FTA_dic, BCK_dic, ANA_dic
    pfout = open(OutDir + "/var_output.dft", "w")
    #strw = "+:h:23:CO2_TOT,CO2_VEGAS,E_BIO_VEGAS,CO2_FFE,E_CO2_FFE,CO2_BCK,ZNU,T,P,PB,Q2,T2,PSFC,U10,V10,HGT,PBLH,U,V,ZNW,W,PH,PHB,XLONG,XLAT,XLONG_U,XLAT_U,XLONG_V,XLAT_V,XTIME\n"
    strw = "+:h:23:ZNU,T,P,PB,Q2,T2,PSFC,U10,V10,HGT,PBLH,U,V,ZNW,W,PH,PHB,XLONG,XLAT,XLONG_U,XLAT_U,XLONG_V,XLAT_V,XTIME\n"

    strw += "+:h:23:AVGFLX_RUM,AVGFLX_RVM,AVGFLX_WWM,QVAPOR,CFU1,CFD1,DFU1,DFD1,EFU1,EFD1,ALT,UST,SWDOWN,HFX,LH,MAPFAC_M,MAPFAC_V,MAPFAC_U,MUU,MUV,MUB,MU,P_TOP,RAINC,RAINNC\n"

    #for ien in range(N_ensemble_ffe):
    for varName in FFE_dic:
        strw += "+:h:23:" + FFE_dic[varName]["ConcName"] +  "," + FFE_dic[varName]["FluxName"] + "\n"
    #for ien in range(N_ensemble_fta):
    for varName in FTA_dic:
        strw += "+:h:23:" + FTA_dic[varName]["ConcName"] +  "," + FTA_dic[varName]["FluxName"] + "\n"

    for varName in BCK_dic:
        strw += "+:h:23:" + BCK_dic[varName]["ConcName"] + "\n"

    #for ien in range(N_ensemble_bck):
    for varName in ANA_dic:
        if ANA_dic[varName]["type"] == "C":
            strw += "+:h:23:" + ANA_dic[varName]["ConcName"] + "\n"
        else:
            strw += "+:h:23:" + ANA_dic[varName]["FluxName"] + "\n"

    pfout.write(strw)
    pfout.close()

def write__input_dft(OutDir):
    global FFE_dic, FTA_dic, BCK_dic

    def _to_writeDic(dic):
        write_dic = {}
        for varName in dic:
            varDic = dic[varName]
            var_write_dic = {
                "ConcName": varDic["ConcName"],
                "FluxName": (varDic["FluxName"] if "FluxName" in varDic else None),
                "input": varDic["default_data"],
                "input_kwargs": varDic["default_kwargs"],
                "offset": varDic["offset"],
                "scale": varDic["scale"],
            }
            write_dic[varName] = var_write_dic
        return write_dic

    def _to_writeDic_ANA(dic):
        write_dic = {}
        for varName in dic:
            varDic = dic[varName]
            var_write_dic = {
                "ConcName": varDic["ConcName"],
            }
            write_dic[varName] = var_write_dic
        return write_dic

    write_FFE = _to_writeDic(FFE_dic)
    write_FTA = _to_writeDic(FTA_dic)
    write_BCK = _to_writeDic(BCK_dic)
    write_ANA = _to_writeDic_ANA(ANA_dic)

    with open(OutDir + "/tracers_input.dft", "w") as pfout:
        strw = ""
        #set_trace()
        strw += write_dict_info(write_FFE, head_name = "FFE_dic", head_space = 0) + "\n\n"
        strw += write_dict_info(write_FTA, head_name = "FTA_dic", head_space = 0) + "\n\n"
        strw += write_dict_info(write_BCK, head_name = "BCK_dic", head_space = 0) + "\n\n"
        strw += write_dict_info(write_ANA, head_name = "ANA_dic", head_space = 0) + "\n"
        pfout.write(strw)

        


if __name__ == "__main__":
    if FileType == "module_ghg_fluxes":
        write__module_ghg_fluxes(demoDir, OutDir)
    if FileType == "registry_chem":
        write__registry_chem(demoDir, OutDir)
    if FileType == "var_output":
        write__var_output(OutDir)
    if FileType == "input_dft":
        write__input_dft(OutDir)
