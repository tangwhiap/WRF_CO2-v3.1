import numpy as np
from getdata import getdata as gd
from GetStationInfo import getinfo as gti
import datetime as dtm
import sys

def nan2undef(vlist, undef):
    vlist = np.array(vlist)
    vlist[np.isnan(vlist)] = undef
    vlist = list(vlist)
    return vlist

#start = "2019-12-01_00:00:00"
#end = "2020-03-01_00:00:00"
#dtMin = 30
#WRFDir = "../data/WRF"
#SENSEDir = "../data/SENSE"
#InfoDir = "../data/stations_info"
#TempDir = "../temp"

start = sys.argv[1]
end = sys.argv[2]
dtMin = int(sys.argv[3])
WRFDir = sys.argv[4]
SENSEDir = sys.argv[5]
InfoDir = sys.argv[6]
TempDir = sys.argv[7]

undef = -9999.0
stainfo_dict = gti(InfoDir)
timeList_dict = {}
co2List_dict = {}
lonList_dict = {}
latList_dict = {}
heightList_dict = {}
first = True

for station in stainfo_dict:
    timeL, co2L = gd(start, end, dtMin, SENSEDir + "/" + stainfo_dict[station][0] + "/K30")
    co2L = nan2undef(co2L, undef)
    timeList_dict[station] = timeL
    co2List_dict[station] = co2L
    lonList_dict[station] = stainfo_dict[station][1]
    latList_dict[station] = stainfo_dict[station][2]
    heightList_dict[station] = stainfo_dict[station][3]
    if first:
        Ntime = len(timeL)
        TimeList = timeL.copy()
        first = False
    else:
        assert len(timeL) == Ntime, "Different length of time series! Happy debugging!"

StationName = [station for station in stainfo_dict]
Nsta = len(stainfo_dict)
with open(TempDir + "/station.dat","w") as outfile:
    outfile.write("# station.dat\n")
    outfile.write("%10d\n"%(Ntime))
    outfile.write("%10d\n"%(Nsta))
    for station in stainfo_dict:
        outfile.write("%12.4f%12.4f%12.4f\n"%(lonList_dict[station], latList_dict[station], heightList_dict[station]))
    for it in range(Ntime):
        datetime = TimeList[it]
        datetime_str = datetime.strftime("%Y-%m-%d_%H:%M:%S")
        outfile.write("%19s\n"%(datetime_str))
        for station in StationName:
            outfile.write("%12.4f\n"%co2List_dict[station][it])


