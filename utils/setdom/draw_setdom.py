#!/usr/bin/env python
# Authors:
#  Wenhan TANG - 02/2021
#  ...

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import sys
import os

DomConfig = sys.argv[1]
#IsDrawStation = sys.argv[2]
#if IsDrawStation.lower() == "true":
#    IsDrawStation = True
#else:
#    IsDrawStation = False
#StaConfig = sys.argv[2]

SHP  = "/home/tangwh/datasets/china_shp"
margL = 1


def draw_rec(geo_ax, domain, DomName = None):
    lon_s = domain[0]
    lon_e = domain[1]
    lat_s = domain[2]
    lat_e = domain[3]
    x = [lon_s, lon_e, lon_e, lon_s, lon_s]
    y = [lat_s, lat_s, lat_e, lat_e, lat_s]
    #geo_ax.plot(x, y, marker = "o", transform = ccrs.PlateCarree())
    geo_ax.plot(x, y, transform = ccrs.PlateCarree())
    if DomName != None:
        geodetic_transform = ccrs.Geodetic()._as_mpl_transform(geo_ax)
        text_transform = offset_copy(geodetic_transform, units = "dots", x = +8)
        text_transform = offset_copy(geodetic_transform, units = "dots", y = -8)
        geo_ax.text(lon_s, lat_e, DomName, fontsize = 16, verticalalignment = "top", horizontalalignment = "left", transform = text_transform)



def draw_domain(DomConfig, StationsDic = {}, StaName = True, Savefig = None):
    fig = plt.figure(figsize = (11, 8))
    geo_ax = fig.add_subplot(1,1,1, projection = ccrs.PlateCarree())

    geo_ax.add_geometries(Reader(os.path.join(SHP, 'cnhimap.shp')).geometries(), ccrs.Geodetic() ,facecolor='none',edgecolor='k',linewidth=1)
    geo_ax.set_xticks(np.arange(-180, 180+2, 2), crs = ccrs.PlateCarree())
    geo_ax.set_yticks(np.arange(-85, 85+2, 2), crs = ccrs.PlateCarree())
    geo_ax.xaxis.set_major_formatter(LongitudeFormatter())
    geo_ax.yaxis.set_major_formatter(LatitudeFormatter())

    fin = open(DomConfig)
    line_list = []
    for iline in enumerate(fin):
        line_list.append(iline)
    fin.close()
    
    for ind, line in line_list:
        domain = line.strip().split(",")
        domain = list(map(float, domain))
        if ind == 0:
            marg = [domain[0] - margL, domain[1] + margL, domain[2] - margL, domain[3] + margL]
            geo_ax.set_extent(marg, crs = ccrs.PlateCarree())
            DomName = "d" + str(ind + 1).zfill(2)
            draw_rec(geo_ax, domain, DomName)
        else:
            DomName = "d" + str(ind + 1).zfill(2)
            draw_rec(geo_ax, domain, DomName)
    geo_ax.gridlines()
    for Name in StationsDic:
        sta_lon = StationsDic[Name][0]
        sta_lat = StationsDic[Name][1]
        geo_ax.plot(sta_lon, sta_lat, marker = "o", color = "red", markersize = 4, alpha = 0.7, transform = ccrs.Geodetic())
        if StaName:
            geodetic_transform = ccrs.Geodetic()._as_mpl_transform(geo_ax)
            text_transform = offset_copy(geodetic_transform, units = "dots", y = -8)
            geo_ax.text(sta_lon, sta_lat, Name, fontsize = 8, verticalalignment = "top", horizontalalignment = "center", transform = text_transform, bbox = {"facecolor": "sandybrown", "alpha": 0.5, "boxstyle": "round"})

    geo_ax.set_title("WRF-CO2 domain (Stagger)")
    if Savefig == None:
        plt.show()
    else:
        plt.savefig(Savefig)

if __name__ == "__main__":
    draw_domain(DomConfig)

