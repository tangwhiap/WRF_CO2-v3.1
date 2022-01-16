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
    
"""
import datetime as dt
import numpy as np
import netCDF4 as nc
import sys
import f90nml
from process import process
#from API_code import *
import glob

#inventories = ['FFDAS']#,'Vulcan','EDGAR','ODIAC','CH4EPA'] # list of inventories to include
fluxvar = "E_CO2_FFE" #,'E_CO2_VULCAN','E_CO2_EDGAR','E_CO2_ODIAC','E_CH4_EPA'] # to intialize the output file 

def init_file(RunDir,dom,ndoms,fluxtime,wrfdom):
    """
    init_file(RunDir,dom,fluxtime,wrfdom)
    
    function to initialize a new netCDF emissions input file

    RunDir = directory to run WRF in / output flux file
    dom = domain string (01,02,etc)
    fluxtime = datetime object of the current time to process
    wrfdom = dictionary containing information about the specified WRF domain    
    """
    outfname = RunDir+'/wrfchemi_d'+dom+'_'+fluxtime.strftime('%Y-%m-%d_%H:00:00')
    #dataout = nc.Dataset(outfname,'w',format='NETCDF4_CLASSIC')
    dataout = nc.Dataset(outfname,'w',format='NETCDF3_64BIT_OFFSET')
    #### time and spatial dimensions
    timeout = dataout.createDimension("Time", None)
    StrLength = dataout.createDimension("StrLength", 19)
    lat2 = dataout.createDimension("latitude", len(wrfdom['latwrf'][:,0]))
    lon2 = dataout.createDimension("longitude", len(wrfdom['latwrf'][0]))
    ez = dataout.createDimension("emissions_zdim",1)
    times = dataout.createVariable("Times", "S1", ("Time","StrLength"))
    vars ={}
    # loop through variables to create
    #for a in range(len(fluxvars)):
        #fluxvar = fluxvars[a]
        #inv = inventories[a]
        #exec(inv+'out = dataout.createVariable("'+fluxvar+'","f4",("Time","emissions_zdim","latitude","longitude"))')
        #exec(inv+'out.setncattr("Sector","PMCH")')
        #exec(inv+'out.setncattr("FieldType", 104)')
        #exec(inv+'out.units = "mol/km^2/hr"')
        #exec('vars["'+fluxvar+'"] = '+inv+'out')

    FFEout = dataout.createVariable(fluxvar,"f4",("Time","emissions_zdim","latitude","longitude"))
    FFEout.setncattr("Sector","PMCH")
    FFEout.setncattr("FieldType", 104)
    FFEout.units = "mol/km^2/hr"
    vars[fluxvar] = FFEout

    for idom in range(1, ndoms + 1):
        FFEout = dataout.createVariable(fluxvar + str(idom),"f4",("Time","emissions_zdim","latitude","longitude"))
        FFEout.setncattr("Sector","PMCH")
        FFEout.setncattr("FieldType", 104)
        FFEout.units = "mol/km^2/hr"
        vars[fluxvar + str(idom)] = FFEout
    vars['Times'] = times
    #### global attributes
    dataout.setncattr("MMINLU", "USGS")
    dataout.setncattr("NUM_LAND_CAT",24)
    
    return dataout, vars

def make_emissions(EmissType, RunDir):
    """
    make_emissions(EmissDir,RunDir)

    main function to call to generate emissions for WRF-Chem
    
    EmissDir - string of path to root emissions directory
    RunDir - string of path to WRF working directory
    """

    inventories = EmissType.strip().split("/")
    #### get a list of domains to process emissions for       
    geofiles = glob.glob(RunDir+'/geo_em*')
    #### parse the namelist for start/end/interval etc
    nml = f90nml.read(RunDir+'/namelist.input')
    nmltime = nml['time_control']
    ndoms = nml["domains"]["max_dom"]
    assert ndoms == len(geofiles), "The max_dom in namelist is " + str(ndoms) + ", but there are (is) " + str(len(geofiles)) +" geo_em* file(s)."
    # start of cycle
    starttime = "%04d%02d%02d%02d" % (nmltime['start_year'][0],nmltime['start_month'][0],nmltime['start_day'][0],nmltime['start_hour'][0])
    starttime = dt.datetime.strptime(starttime,"%Y%m%d%H")
    # end of cycle
    endtime = "%04d%02d%02d%02d" % (nmltime['end_year'][0],nmltime['end_month'][0],nmltime['end_day'][0],nmltime['end_hour'][0])
    endtime = dt.datetime.strptime(endtime,"%Y%m%d%H")
    # emissions data interval for WRF
    aux5int = nmltime['auxinput5_interval_m'][0]
    # number of frames in the file
    aux5frames = nmltime['frames_per_auxinput5'][0]

    ##### loop through each domain
    for geofname in geofiles:
        # get domain number
        domain = geofname[-5:]
        dom = domain[0:2]
        print("Processing domain: ", dom)
        # read in input geogrid file
        geofile = nc.Dataset(geofname,'r')
        # get domain info from Geogrid file
        latwrf = geofile.variables['XLAT_M'][0]
        lonwrf = geofile.variables['XLONG_M'][0]
        # get the four corners of the domain
        lat_s = latwrf[0,0];lat_n = latwrf[-1,-1]
        lon_w = lonwrf[0,0];lon_e = lonwrf[-1,-1]
        # get the resolution in degrees
        res = (lat_n - lat_s)/len(latwrf[0,:])
        wrfdom = {'latwrf':latwrf,'lonwrf':lonwrf,'lat_s':lat_s,'lat_n':lat_n,'lon_w':lon_w,'lon_e':lon_e,'res':res,'dom':dom}

        fluxtime = starttime
# open the first output file
        dataout, vars = init_file(RunDir,dom,ndoms,fluxtime,wrfdom)
        fluxframes = 1

        ##### loop through times to process
        while fluxtime <= endtime:
            print("Processing: ", fluxtime.strftime("%Y-%m-%d_%H:%M:%S"))
            if fluxframes > int(aux5frames):
                fluxframes = 1
                dataout.close()
                dataout, vars = init_file(RunDir,dom,ndoms,fluxtime,wrfdom)
            #for a in range(len(fluxvars)):
                # modified by TangWenhan
                #loc = locals()
                #exec('flux = '+inventories[a]+'.process(EmissDir,fluxtime,wrfdom)')
            flux = process(EmissType,  fluxtime, wrfdom)
                #flux = loc["flux"]
                # === end ===
            vars[fluxvar][fluxframes-1] = flux
            for idom in range(1, ndoms + 1):
                vars[fluxvar + str(idom)][fluxframes-1] = flux * (1 if idom == int(dom) else 0)
            vars['Times'][fluxframes-1] = list(fluxtime.strftime('%Y-%m-%d_%H:%M:%S'))
            fluxframes = fluxframes + 1
            fluxtime = fluxtime + dt.timedelta(minutes=int(aux5int))


#### if script is called from the command line
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('wrong usage:')
        print(sys.argv[0]+'EmissType RunDir')
        sys.exit()
    EmissType = sys.argv[1]
    RunDir = sys.argv[2]
    make_emissions(EmissType,  RunDir)
