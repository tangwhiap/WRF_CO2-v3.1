#!/usr/bin/env python
import datetime as dtm
from datetime import datetime
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from pdb import set_trace

UserDefined_interpolate = False
interpolate_method = "linear"

def interface(Time,DataDir,wrfdom):

    # domain configure
    nlon = 144
    nlat = 72
    glons = np.linspace(1.25, 360-1.25, nlon)
    glats = np.linspace(-90+1.25, 90-1.25, nlat)

    # Convert longitude range to -180 ~ 180
    glons = ((glons+180)%360)-180
    DataDir = DataDir.strip().split(":")
    infile = DataDir[0].strip() + "/%4d%02d" % (Time.year, Time.month) + ".CFtaS"
    gcfta = np.fromfile(infile, dtype = "float32")
    Nrec = len(gcfta)
    Ndays = int(Nrec/nlon/nlat)
    gcfta = gcfta.reshape(Ndays, nlat, nlon)
    gcfta = gcfta[Time.day - 1, :, :]


    ## convert CFta units from KgC/m2/sec to mol/km2/hr for WRF
    gcfta = gcfta*1000./12.*1000000.*3600. ## 1000g/kg, 12g/mol, 1e6 m2/km2, 3600 sec/hr

    glons,glats=np.meshgrid(glons,glats)
    return {"lon" : glons.flatten(), "lat" : glats.flatten(), "value" : gcfta.flatten()}


