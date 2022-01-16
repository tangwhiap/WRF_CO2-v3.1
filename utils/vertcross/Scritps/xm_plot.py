#!/usr/bin/env python
import numpy as np
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.pyplot import MultipleLocator
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from matplotlib.colors import ListedColormap
from owslib.wmts import WebMapTileService
import datetime as dtm
from pdb import set_trace
from section_import_point import sip_dic
from matplotlib.ticker import FuncFormatter
import matplotlib.ticker as mticker
mpl.use("Agg")

ShpDir = "/home/tangwh/datasets/china_shp/cnhimap.shp"
URL = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi'
layer = "BlueMarble_NextGeneration"
wmts = WebMapTileService(URL)


str_StartDT = "2021-01-03_00:00:00"
str_EndDT = "2021-01-26_00:00:00"
#str_EndDT = "2021-01-03_00:00:00"
#str_EndDT = "2018-12-01_00:00:00"
dtMins = 15
Domid = 1
FileName = "wrfvtc_d01_2021-01-03_00:00:00"
DataDir_vtc = "../output"
DataDir_co2 = "../data/1"
DataDir_xco2 = "../data/1xco2"
PlotDir = "../plot3"
z_top = 2000
VarPlot = "CO2_TOT"
UTC = +8

# CO2_TOT
#vmin_sec = 350
#vmax_sec = 650

# CO2_FFE_INDUSP
vmin_sec = 350
vmax_sec = 600

vmin_sur = 400
vmax_sur = 600

vmin_xco2 = 400
vmax_xco2 = 410

section = "BJ_TJ"
#section = "BH"
#section = "N397"
N_loc_visable = 8

Start = dtm.datetime.strptime(str_StartDT, "%Y-%m-%d_%H:%M:%S")
End = dtm.datetime.strptime(str_EndDT, "%Y-%m-%d_%H:%M:%S")
dt = dtm.timedelta(minutes = dtMins)
dt_UTC = dtm.timedelta(hours = UTC)
point_dic = sip_dic[section]

def alpha_vary_cmap(colormap):
    cmap = plt.get_cmap(colormap)
    my_cmap = cmap(np.arange(cmap.N))
    my_cmap[:,-1] = np.linspace(0, 1, cmap.N)
    my_cmap = ListedColormap(my_cmap)
    return my_cmap

def draw_2D(fig, ax, proj, co2, lon, lat, title = None, uv_dic = None, uv_set = None, vmin = 400, vmax = 700, cbar_orn = "vertical", sections_dic = None):
    
    assert co2.shape == lon.shape
    assert lon.shape == lat.shape

    if uv_dic != None:
        u = uv_dic["U"]
        v = uv_dic["V"]
        assert u.shape == lat.shape
        assert v.shape == u.shape
        if uv_set == None:
            uv_set = {}
        if "xint" not in uv_set:
            uv_set["xint"] = 1
        if "yint" not in uv_set:
            uv_set["yint"] = 1
        if "windcolor" not in uv_set:
            uv_set["windcolor"] = "black"
        if "scale" not in uv_set:
            uv_set["scale"] = 150
        if "width" not in uv_set:
            uv_set["width"] = 0.002

    lon_s = lon[0,0]
    lon_e = lon[0,-1]
    lat_s = lat[0,0]
    lat_e = lat[-1,0]

    lon_s = 113
    lon_e = 120
    #proj = ccrs.PlateCarree()
    #fig = plt.figure()
    #ax = fig.add_subplot(1, 1, 1, projection = proj)
    ax.add_wmts(wmts, layer)
    ax.add_geometries( Reader(ShpDir).geometries(), proj, facecolor = "none", edgecolor = "k", linewidth = 2)
    ax.set_extent([lon_s, lon_e, lat_s, lat_e], crs = proj)
    gl = ax.gridlines(crs = proj, linestyle = "--", alpha = 0.5, draw_labels = True)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style={'size':20}
    gl.ylabel_style={'size':20}
    #gl.xpadding = 2
    #gl.ypadding = 1
    gl.xlocator=mticker.FixedLocator(np.arange(-180, 180, 2))
    gl.ylocator=mticker.FixedLocator(np.arange(-90, 90, 2)) 
    levels = np.linspace(vmin, vmax, 100)
    cbar_levels = np.arange(400, 601, 50)
    #cmap = alpha_vary_cmap("YlOrRd")
    #cmap = alpha_vary_cmap("rainbow")
    cmap = alpha_vary_cmap("jet")
    cs = ax.contourf(lon, lat, co2, transform = proj, levels = levels, cmap = cmap, extend = "max", antialiased = True)
    comma_fmt = FuncFormatter(lambda x, p: format(int(x)))
    cbar = fig.colorbar(cs, orientation = cbar_orn, format = comma_fmt, ticks = cbar_levels)
    cbar.ax.tick_params(labelsize = 16)
    cbar.set_label("ppm", fontsize = 20)

    if uv_dic != None:
        ax.quiver( lon[::uv_set["yint"],::uv_set["xint"]], lat[::uv_set["yint"],::uv_set["xint"]], u[::uv_set["yint"],::uv_set["xint"]], v[::uv_set["yint"],::uv_set["xint"]], color = uv_set["windcolor"], scale = uv_set["scale"], width = uv_set["width"], zorder = 2)
    if sections_dic != None:
        for sector in sections_dic:
            start_point = sections_dic[sector]["start"]
            end_point = sections_dic[sector]["end"]
            line_color = sections_dic[sector]["color"]
            ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], transform = proj, color = line_color, linewidth = 2)
    #fig.suptitle(title)
    #ax.tick_params(axis='both', which='major', labelsize=20)
    ax.set_title(title)
    #plt.savefig(SaveName)
    #plt.close(fig)
        
