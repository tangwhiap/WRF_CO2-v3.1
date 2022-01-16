#!/usr/bin/env python

"""
make_emiss.py

generate wrfchemi emissions files for WRF-Chem
using multiple emission inventories
with functions in emissions/<inventory>.py

Authors:

    C. Martin - 4/2017 (Original version)

    Wenhan Tang - 11/2020
      convert it from python2 to python3.
      modified the structure of emiss data prepocessing module,
      let it be compatible with input data API.

    Wenhan TANG - 08/2021
      Rewrite it.
      let it be compatible with tracers registry.
      combined make_emiss amd make_flux.

    Wenhan TANG - 09/2021
      Add parallel running.
      Add the three modes: (online, offline, link), let it to be more flexible.

"""
import datetime as dt
import numpy as np
import netCDF4 as nc
import sys
import os
import f90nml
from data_process import process
import glob
import multiprocessing as mtp
from optparse import OptionParser
import warnings
warnings.filterwarnings("ignore")

from pdb import set_trace

#ffePrefix = "wrfchemi"
#ftaPrefix = "wrfbiochemi"

argv = sys.argv
CaseName = argv[1]
inputType = argv[2]
#RunDir = argv[3]

parser = OptionParser()

parser.add_option("-t", "--runtype", dest = "run type", default = "online")
parser.add_option("-l", "--link", dest = "link", default = "false")
parser.add_option("-d", "--origdir", dest = "orig dir")
parser.add_option("-s", "--start", dest = "start time")
parser.add_option("-e", "--end", dest = "end time")
parser.add_option("-n", "--namelist", dest = "namelist file", default = "./namelist.input")
parser.add_option("-g", "--geodir", dest = "geofile dir")
parser.add_option("-o", "--output", dest = "output dir")
parser.add_option("-r", "--rundir", dest = "run dir")
parser.add_option("-c", "--core", dest = "CPU cores", default = "1")

options, args = parser.parse_args()
options = options.__dict__

runType = options["run type"].lower()
assert runType in ["online", "offline"]

nCores = int(options["CPU cores"])
assert nCores >= 1

if runType == "online":
    assert options["run dir"] is not None
    RunDir = options["run dir"]


    geoDir = RunDir
    namelistFile = RunDir + "/namelist.input"
    starttime = None
    endtime = None

    if options["link"].lower() == "true":
        isLink = True
    else:
        isLink = False

    if isLink:
        assert options["orig dir"] is not None
        origDir = options["orig dir"]


if runType == "offline":
    assert options["start time"] is not None
    starttime = dt.datetime.strptime(options["start time"], "%Y-%m-%d_%H:%M:%S")

    #assert options["end time"] is not None
    endtime = options["end time"]
    endtime = dt.datetime.strptime(options["end time"], "%Y-%m-%d_%H:%M:%S")

    assert options["output dir"] is not None
    OutDir = options["output dir"]

    assert options["namelist file"] is not None
    namelistFile = options["namelist file"]

    assert options["geofile dir"] is not None
    geoDir = options["geofile dir"]

    RunDir = OutDir
    isLink = False


loc = locals()
exec("from config.tracers_input_" + CaseName + " import FFE_dic, FTA_dic")
FFE_dic = loc["FFE_dic"]
FTA_dic = loc["FTA_dic"]

inputType = inputType.upper()
assert inputType in ["FFE", "FTA"]

if inputType == "FFE":
    INPUT_dic = FFE_dic
    auxID = 5
    from emiss_API import *

if inputType == "FTA":
    INPUT_dic = FTA_dic
    #starttimee = FTA_dic
    auxID = 6
    from cfta_API import *

