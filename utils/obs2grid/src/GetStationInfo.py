import numpy as np
def printWarning(iline, line):
    print("Warning! The line " + str(iline) + " : " + str(line) + " can't be recognized, skip it.")

def getinfo(InfoDir):
    info_dict = {}
    file = open(InfoDir + "/stations_info.txt")
    for iline, line in enumerate(file):
        strline = line.strip().split()
        print(strline)
        if len(strline) != 5:
            printWarning(iline, line)
            continue

        if len(strline[0]) == 0:
            printWarning(iline, line)
            continue

        if strline[0][0] == "#":
            printWarning(iline, line)
            continue
        try:
            StationName_dir = strline[0]
            StationName = strline[1]
            lon = float(strline[2])
            lat = float(strline[3])
            height = float(strline[4])
        except:
            printWarning(iline, line)
            continue
        #info_dict[StationName_dir] = (StationName, lon, lat, height)
        info_dict[StationName] = (StationName_dir, lon, lat, height)
    return info_dict