ds_vtc = xr.open_dataset(DataDir_vtc + "/" + FileName)
Current = Start

sections_dic = {}
crosslon = ds_vtc["crosslon_" + section].values
crosslat = ds_vtc["crosslat_" + section].values
sections_dic[section] = {"start": (crosslon[0], crosslat[0]), "end": (crosslon[-1], crosslat[-1]), "color": "red"}
for point in point_dic:
    plon = point_dic[point][0]
    plat = point_dic[point][1]
    pName = point_dic[point][2]
    dislist = (crosslon - plon) **2 + (crosslat - plat) ** 2
    iloc = int( np.where( dislist == dislist.min() )[0] )
    point_dic[point] = (plon, plat, pName, iloc)

while(Current <= End):
    print("Drawing ", Current.strftime("%Y-%m-%d_%H:%M:%S"))
    fig = plt.figure(figsize = (20, 14))
    #ax = fig.add_subplot(1,1,1)
    ax = plt.subplot2grid((3,4), (2,0), rowspan = 1, colspan = 4, fig = fig)
    z_spec = ds_vtc.z_spec.values
    z_sel = z_spec[ (z_spec <= z_top) ]
    data = ds_vtc["VTC_z_" + section].sel(time = np.datetime64(Current), VarName = VarPlot.encode("UTF-8"), z_spec = z_sel)
    surface_z = ds_vtc["Surface_z_" + section].sel(time = np.datetime64(Current)).values
    PBLH = ds_vtc["PBLH_" + section].sel(time = np.datetime64(Current)).values
    levels = np.linspace(vmin_sec, vmax_sec, 100)
    cbar_levels = np.arange(350, 601, 50)
    cmap = alpha_vary_cmap("jet")
    lonlat = ["(%.2fE, %.2fN)" % (lon,lat) for lon, lat in zip(ds_vtc["crosslon_" + section].values, ds_vtc["crosslat_" + section].values)]
    #lonlat = [" " for i in range(len(crosslon))]
    cs = ax.contourf(lonlat, z_sel, data, levels = levels, cmap = cmap, extend = "max", antialiased = True)
    ax.set_ylim([z_sel[0], z_sel[-1]])
    comma_fmt = FuncFormatter(lambda x, p: format(int(x)))
    cbar = fig.colorbar(cs, format = comma_fmt, ticks = cbar_levels)
    cbar.ax.tick_params(labelsize = 16)
    cbar.set_label("ppm", fontsize = 20)
    ax.plot(lonlat, surface_z, color = "black", linewidth = 3, alpha = 0.5)
    ax.plot(lonlat, PBLH, color = "blue", linestyle = "--", linewidth = 2, alpha = 0.4)
    
    #print(PBLH-surface_z)
    #ax.xaxis.set_major_locator(MultipleLocator(len(lonlat) // N_loc_visable))
    #ax.set_xticklabels(labels = lonlat, rotation = 30)
    hs, he = ax.get_ylim()
    for point in point_dic:
        pName = point_dic[point][2]
        iloc = point_dic[point][3]
        height = surface_z[iloc]
        y_percent = (height - hs) / (he - hs)
        x_percent = iloc / len(crosslon)
        #ax.text(x_percent, y_percent - 0.01, pName, horizontalalignment = "center", verticalalignment = "top", transform = ax.transAxes, fontsize = 20, alpha = 0.5, color = "red")
        ax.annotate(pName, xy = (x_percent, y_percent), xycoords = "axes fraction", xytext = (x_percent, y_percent - 0.15), textcoords = "axes fraction", arrowprops = {"facecolor": "red", "shrink": 0.05}, fontsize = 20)

    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.set_ylabel("Altitude (m)", fontsize = 20)
    ax.set_xticks([])
    #ax.set_title("Section")

    proj = ccrs.PlateCarree()

    ax2 = plt.subplot2grid((3,4), (0,1), rowspan = 2, colspan = 2, fig = fig, projection = proj)
    ds_co2 = xr.open_dataset(DataDir_co2 + "/wrfco2_d" + str(Domid).zfill(2) + "_" + Current.strftime("%Y-%m-%d_%H:%M:%S"))
    co2 = ds_co2.variables[VarPlot][0,0].values
    u = ds_co2["U10"][0].values
    v = ds_co2["V10"][0].values
    lon = ds_co2["XLONG"][0].values
    lat = ds_co2["XLAT"][0].values
    draw_2D(fig, ax2, proj, co2, lon, lat, title = None, uv_dic = {"U": u, "V": v}, uv_set = {"xint": 10, "yint": 10, "windcolor": "white"}, vmin = vmin_sur, vmax = vmax_sur, cbar_orn = "vertical", sections_dic = sections_dic)

    '''
    ax3 = plt.subplot2grid((3,4), (0,2), rowspan = 2, colspan = 2, fig = fig, projection = proj)
    ds_xco2 = xr.open_dataset(DataDir_xco2 + "/wrfxco2_d" + str(Domid).zfill(2) + "_" + Current.strftime("%Y-%m-%d_%H:%M:%S"))
    xco2 = ds_xco2[VarPlot][0].values
    #u = ds_co2["U10"][0].values
    #v = ds_co2["V10"][0].values
    lon = ds_xco2["lon"].values
    lat = ds_xco2["lat"].values
    lon, lat = np.meshgrid(lon, lat)
    draw_2D(fig, ax3, proj, xco2, lon, lat, title = "XCO2", vmin = vmin_xco2, vmax = vmax_xco2, cbar_orn = "vertical", sections_dic = sections_dic)
    '''

#    sup_title = section + " - " + VarPlot + "\n" + Current.strftime("%Y-%m-%d_%H:%M:%S") + " UTC\n" + (Current + dt_UTC).strftime("%Y-%m-%d_%H:%M:%S") + " LST"
    #sup_title = section + " - " + VarPlot + "\n" + (Current + dt_UTC).strftime("%Y-%m-%d_%H:%M:%S") + " LST"
    sup_title = (Current + dt_UTC).strftime("%Y-%m-%d %H:%M:%S")
    fig.suptitle(sup_title, y = 0.91, fontsize = 28)
    #plt.show()
    plt.savefig(PlotDir + "/vtc2_" + section + "_" + VarPlot + "_" + Current.strftime("%Y-%m-%d_%H:%M:%S") + ".png", dpi = 200)
    plt.close(fig)
    Current += dt