def init_file(RunDir, dom, fluxtime, wrfdom, inputType, auxName):

    """
    init_file(RunDir,dom,fluxtime,wrfdom)
    
    function to initialize a new netCDF emissions input file

    RunDir = directory to run WRF in / output flux file
    dom = domain string (01,02,etc)
    fluxtime = datetime object of the current time to process
    wrfdom = dictionary containing information about the specified WRF domain    
    """


    auxName = auxName.replace("<domain>", dom)
    auxName = auxName.replace("<date>", fluxtime.strftime("%Y-%m-%d_%H:%M:%S"))
    outfname = RunDir + "/" + auxName
    #dataout = nc.Dataset(outfname,"w",format="NETCDF4_CLASSIC")
    dataout = nc.Dataset(outfname, "w", format = "NETCDF3_64BIT_OFFSET")
    #### time and spatial dimensions
    timeout = dataout.createDimension("Time", None)
    StrLength = dataout.createDimension("StrLength", 19)
    lat2 = dataout.createDimension("latitude", len(wrfdom["latwrf"][:,0]))
    lon2 = dataout.createDimension("longitude", len(wrfdom["latwrf"][0]))
    ez = dataout.createDimension("emissions_zdim",1)
    times = dataout.createVariable("Times", "S1", ("Time", "StrLength"))
    vars ={}

    for varName in INPUT_dic:
        vars[varName] = dataout.createVariable(INPUT_dic[varName]["FluxName"], "f4", ("Time", "emissions_zdim", "latitude", "longitude"))
        vars[varName].setncattr("Sector","PMCH")
        vars[varName].setncattr("FieldType", 104)
        vars[varName].units = "mol/km^2/hr"

    vars["Times"] = times
    #### global attributes
    dataout.setncattr("MMINLU", "USGS")
    dataout.setncattr("NUM_LAND_CAT", 24)
    
    return dataout, vars


def _make_emission_aFile(args):
    RunDir, dom, fluxtimeList, wrfdom, inputType, auxName = args
    print("Processing " + fluxtimeList[0].strftime("%Y-%m-%d %H:%M:%S") + " on domain " + dom)
    dataout, vars = init_file(RunDir, dom, fluxtimeList[0], wrfdom, inputType, auxName)
    for fluxframes, fluxtime in enumerate(fluxtimeList):
        for varName in INPUT_dic:
            #print("--> varName = " + varName)
            FluxType = INPUT_dic[varName]["input"]
            input_kwargs = INPUT_dic[varName]["input_kwargs"]
            offset = INPUT_dic[varName]["offset"]
            scale = INPUT_dic[varName]["scale"]
            flux = process(inputType, FluxType, fluxtime, wrfdom, input_kwargs, offsetList = offset, scaleList = scale)
            vars[varName][fluxframes] = flux

        vars["Times"][fluxframes] = list(fluxtime.strftime("%Y-%m-%d_%H:%M:%S"))

    dataout.close()

def _link_emission_aFile(args):
    RunDir, dom, fluxtimeList, wrfdom, inputType, auxName = args
    print("Linking " + fluxtimeList[0].strftime("%Y-%m-%d %H:%M:%S") + " on domain " + dom)
    auxName = auxName.replace("<domain>", dom)
    auxName = auxName.replace("<date>", fluxtimeList[0].strftime("%Y-%m-%d_%H:%M:%S"))
    origfname = origDir + "/" + auxName
    linkfname = RunDir + "/" + auxName
    assert os.path.exists(origfname), origfname + " can't be found."
    os.system("ln -sf " + origfname + " " + linkfname)



#starttime = INPUT_dic

