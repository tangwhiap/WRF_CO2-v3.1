#!/usr/bin/env python
# Write CTL files for WRF output in lat-lon grids
# Authors:
# TangWenhan - 8/2020 (Original Version)
# ...

import xarray as xr
import os
import sys
import f90nml as nml

#argv from WRF-CO2_ofl.sh
WrfoutDir = sys.argv[1] # Directory of wrf output files
WrfctlDir = sys.argv[2] # Directory of namelist.input
CtlDir = WrfoutDir      # Directory prepared for CTL files
#CtlDir=sys.argv[2] # Directory prepared for CTL files

# Global Setting
#PDir="/home/tangwh/modeling/wrf2bin" # Parrent Directory
#WrfoutDir=PDir+"/data2" # Directory of wrf output files
#CtlDir=PDir+"/ctloutput2" # Directory prepared for CTL files
nmlf = nml.read(WrfctlDir + "/namelist.input")
max_dom = nmlf["domains"]["max_dom"]
interval = nmlf["time_control"]["auxhist23_interval"]
#domains=["d01","d02","d03"] # Domains set in wrf
#Dt_each_dom={"d01":"30mn","d02":"15mn","d03":"15mn"} # time intervals for each domain
domains = ["d" + str(idom).zfill(2) for idom in range(1, max_dom + 1)]
Dt_each_dom = {}
for i, idom in enumerate(domains):
    Dt_each_dom[idom] = str(interval[i]) + "mn"


def d_array(array,integer=False):
    #compute dx, dy, dz ...
    d=(array[1:]-array[:-1]).mean()
    if integer:
        d=int(d)
    return d

def month_num2str(mon):
    m3_dict={"01":"JAN","02":"FEB","03":"MAR","04":"APR","05":"MAY","06":"JUN","07":"JUL","08":"AUG","09":"SEP","10":"OCT","11":"NOV","12":"DEC"}
    return m3_dict[mon]

def datetime_filename2grads(filename):
    #extract datetime information from wrfout files name, convert into grads standard datetime format.
    fn_list=filename.split("_")
    date=fn_list[2].split("-")
    time=fn_list[3].split(":")
    year=date[0]
    mon=month_num2str(date[1])
    day=date[2]
    hour=time[0]
    minute=time[1]
    return hour+":"+minute+"Z"+day+mon+year
    
def ctl_center(wrfoutdir,ctldir,dom,nx,xs,dx,ny,ys,dy,nz,zs,ds,nt,ts,dt):
    #write ctl files for physical variables in center grid
    f=open(ctldir+"/wrfco2_"+dom+"_center.ctl","w")
    f.write("dset ^wrfco2_"+dom+"_%y4-%m2-%d2_%h2:%n2:00\n")
    f.write("dtype netcdf\n")
    f.write("options template\n")
    f.write("undef -888\n")
    f.write("TITLE WRF Output Grid: Time, bottom_top, south_north, west_east\n")
    f.write("xdef "+str(nx)+" linear "+str(xs)+" "+str(dx)+"\n")
    f.write("ydef "+str(ny)+" linear "+str(ys)+" "+str(dy)+"\n")
    f.write("zdef "+str(nz)+" linear "+str(zs)+" "+str(dz)+"\n")
    f.write("tdef "+str(nt)+" linear "+ts+" "+dt+"\n")
    f.write("vars 15\n")
    f.write("ZNU=>ZNU 38 t,z eta values on half (mass) levels\n") 
    f.write("T=>T 38 t,z,y,x perturbation potential temperature (theta-t0)\n") 
    f.write("P=>P 38 t,z,y,x perturbation pressure\n") 
    f.write("PB=>PB 38 t,z,y,x BASE STATE PRESSURE\n") 
    f.write("Q2=>Q2 1 t,y,x QV at 2 M\n") 
    f.write("T2=>T2 1 t,y,x TEMP at 2 M\n") 
    f.write("PSFC=>PSFC 1 t,y,x SFC PRESSURE\n") 
    f.write("U10=>U10 1 t,y,x U at 10 M\n") 
    f.write("V10=>V10 1 t,y,x V at 10 M\n") 
    f.write("HGT=>hgt   1  t,y,x    terrain height\n") 
    f.write("PBLH=>PBLH 1 t,y,x PBL HEIGHT\n") 
    f.write("CO2_BCK=>CO2_BCK 38 t,z,y,x mixing ratio of background CO2\n") 
    f.write("CO2_TOT=>CO2_TOT 38 t,z,y,x mixing ratio of CO2, total\n") 
    f.write("CO2_FFDAS=>CO2_FFDAS 38 t,z,y,x mixing ratio of CO2, FFDAS Anthropogenic "+dom+"\n") 
    f.write("CO2_VEGAS=>CO2_VEGAS 38 t,z,y,x mixing ratio of CO2, VEGAS bio fluxes "+dom+"\n") 
    f.write("endvars\n") 
    f.close()
    
