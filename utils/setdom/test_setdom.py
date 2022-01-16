#!/usr/bin/env python
# This is a script for showing domain configure.
# Authors:
#  Wenhan Tang - 01/2021
#  ...


import f90nml as nml
from setdomlib import *
import sys
from draw_setdom import draw_domain
#RunDir = "/home/tangwh/wrf-latlon/setdom/work"
#domType = "Maryland"
#RunDir = sys.argv[1]
#domType = sys.argv[2]

configDirName = sys.argv[1]
domType = sys.argv[2]
OutDir = sys.argv[3]
Savefig = sys.argv[4]
IsDrawStation = sys.argv[5]

if IsDrawStation.lower() == "true":
    IsDrawStation = True
else:
    IsDrawStation = False
if IsDrawStation:
    StaConfig = sys.argv[6]
    IsDrawName = sys.argv[7]
    if IsDrawName.lower() == "true":
        IsDrawName = True
    else:
        IsDrawName = False
if Savefig.lower() == "x11":
    Savefig = None

def set_domain(domain_config_dic):
    dom_list = []
    max_dom = len(domain_config_dic)
    for idom in range(1, max_dom + 1):
        idom_name = "d" + str(idom).zfill(2)
        assert idom_name in domain_config_dic, "main_setdom: Could not find " + idom_name
        assert idom_name == domain_config_dic[idom_name]["name"], "main_setdom: key word: " + idom_name + " conflicts with name of domain object: " + domain_config_dic[idom_name]["name"]
        dom = domain(domain_config_dic[idom_name])
        if idom != 1:
            dom.nesting(dom_list)
        dom_list.append(dom)
    return dom_list


if __name__ == "__main__":
    
    nml_file = nml.read(configDirName)
    assert domType in nml_file, "domain type: " + domType + " not be found."
    nml_dic = nml_file[domType]
    max_dom = nml_dic["max_dom"]
    xs = nml_dic["xs"]
    xe = nml_dic["xe"]
    ys = nml_dic["ys"]
    ye = nml_dic["ye"]
    dx = nml_dic["dx"]
    dy = nml_dic["dy"]
    assert len(xs) >= max_dom and len(xe) >= max_dom and len(ys) >= max_dom and len(ye) >= max_dom and len(dx) >= max_dom and len(dy) >= max_dom, "namelist.setdom: args number error."
    domain_config_dic = {}
    for idom in range(max_dom):
        domain_name = "d" + str(idom + 1).zfill(2)
        domain_config_dic[domain_name] = {"lon_s" : xs[idom], "lon_e" : xe[idom], "lat_s" : ys[idom], "lat_e" : ye[idom], "dlon" : dx[idom], "dlat" : dy[idom], "name" : domain_name}
    dom_list = set_domain(domain_config_dic)
    with open(OutDir + "/.domain_range", "w") as fout:
        for idom, dom in enumerate(dom_list):
            print("Configure of domain: d" + str(idom + 1).zfill(2))
            print(dom)
            fout.write("%.4f,%.4f,%.4f,%.4f\n" % (dom.lon_s, dom.lon_e, dom.lat_s, dom.lat_e))
    if IsDrawStation:
        StationsDic = {}
        with open(StaConfig) as fin:
            for iline in fin:
                readline = iline.strip().split()
                StaName = readline[0].strip()
                lon = float(readline[1].strip())
                lat = float(readline[2].strip())
                StationsDic[StaName] = (lon, lat)
    if IsDrawStation:
        draw_domain(OutDir + "/.domain_range", StationsDic = StationsDic, StaName = IsDrawName, Savefig = Savefig)
    else:
        draw_domain(OutDir + "/.domain_range", Savefig = Savefig)