def make_emissions(inputType, RunDir, isLink):
    global starttime, endtime
    """
    make_emissions(EmissDir,RunDir)

    main function to call to generate emissions for WRF-Chem
    
    EmissDir - string of path to root emissions directory
    RunDir - string of path to WRF working directory
    """
    #print(namelistFile)
    inputType = inputType.upper()
    assert inputType in ["FFE", "FTA"]

    #inventories = EmissType.strip().split("/")
    #### get a list of domains to process emissions for       
    geofiles = glob.glob(geoDir + "/geo_em*")
    #### parse the namelist for start/end/interval etc
    nml = f90nml.read(namelistFile)
    nmltime = nml["time_control"]
    ndoms = nml["domains"]["max_dom"]
    assert ndoms <= len(geofiles), "The max_dom in namelist is " + str(ndoms) + ", but there are (is) " + str(len(geofiles)) +" geo_em* file(s)."

    if runType == "online":
        # start of cycle
        starttime = "%04d%02d%02d%02d" % (nmltime["start_year"][0],nmltime["start_month"][0],nmltime["start_day"][0],nmltime["start_hour"][0])
        starttime = dt.datetime.strptime(starttime,"%Y%m%d%H")
        # end of cycle
        endtime = "%04d%02d%02d%02d" % (nmltime["end_year"][0],nmltime["end_month"][0],nmltime["end_day"][0],nmltime["end_hour"][0])
        endtime = dt.datetime.strptime(endtime,"%Y%m%d%H")
    # emissions data interval for WRF
    auxName = nmltime["auxinput" + str(auxID) + "_inname"]
    auxintList = nmltime["auxinput" + str(auxID) + "_interval_m"]
    if not isinstance(auxintList, list):
        auxintList = [auxintList]
    # number of frames in the file
    auxframesList = nmltime["frames_per_auxinput" + str(auxID)]
    if not isinstance(auxframesList, list):
        auxframesList = [auxframesList]

    ##### loop through each domain

    parallelArgs = []
    for idom in range(ndoms):
    #for geofname in geofiles:
        geofname = geofiles[idom]
        # get domain number
        domain = geofname[-5:]
        dom = domain[0:2]
        domID = int(dom)
        auxint = auxintList[domID - 1]
        auxframes = auxframesList[domID - 1]
        #print("Processing domain: ", dom)
        # read in input geogrid file
        geofile = nc.Dataset(geofname,"r")
        # get domain info from Geogrid file
        latwrf = geofile.variables["XLAT_M"][0].filled(np.nan)
        lonwrf = geofile.variables["XLONG_M"][0].filled(np.nan)
        # get the four corners of the domain
        lat_s = latwrf[0,0];lat_n = latwrf[-1,-1]
        lon_w = lonwrf[0,0];lon_e = lonwrf[-1,-1]
        latList = latwrf[:, 0]
        lonList = lonwrf[0, :]
        # get the resolution in degrees
        #dlat = (lat_n - lat_s)/len(latwrf[0,:])
        #dlon = (lon_e - lon_w)/len(lonwrf[:,0])
        nLat, nLon = latwrf.shape
        dLon = np.mean((lonList[1:] - lonList[:-1]))
        dLat = np.mean((latList[1:] - latList[:-1]))
        wrfdom = {"latwrf": latwrf, "lonwrf": lonwrf, "lat_s": lat_s, "lat_n": lat_n, "lon_w": lon_w, "lon_e": lon_e, "dLon": dLon, "dLat": dLat, "dom": dom}

        fluxtime = starttime
# open the first output file
        #dataout, vars = init_file(RunDir,dom,ndoms,fluxtime,wrfdom)
        #dataout, vars = init_file(RunDir, dom, fluxtime, wrfdom, inputType)
        fluxframes = 1
        fluxtimeList = []
        ##### loop through times to process
        while fluxtime <= endtime:

            #print("Processing: ", fluxtime.strftime("%Y-%m-%d_%H:%M:%S"))
            if fluxframes > int(auxframes):
                #dataout.close()
                #dataout, vars = init_file(RunDir,dom,ndoms,fluxtime,wrfdom)
                #dataout, vars = init_file(RunDir, dom, fluxtime, wrfdom, inputType)
                #print(dom, fluxtimeList)
                parallelArgs.append((RunDir, dom, fluxtimeList, wrfdom, inputType, auxName))
                fluxframes = 1
                fluxtimeList = []

            """
            for varName in INPUT_dic:
                print("--> varName = " + varName)
                FluxType = INPUT_dic[varName]["input"]
                input_kwargs = INPUT_dic[varName]["input_kwargs"]
                offset = INPUT_dic[varName]["offset"]
                scale = INPUT_dic[varName]["scale"]
                flux = process(inputType, FluxType, fluxtime, wrfdom, input_kwargs, offsetList = offset, scaleList = scale)
                vars[varName][fluxframes - 1] = flux

            vars["Times"][fluxframes - 1] = list(fluxtime.strftime("%Y-%m-%d_%H:%M:%S"))
            """
            fluxtimeList.append(fluxtime)
            fluxframes = fluxframes + 1
            fluxtime = fluxtime + dt.timedelta(minutes = int(auxint))
        #print(dom, fluxtimeList)
        parallelArgs.append((RunDir, dom, fluxtimeList, wrfdom, inputType, auxName))

    if isLink:
        for args in parallelArgs:
            _link_emission_aFile(args)
    else:
        if nCores == 1:
            for args in parallelArgs:
                _make_emission_aFile(args)
        else:
            pool = mtp.Pool(nCores)
            pool.map(_make_emission_aFile, parallelArgs)
            pool.close()
            pool.join()

if __name__ == "__main__":
    make_emissions(inputType, RunDir, isLink)



