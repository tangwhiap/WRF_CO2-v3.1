import numpy as np
import sys
#WRFDir = "../data/WRF"
#DataDir = "../data"
#TempDir = "../temp"
#OutDir = "../output"
FileName = "namelist.o2g"
varname = "co2"
varLongName = "CO2 concentration (ppm)"
#num_out = "True"
#dtMin = 30
#dom = 1

WRFDir = sys.argv[1]
DataDir = sys.argv[2] 
TempDir = sys.argv[3]
OutDir = sys.argv[4]
num_out = sys.argv[5]
dtMin = int(sys.argv[6])
dom = int(sys.argv[7])
output_split = sys.argv[8]
hourly = sys.argv[9]
daily = sys.argv[10]
monthly = sys.argv[11]

valid_record = {"xdef":(), "ydef":(), "zdef":()}
CtlFile = open(WRFDir + "/wrfco2_d0" + str(dom).zfill(1) + "_center.ctl")
for line in CtlFile:
    line_list = line.strip().split()
    first_sign = line_list[0].lower()
    if first_sign in valid_record:
        valid_record[first_sign] = (line_list[1], line_list[3], line_list[4])
CtlFile.close()

# Variables required in namelist.o2g
# nlon, nlat, nlev, lon_s, lat_s, dlon, dlat
# varname varLongName dtime
# TempDir, DataDir, OutDir
nlon, lon_s, dlon = valid_record["xdef"]
nlat, lat_s, dlat = valid_record["ydef"]
nlev, lev_s, dlev = valid_record["zdef"]
num_out = "." + num_out.upper() + "."
output_split = "." + output_split.upper() + "."
hourly = "." + hourly.upper() + "."
daily = "." + daily.upper() + "."
monthly = "." + monthly.upper() + "."
with open(FileName, "w") as nml:
    nml.write("&grid\n")
    nml.write(" nlon = %s,\n"%(nlon))
    nml.write(" nlat = %s,\n"%(nlat))
    nml.write(" nlev = %s,\n"%(nlev))
    nml.write(" str_lon_s = '%s',\n"%(lon_s))
    nml.write(" str_lat_s = '%s',\n"%(lat_s))
    nml.write(" str_dlon = '%s',\n"%(dlon))
    nml.write(" str_dlat = '%s',\n"%(dlat))
    nml.write(" dom = %s,\n"%(str(dom).zfill(1)))
    nml.write("/\n")
    nml.write("&Name\n")
    nml.write(" varname = '%s',\n"%(varname))
    nml.write(" varLongName = '%s',\n"%(varLongName))
    nml.write(" dtime = '%s',\n"%(str(dtMin).zfill(1) + "mn"))
    nml.write("/\n")
    nml.write("&control\n")
    nml.write(" num_out = %s,\n"%(num_out))
    nml.write(" output_split = %s,\n"%(output_split))
    nml.write("/\n")
    nml.write("&mean\n")
    nml.write(" hourly = %s,\n"%(hourly))
    nml.write(" daily = %s,\n"%(daily))
    nml.write(" monthly = %s,\n"%(monthly))
    nml.write("/\n")
    nml.write("&dir\n")
    nml.write(" TempDir = '%s',\n"%(TempDir))
    nml.write(" DataDir = '%s',\n"%(DataDir))
    nml.write(" WRFDir = '%s',\n"%(WRFDir))
    nml.write(" OutDir = '%s',\n"%(OutDir))
    nml.write("/\n")