def ctl_u(wrfoutdir,ctldir,dom,nx,xs,dx,ny,ys,dy,nz,zs,ds,nt,ts,dt):
    #write ctl files for the U variable (Time, bottom_top, south_north, west_east_stag)
    f=open(ctldir+"/wrfco2_"+dom+"_u.ctl","w")
    f.write("dset ^wrfco2_"+dom+"_%y4-%m2-%d2_%h2:%n2:00\n")
    f.write("dtype netcdf\n")
    f.write("options template\n")
    f.write("undef -888\n")
    f.write("TITLE WRF Output Grid: Time, bottom_top, south_north, west_east_stag\n")
    f.write("xdef "+str(nx)+" linear "+str(xs)+" "+str(dx)+"\n")
    f.write("ydef "+str(ny)+" linear "+str(ys)+" "+str(dy)+"\n")
    f.write("zdef "+str(nz)+" linear "+str(zs)+" "+str(dz)+"\n")
    f.write("tdef "+str(nt)+" linear "+ts+" "+dt+"\n")
    f.write("vars 1\n")
    f.write("U=>U 38 t,z,y,x x-wind component\n")
    f.write("endvars\n")
    f.close()
    
def ctl_v(wrfoutdir,ctldir,dom,nx,xs,dx,ny,ys,dy,nz,zs,ds,nt,ts,dt):
    #write ctl files for the V variable (Time, bottom_top, south_north_stag, west_east)
    f=open(ctldir+"/wrfco2_"+dom+"_v.ctl","w")
    f.write("dset ^wrfco2_"+dom+"_%y4-%m2-%d2_%h2:%n2:00\n")
    f.write("dtype netcdf\n")
    f.write("options template\n")
    f.write("undef -888\n")
    f.write("TITLE WRF Output Grid: Time, bottom_top, south_north_stag, west_east\n")
    f.write("xdef "+str(nx)+" linear "+str(xs)+" "+str(dx)+"\n")
    f.write("ydef "+str(ny)+" linear "+str(ys)+" "+str(dy)+"\n")
    f.write("zdef "+str(nz)+" linear "+str(zs)+" "+str(dz)+"\n")
    f.write("tdef "+str(nt)+" linear "+ts+" "+dt+"\n")
    f.write("vars 1\n")
    f.write("V=>V 38 t,z,y,x y-wind component\n")
    f.write("endvars\n")
    f.close()

def ctl_w(wrfoutdir,ctldir,dom,nx,xs,dx,ny,ys,dy,nz,zs,ds,nt,ts,dt):
    #write ctl files for the ZNW, W, PH, PHB variables (Time, bottom_top_stag, south_north, west_east)
    f=open(ctldir+"/wrfco2_"+dom+"_w.ctl","w")
    f.write("dset ^wrfco2_"+dom+"_%y4-%m2-%d2_%h2:%n2:00\n")
    f.write("dtype netcdf\n")
    f.write("options template\n")
    f.write("undef -888\n")
    f.write("TITLE WRF Output Grid: Time, bottom_top_stag, south_north, west_east\n")
    f.write("xdef "+str(nx)+" linear "+str(xs)+" "+str(dx)+"\n")
    f.write("ydef "+str(ny)+" linear "+str(ys)+" "+str(dy)+"\n")
    f.write("zdef "+str(nz)+" linear "+str(zs)+" "+str(dz)+"\n")
    f.write("tdef "+str(nt)+" linear "+ts+" "+dt+"\n")
    f.write("vars 4\n")
    f.write("ZNW=>ZNW 39 t,z eta values on full (w) levels\n")
    f.write("W=>W 39 t,z,y,x z-wind component\n")
    f.write("PH=>PH 39 t,z,y,x perturbation geopotential\n")
    f.write("PHB=>PHB 39 t,z,y,x base-state geopotential\n")
    f.write("endvars\n")
    f.close()


