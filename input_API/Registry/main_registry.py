#!/usr/bin/env python
"""
InputData API Registry
Authors:
  Wenhan Tang - 11/2020 (Original Version)
  ...
"""
import os
import sys

APIDir = sys.argv[1]
PrepSrcDir = sys.argv[2]

RegDir = APIDir + "/Registry"

def autoWarn_py(f):
    f.write("#!/usr/bin/env python\n")
    f.write("\"\"\"\n")
    f.write("!!! --- WARNING --- !!!\n")
    f.write("!!! This script is generated automatically by InputData API Registry. !!!\n")
    f.write("!!! Don't edit, Your changes to this file will be lost  !!!\n")
    f.write("\"\"\"\n")

def autoWarn_sh(f):
    f.write("#!/bin/bash\n")
    f.write("#!!! --- WARNING --- !!!\n")
    f.write("#!!! This script is generated automatically by InputData API Registry. !!!\n")
    f.write("#!!! Don't edit, Your changes to this file will be lost  !!!\n")


def registry_udapi(inType):
    global RegDir, APIDir
    _configf = open(APIDir + "/" + inType + "/API_code/_config.py","w")
    autoWarn_py(_configf)
    DataNameList = []
    with open(RegDir + "/registry." + inType) as regf:
        for readline in regf:
            line = readline.strip().split()
            if len(line) == 0 or line[0].strip() == "#":
                continue
            if len(line) == 2:
                DataName = line[0].strip()
                DataDir = line[1].strip()
                print("InputData API Registry:  Registering: " + inType + "/" + DataName)
                _configf.write(DataName + "_Dir = \"" + DataDir + "\"\n")
                DataNameList.append(DataName)
                assert os.path.exists(APIDir + "/" + inType + "/API_code/" + DataName + ".py"), "Fatal Error !!! Could not find API code " + APIDir + "/" + inType + "/API_code/" + DataName + ".py"
    _configf.close()
    DataNameList.append("_config")
    with open(APIDir + "/" + inType + "/API_code/__init__.py","w") as intf:
        autoWarn_py(intf)
        intf.write("__all__ = " + str(DataNameList) + "\n")

    process_dirName = PrepSrcDir + "/" + ("process_input" if inType in ["emiss", "cfta"] else "process_bckg")
    if os.path.exists(process_dirName + "/" + inType + "_API"):
        #os.system("unlink " + PrepSrcDir + "/process_" + inType + "/API_code")
        os.system("unlink " + process_dirName + "/" + inType +  "_API")
    os.system("ln -sf " + APIDir +  "/" + inType + "/API_code " + process_dirName + "/" + inType +   "_API")
    
def registry_geog():
    global RegDir, APIDir
    with open(RegDir + "/registry.geog") as regf:
        for readline in regf:
            if len(readline.strip()) == 0 or readline.strip()[0] == "#":
                continue
            line = readline.strip().split()
            if len(line) == 0:
                continue
            if len(line) == 2:
                DataName = line[0].strip()
                DataDir = line[1].strip()
                print("InputData API Registry:  Registering: geog/" + DataName)
                #_configf = open(APIDir + "/" + inType + "/_" + DataName + "_config.sh","w")
                _configf = open(APIDir + "/geog/_" + DataName + "_config.sh","w")
                autoWarn_sh(_configf)
                _configf.write("GeoDataDir=" + DataDir + "\n")
                _configf.close()

def registry_met_sst(inType):
    global RegDir, APIDir
    with open(RegDir + "/registry." + inType) as regf:
        for readline in regf:
            if len(readline.strip()) == 0 or readline.strip()[0] == "#":
                 continue
            line = readline.strip().split()
            if len(line) == 0:
                continue
            if len(line) == 5:
                DataName = line[0].strip()
                VtableName = line[1].strip()
                NameForm = line[2].strip()
                MetDataDt = line[3].strip()
                DataDir = line[4].strip()
                print("InputData API Registry:  Registering: " + inType + "/" + DataName)
                _configf = open(APIDir + "/" + inType + "/_" + DataName + "_config.sh","w")
                autoWarn_sh(_configf)
                if inType == "met":
                    var_prefix = "Met"
                if inType == "sst":
                    var_prefix = "SST"
                _configf.write(var_prefix + "VtableName=" + VtableName + "\n")
                _configf.write(var_prefix + "NameForm=" + NameForm + "\n")
                _configf.write(var_prefix + "DataDt=" + MetDataDt + "\n")
                _configf.write(var_prefix + "DataDir=" + DataDir + "\n")
                _configf.close()

if __name__ == "__main__":

    inputTypeList = ["emiss","cfta","bckg","geog","met","sst"]
    for inType in inputTypeList:
        if inType in ["emiss","cfta","bckg"]:
            registry_udapi(inType)
        if inType in ["geog"]:
            registry_geog()
        if inType in ["met","sst"]:
            registry_met_sst(inType)


