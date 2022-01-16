#!/usr/bin/env python
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.pyplot import MultipleLocator
import datetime as dtm

str_StartDT = "2018-12-01_00:00:00"
#str_EndDT = "2018-12-14_00:00:00"
str_EndDT = "2018-12-01_00:01:00"
dtMins = 15
FileName = "wrfvtc_d02_2018-12-01_00:00:00"
DataDir = "../output"
PlotDir = "../plot"
z_top = 2000
VarPlot = "CO2_TOT"
vmin = 350
vmax = 650
section = "BJ_TJ"
#section = "BH"
N_loc_visable = 8

Start = dtm.datetime.strptime(str_StartDT, "%Y-%m-%d_%H:%M:%S")
End = dtm.datetime.strptime(str_EndDT, "%Y-%m-%d_%H:%M:%S")
dt = dtm.timedelta(minutes = dtMins)

def alpha_vary_cmap(colormap):
    cmap = plt.get_cmap(colormap)
    my_cmap = cmap(np.arange(cmap.N))
    my_cmap[:,-1] = np.linspace(0, 1, cmap.N)
    my_cmap = ListedColormap(my_cmap)
    return my_cmap

ds = xr.open_dataset(DataDir + "/" + FileName)
Current = Start
while(Current <= End):
    print("Drawing ", Current.strftime("%Y-%m-%d_%H:%M:%S"))
    fig = plt.figure(figsize = (20, 7))
    ax = fig.add_subplot(1,1,1)
    z_spec = ds.z_spec.values
    z_sel = z_spec[ (z_spec <= z_top) ]
    data = ds["VTC_z_" + section].sel(time = np.datetime64(Current), VarName = VarPlot.encode("UTF-8"), z_spec = z_sel)
    surface_z = ds["Surface_z_" + section].sel(time = np.datetime64(Current)).values
    PBLH = ds["PBLH_" + section].sel(time = np.datetime64(Current)).values
    levels = np.linspace(vmin, vmax, 100)
    cmap = alpha_vary_cmap("jet")
    lonlat = ["(%.2fE, %.2fN)" % (lon,lat) for lon, lat in zip(ds["crosslon_" + section].values, ds["crosslat_" + section].values)]
    cs = ax.contourf(lonlat, z_sel, data, levels = levels, cmap = cmap, extend = "max", antialiased = True)
    cbar = fig.colorbar(cs)
    ax.plot(lonlat, surface_z, color = "black", linewidth = 3, alpha = 0.5)
    ax.plot(lonlat, PBLH, color = "blue", linestyle = "--", linewidth = 2, alpha = 0.4)
    print(PBLH-surface_z)
    ax.xaxis.set_major_locator(MultipleLocator(len(lonlat) // N_loc_visable))
    ax.set_xticklabels(labels = lonlat, rotation = 30)
    ax.set_ylabel("Altitude (m)")
    #ax.xaxis.set_visible(False)
    #ax_lon = ax.twinx()
    #ax_lon.plot(ds["crosslon_" + section].values, ds["crosslon_" + section].values * np.nan)
    #ax_lon.xaxis.set_visible(False)
    #ax_lon.set_xlabel("longitude")
    #plt.show()
    fig.suptitle(section + " " + VarPlot + "\n" + Current.strftime("%Y-%m-%d_%H:%M:%S") + " UTC")
    plt.savefig(PlotDir + "/vtc_" + section + "_" + VarPlot + "_" + Current.strftime("%Y-%m-%d_%H:%M:%S") + ".png")
    Current += dt