if __name__ == "__main__":
    
    # Coordinates Variables (or dimensions) extracted from wrfout files
    # variable name in this code => variable name in wrfout files
    # xlon => XLONG,
    # xlat => XLAT, 
    # xlon_u => XLONG_U, 
    # xlat_u => XLAT_U,
    # xlon_v => XLONG_V, 
    # xlat_v => XLAT_V, 
    # vertical => bottom_top, 
    # vertical_stag => bottom_top_stag
    
    nt_each_dom=[-1,-1,-1] # Total time steps of each domain

    for dom in domains:
        
        # search wrfout files in WrfoutDir
        file_list=os.popen("ls "+WrfoutDir+"/wrfco2_"+dom+"*")
        file_list=file_list.read().split("\n")[:-1]
        
        # open one of these files and extract the coordinates variable
        ds=xr.open_dataset(file_list[0])
        xlon=ds.XLONG.values[0,0]
        xlat=ds.XLAT.values[0,:,0]
        xlon_u=ds.XLONG_U.values[0,0]
        xlat_u=ds.XLAT_U.values[0,:,0]
        xlon_v=ds.XLONG_V.values[0,0]
        xlat_v=ds.XLAT_V.values[0,:,0] 
        vertical=ds.bottom_top.values
        vertical_stag=ds.bottom_top_stag.values
        
        # General setting for physical variable, u, v, w and znw
        nt=len(file_list)
        StartTime=file_list[0].split("/")[-1]
        ts=datetime_filename2grads(StartTime)
        dt=Dt_each_dom[dom]
        nt_each_dom[int(dom[1:])-1]=nt

        # center variables
        nx=len(xlon)
        xs=xlon[0]
        dx=d_array(xlon)
        ny=len(xlat)
        ys=xlat[0]
        dy=d_array(xlat)
        nz=len(vertical)
        zs=vertical[0]
        dz=d_array(vertical,integer=True)
        ctl_center(WrfoutDir,CtlDir,dom,nx,xs,dx,ny,ys,dy,nz,zs,dz,nt,ts,dt)
        
        # U variable (x: stagger)
        nx=len(xlon_u)
        xs=xlon_u[0]
        dx=d_array(xlon_u)
        ny=len(xlat_u)
        ys=xlat_u[0]
        dy=d_array(xlat_u)
        nz=len(vertical)
        zs=vertical[0]
        dz=d_array(vertical,integer=True)
        ctl_u(WrfoutDir,CtlDir,dom,nx,xs,dx,ny,ys,dy,nz,zs,dz,nt,ts,dt)
        
        # V variable (y: stagger)
        nx=len(xlon_v)
        xs=xlon_v[0]
        dx=d_array(xlon_v)
        ny=len(xlat_v)
        ys=xlat_v[0]
        dy=d_array(xlat_v)
        nz=len(vertical)
        zs=vertical[0]
        dz=d_array(vertical,integer=True)
        ctl_v(WrfoutDir,CtlDir,dom,nx,xs,dx,ny,ys,dy,nz,zs,dz,nt,ts,dt)
        
        # W, PH, PHB, ZNW variables (z: stagger)
        nx=len(xlon)
        xs=xlon[0]
        dx=d_array(xlon)
        ny=len(xlat)
        ys=xlat[0]
        dy=d_array(xlat)
        nz=len(vertical_stag)
        zs=vertical_stag[0]
        dz=d_array(vertical_stag,integer=True)
        ctl_w(WrfoutDir,CtlDir,dom,nx,xs,dx,ny,ys,dy,nz,zs,dz,nt,ts,dt)

	#Create a.gs for testing
    #os.system("sed s/{TimeTotal_d01}/"+str(nt_each_dom[0])+"/g "+CtlDir+"/a.gs.bench > "+CtlDir+"/temp1")
    #os.system("sed s/{TimeTotal_d02}/"+str(nt_each_dom[1])+"/g "+CtlDir+"/temp1 >"+CtlDir+"/temp2")
    #os.system("sed s/{TimeTotal_d03}/"+str(nt_each_dom[2])+"/g "+CtlDir+"/temp2 > "+CtlDir+"/a.gs")
    #os.system("rm -f "+CtlDir+"/{temp1,temp2}")
        
       
        
        

        
