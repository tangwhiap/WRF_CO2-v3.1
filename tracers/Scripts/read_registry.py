#!/usr/bin/env python

# Authors:
#   Wenhan TANG - 08/2021
#   ...


def isComment(line):
    if line.strip().split(";")[0] == "":
        return True
    if line.strip().split(";")[0][0] == "#":
        return True
    return False

def strToDic(strDic):
    loc = locals()
    exec("dic = " + strDic)
    dic = loc["dic"]
    return dic

def read_registry(regisFile):
    with open(regisFile) as rgf:
        fLines = []
        for iline in rgf:
            fLines.append(iline.strip())

    FFE_dic = {}
    FTA_dic = {}
    BCK_dic = {}
    ANA_dic = {}
    variableType = None
    loc = locals()
    for iLine in fLines:
        if isComment(iLine):
            continue
        if iLine.strip().split(" ")[0] == "$":
            variableType = iLine.strip().split(" ")[1].upper()
            assert variableType in ["FFE", "FTA", "BCK", "ANA"]
            continue
        #exec("current_dic = " + variableType + "_dic")
        #current_dic = loc["current_dic"]
        
        if variableType == "FFE":
            infoList = iLine.strip().split(";")
            infoList = [info.strip() for info in infoList]
            try:
                name, data, kwargs, offset, scale, desc = tuple(infoList)
            except:
                print(infoList)
            name = name.upper()
            kwargs = strToDic(kwargs)
            #offset = float(offset)
            FFE_dic[name] = {"default_data": data, "default_kwargs": kwargs, "offset": offset, "scale": scale, "description": desc}
            
        if variableType == "FTA":
            infoList = iLine.strip().split(";")
            infoList = [info.strip() for info in infoList]
            name, data, kwargs, offset, scale, desc = tuple(infoList)
            name = name.upper()
            kwargs = strToDic(kwargs)
            #offset = float(offset)
            FTA_dic[name] = {"default_data": data, "default_kwargs": kwargs, "offset": offset, "scale": scale, "description": desc}
            
        if variableType == "BCK":
            infoList = iLine.strip().split(";")
            infoList = [info.strip() for info in infoList]
            name, data, kwargs, offset, scale, desc = tuple(infoList)
            name = name.upper()
            kwargs = strToDic(kwargs)
            BCK_dic[name] = {"default_data": data, "default_kwargs": kwargs, "offset": offset, "scale": scale, "description": desc}
            
        if variableType == "ANA":
            infoList = iLine.strip().split(";")
            infoList = [info.strip() for info in infoList]
            #name, type_, kwargs, desc, formula = tuple(infoList)
            name, type_, desc, formula = tuple(infoList)
            name = name.upper()
            type_ = type_.upper()
            assert type_ in ["C", "E", "F"]
            #ANA_dic[name] = {"type": type_, "default_kwargs": kwargs, "description": desc, "formula": formula}
            ANA_dic[name] = {"type": type_, "description": desc, "formula": formula}

    return FFE_dic, FTA_dic, BCK_dic, ANA_dic

