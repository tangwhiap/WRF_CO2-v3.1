#!/usr/bin/env python
import f90nml as nml
import sys

ConfigDir = sys.argv[1]
Region = sys.argv[2]

nmlf = nml.read(ConfigDir + "/setdom.nml")
max_dom = nmlf[Region]["max_dom"]
print("set max_dom = " + str(max_dom))

with open(ConfigDir + "/max_dom.sh", "w") as f:
    f.write("#!/bin/bash\n")
    f.write("# This script is generated automatically by WRF-CO2 CORE: get_maxdom.py\n")
    f.write("max_dom=" + str(max_dom) + "\n")
