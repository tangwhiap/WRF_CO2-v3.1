#!/usr/bin/env grads
'reinit'
*_CASENAME=exp
*_time1='00:00z01jan2020'
*_time2='00:00z03jan2020'
*_DataDir='/home/tangwh/WRF-CO2-v3.0/cases/exp/output/wrfbin'
*_PlotDir='/home/tangwh/WRF-CO2-v3.0/cases/exp/plot/plotwork'
*_dom=1

iline=1
while(iline<=100)
    rf=read(".gs_input")
    stat=subwrd(rf,1)
    if(stat!=0)
        break
    endif 
    info=sublin(rf,2)
    say info
    if(iline=1) ; _CASENAME=info ; endif
    if(iline=2) ; _time1=info ; endif
    if(iline=3) ; _time2=info ; endif
    if(iline=4) ; _DataDir=info ; endif
    if(iline=5) ; _PlotDir=info ; endif
    if(iline=6) ; _dom=info ; endif
    iline=iline+1
*iline=iline+1 ;Set a infinitive cycle, until EOF.
endwhile
say '==================='
say _CASENAME
say _time1
say _time2
say _DataDir
say _PlotDir
say _dom
say '==================='



_psName='co2_met_d0'_dom'.ps'
_interval=24

'enable print meta'
VARdef()
drawCover()
*'q pos'
'print'
'clear'
MinmaxPlot()
*'q pos'
'print'
'clear'
t=_t1
while(t<=_t2)
PagePlot(t)
*'q pos'
'print'
'clear'
t=t+_interval
endwhile
'disable print'
'!gxps -i -c meta -o '_PlotDir'/'_psName
return

function VARdef()
    'open '_DataDir'/wrfco2_d0'_dom'.ctl'
    'set time '_time1
    _t1=getT()
    'set time '_time2
    _t2=getT()
    'set t '_t1' '_t2
    'set z 1'
    'define co2tot=co2_tot'
    'define PBLH=pblh'
    'define wind10=mag(u10,v10)'
    'define w=w'
    'set t 1'
    'co2max=max(co2_tot,t='_t1+1',t='_t2')'
    'co2min=min(co2_tot,t='_t1+1',t='_t2')'
return

function drawCover()
    title.1='WRF-CO2 BenchPlots 2'
    title.2='CO2 and meteorology conditions'
    title.3='CASE: '%_CASENAME
    title.4=_time1%' - '_time2
    title.5='domain: d0'_dom
*zstrc(x,y,str,siz,col,thick)
    'set vpage off'
    ys=10
    yint=0.8
    ititle=1
    yc=ys
    while(ititle<=5) 
        zstrc(4.3,yc,title.ititle,0.25,1,5)
        yc=yc-yint
        ititle=ititle+1
    endwhile
    subplot2gridm(2,1,2,1,1,1,0,0,0,0) 
    SpaPlot(hgt,1,0,10000,0,2500,125,1)
    'drawstr -p 2 -z 0.2 -t "Region of d0'_dom'" -b 0 -xo -yo -k 10'
    'drawstr -p 6 -z 0.2 -t "Longitude" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.2 -t "Latitude" -b 0 -xo -yo -k 10'
return

function MinmaxPlot()
    'set t 1'
    'set z 1'
    'set vpage off'
    zstrc(4,10.5,_time1%' - '%_time2,0.2,1,5)
    subplot2gridm(2,1,1,1,1,1,1,0,0,0)
    SpaPlot(co2max,1,0,10000,-1,-1,-1,0)
    'drawstr -p 2 -z 0.2 -t "CO2 maximum (ppm)" -b 0 -xo -yo -k 10'
    subplot2gridm(2,1,2,1,1,1,1,0,0,0)
    SpaPlot(co2min,1,0,10000,-1,-1,-1,0)
    'drawstr -p 2 -z 0.2 -t "CO2 minimum (ppm)" -b 0 -xo -yo -k 10'
return

function PagePlot(t)
    'set t 't
    timestr=qTime()
    zstr='z=1'
    'set vpage off'
    zstrc(4,10.5,timestr,0.2,1,5)

    zstrc(4,10.2,zstr,0.2,1,5)

    subplot2gridm(2,2,1,1,1,1,1,0,0,0)
    SpaPlot(co2tot,t,0,10000,400,560,20,1)
    'd skip(u,6,6);skip(v,6,6)'
    'drawstr -p 2 -z 0.25 -t "CO2 total (ppm)" -b 0 -xo -yo -k 10'

    subplot2gridm(2,2,1,2,1,1,1,0,0,0)
    SpaPlot(pblh,t,0,10000,0,1200,60,1)
    'drawstr -p 2 -z 0.25 -t "PBL height (m)" -b 0 -xo -yo -k 10'

    subplot2gridm(2,2,2,1,1,1,1,0,0,0)
    SpaPlot(wind10,t,0,10000,0,15,1,1)
    'drawstr -p 2 -z 0.25 -t "Wind speed in 10m (m/s)" -b 0 -xo -yo -k 10'
    
    subplot2gridm(2,2,2,2,1,1,1,0,0,0)
*SpaPlot(emiss,t,0,1000000,0,1000000,50000)
    SpaPlot(w,t,-100,100,-0.15,0.15,0.03,1)
    'drawstr -p 2 -z 0.25 -t "Vertical wind speed (m/s)" -b 0 -xo -yo -k 10'

*subplot2gridm(3,2,3,1,1,1,1,0,0,0)
*SpaPlot(co2vegas,t,0,10000,-20,20,1)
*'drawstr -p 2 -z 0.25 -t "CO2 influenced by Biosphere (ppm)" -b 0 -xo -yo -k 10'
    
*subplot2gridm(3,2,3,2,1,1,1,0,0,0)
*SpaPlot(cfta,t,0,10000,0,4500,500)
*'drawstr -p 2 -z 0.25 -t "Biosphere CFTA (mol/km^2/hr)" -b 0 -xo -yo -k 10'



return

function SpaPlot(var,t,pmin,pmax,lmin,lmax,lint,ifclevs)
    'set t 't
    'set gxout shaded'
    'set mpdset cnworld'
    'set grid on'
    'set grads off'
    'set cmin 'pmin
    'set cmax 'pmax
    if(ifclevs=1)
        strclev=''
        numclev=lmin
        while(numclev<=lmax)
            strclev=strclev%' '%numclev
            numclev=numclev+lint
        endwhile
        'set clevs'strclev
    endif
    'd 'var
    'cbar'
return


function setArea(lon1,lon2,lat1,lat2)
    'set lon 'lon1' 'lon2
    'set lat 'lat1' 'lat2
return

function setLoc(lon,lat)
    'set lon 'lon
    'set lat 'lat
return

function qTime()
    'q time'
    res=sublin(result,1)
    timestr=subwrd(res,3)
return timestr



function getT()
    'q dim'
    temp=sublin(result,5)
    t=subwrd(temp,9)
return t

function zstr0(x,y,str,siz,col,thick)
*    'set vpage off'
    'set strsiz 'siz
    'set string 'col' bl 'thick
    'draw string 'x' 'y' 'str
return

function zstrc(x,y,str,siz,col,thick)
*    'set vpage off'
    'set strsiz 'siz
    'set string 'col' c 'thick
    say 'draw string 'x' 'y' 'str
    'draw string 'x' 'y' 'str
return

function subplot2gridm(ny,nx,iy,ix,ysp,xsp,ur,dr,lr,rr)
    Lx=8.5-lr-rr
    Ly=11-ur-dr
    dx=Lx/nx
    dy=Ly/ny
    sx=0
    sy=0
    x1=(ix-1)*dx
    x2=(ix+xsp-1)*dx
    y2=Ly-(iy-1)*dy
    y1=Ly-(iy-1+ysp)*dy
*    say x1', 'x2', 'y1', 'y2
*    say x1+lr' 'x2+lr' 'y1+dr' 'y2+dr
    'set vpage off'
*say 'set vpage 'x1+lr' 'x2+lr' 'y1+dr' 'y2+dr
    'set vpage 'x1+lr' 'x2+lr' 'y1+dr' 'y2+dr
return

function subplot2grid(ny,nx,iy,ix,ysp,xsp)
    Lx=8.5
    Ly=11-upr
    dx=Lx/nx
    dy=Ly/ny
    sx=0
    sy=0
    x1=(ix-1)*dx
    x2=(ix+xsp-1)*dx
    y2=Ly-(iy-1)*dy
    y1=Ly-(iy-1+ysp)*dy
*    say x1', 'x2', 'y1', 'y2
    'set vpage 'x1' 'x2' 'y1' 'y2
return
