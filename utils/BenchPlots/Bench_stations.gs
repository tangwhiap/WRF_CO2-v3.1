#!/home/liuzq/software/grads-2.0.2.oga.2/Classic/bin/grads -pbcx
* station.gs
*************************************************
* A GrADS script for "auto-BenchPlot" to show the difference 
* between data observed and simulated at each station location.

* Authors:
*   TangWenhan  09/2020 (Original version)
*   ...

* Usage:
* Set start datetime via _time1; format: “hhzddMMMyyyy”
* Set end datetime via _time2; format: "hhzddMMMyyyy"
* Set directory of CTL files via _InDir
* Set output directory via _OutDir
*************************************************

*_time1=00z01dec2019;_time2=06z14oct2020
*_time1=01z01jan2020;_time2=00z03jan2020
*_time1=00z01jan2020;_time2=00z01feb2020
*_time1=00z01feb2020;_time2=00z01mar2020

*_WRFInDir='/home/tangwh/WRF-CO2-v3.0/cases/exp/output/wrfbin'
*_OBSInDir='/home/tangwh/WRF-CO2-v3.0/cases/exp/plot/plotwork/obs'
*_OutDir='/home/tangwh/WRF-CO2-v3.0/cases/exp/plot/plotwork'
*_StaInfoDir='.'

iline=1
while(iline<=100)
    rf=read(".gs_input")
    stat=subwrd(rf,1)
    if(stat!=0)
        break
    endif 
    info=sublin(rf,2)
    if(iline=1) ; _CASENAME=info ; endif
    if(iline=2) ; _time1=info ; endif
    if(iline=3) ; _time2=info ; endif
    if(iline=4) ; _WRFInDir=info ; endif
    if(iline=5) ; _OutDir=info ; endif
    if(iline=6) ; _dom=info ; endif
    if(iline=7) ; _StaInfoDir=info ; endif
    if(iline=8) ; _OBSInDir=info ; endif
    iline=iline+1
*iline=iline+1 ;Set a infinitive cycle, until EOF.
endwhile


say '==================='
say _CASENAME
say _time1
say _time2
say _WRFInDir
say _OutDir
say _dom
say _StaInfoDir
say _OBSInDir
say '==================='

_OutName='stations_obs-wrf'

_dt=''
*_dt='_hourly'
*_dt='_daily'

*_v1=400;_v2=500
*_vd1=-50;_vd2=50
_v1=350;_v2=650
_vd1=-200;_vd2=200
_profz1=1;_profz2=38
_profz3=1;_profz4=6
_nz=38
*'!mkdir -p '_OutDir
'reinit'
'enable print meta'
stainfo()
VARdef(_dom)
drawCover()
*DIMdef(1)
ista=1
while(ista<=_Nsta)
    plot1sta(ista)
    ista=ista+1
endwhile
'disable print'
'!gxps -i -c meta -o '_OutDir'/'_OutName'.ps'
*'!rm -f meta'

function stainfo()
    _Nsta=0
    iline=1
    while(iline<=100)
        rf=read(_StaInfoDir"/stations_info.txt")
        stat=subwrd(rf,1)
        if(stat!=0)
            break
        endif 
        info=sublin(rf,2)
        issta=subwrd(info,1)
        if(issta='$')
            _Nsta=_Nsta+1
            _StaName._Nsta=subwrd(info,2)
            _lon._Nsta=subwrd(info,3)
            _lat._Nsta=subwrd(info,4)
            _nz._Nsta=subwrd(info,5)
            iz=1
            while(iz<=_nz._Nsta)
                _iz._Nsta.iz=subwrd(info,5+iz)
            iz=iz+1
            endwhile
        endif
*iline=iline+1 ;Set a infinitive cycle, until EOF.
    endwhile
return

function VARdef(dom)
*   dir='/home/tangwh/analysis/OBS_WRF_v2/obs_wrf_ctl'
    'open '_OBSInDir'/obs_d0'dom''_dt'.ctl'
    'q ctlinfo'
    say result
    'open '_WRFInDir'/wrfco2_d0'dom''_dt'.ctl'
    'q ctlinfo 2'
    say result
    _lons=getlons()
    _lone=getlone()
    _lats=getlats()
    _late=getlate()
    say _lons' '_lone' '_lats' '_late
return

function drawCover()
    title.1='WRF-CO2 BenchPlots 3'
    title.2='CO2 at observation stations'
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
    'set lon '_lons' '_lone
    'set lat '_lats' '_late
    'set z 1'
    'set t 1'
    'set grads off'
    'set gxout grfill'
    'set mpdset cnworld'
    'd hgt.2'
    ista=1
    while(ista<=_Nsta)
        drawpoint(_lon.ista,_lat.ista,0.2)
        ista=ista+1
    endwhile
*SpaPlot(hgt,1,0,10000,0,2500,125)
    'drawstr -p 2 -z 0.2 -t "Region of d0'_dom'" -b 0 -xo -yo -k 10'
    'drawstr -p 6 -z 0.2 -t "Longitude" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.2 -t "Latitude" -b 0 -xo -yo -k 10'
    'q pos'
    'print'
return

function StaVARdef(ista,iz)
    'set time '_time1' '_time2
    iz=1
    while(iz<=_nz.ista)
        'set z '_iz.ista.iz
        setLoc(_lon.ista,_lat.ista)
        'define co2obs'ista'z'iz'=co2'
        say 'co2obs'ista'z'iz' loaded'
        'define co2wrf'ista'z'iz'=co2_tot.2'
        say 'co2wrf'ista'z'iz' loaded'
        'define uwrf'ista'z'iz'=u.2'
        say 'uwrf'ista'z'iz' loaded'
        'define vwrf'ista'z'iz'=v.2'
        say 'vwrf'ista'z'iz' loaded'
        'define windwrf'ista'z'iz'=mag(uwrf'ista'z'iz',vwrf'ista'z'iz')'
        say 'windwrf'ista'z'iz' loaded'
        
        'define co2bck'ista'z'iz'=co2_bck.2'
        say 'co2bck'ista'z'iz' loaded'
        'define co2vegas'ista'z'iz'=co2_vegas.2-1200'
        say 'co2vegas'ista'z'iz' loaded'
        'define co2ffe'ista'z'iz'=co2_ffe.2'
        say 'co2ffe'ista'z'iz' loaded'
        iz=iz+1
    endwhile
    'define pblhwrf'ista'=PBLH.2(z=1)'
    say 'pblhwrf'ista' loaded'
    'set z '_profz1' '_profz2
    'define co2profwrf'ista'=co2_tot.2'
    say 'co2profwrf'ista' loaded'
    'set z 1'
return

function SCAT(ista,iz,color)
    'set time '_time1' '_time2
*    'set z '_iz.ista.iz
    'set gxout scatter'
    'set grads off'
    'set ccolor 'color
    'd co2obs'ista'z'iz';co2wrf'ista'z'iz
    'set gxout vector'
return



function plot1sta(ista)
    v1=_v1;v2=_v2
    vd1=_vd1;vd2=_vd2
    if (ista<1 | ista>_Nsta)
        say 'Error. station id 'ista' is out of range!'
        return
    endif
    StaVARdef(ista)
    'clear'
    'set vpage off'
    'set datawarn off'
    zstrc(2.3,9.5,_StaName.ista,0.3,1,7)
    zstrc(2.3,9,'lon = '_lon.ista' lat = '_lat.ista,0.16,1,5)

    
    subplot2gridm(1,2,1,2,1,1,0,8,0,0)
    'set lon '_lons' '_lone
    'set lat '_lats' '_late
    'set z 1'
    'set time '_time1
    'set grads off'
    'set gxout grfill'
    'set mpdset cnworld'
    'd hgt.2'
    drawpoint(_lon.ista,_lat.ista,0.415)

    if(_nz.ista>=1)
        'set z '_iz.ista.1
        subplot2gridm(8,1,1,1,3,1,3,0,0,0)
        'set time '_time1' '_time2
        setLoc(_lon.ista,_lat.ista)
        'set grads off';'set ylab on';'set xlab off'
        'set ylopts 1 3 0.11'  ;*set ylopts color thick size
        'set ylint 100'
        'set vrange 'v1' 'v2
        'set gxout line'
        
        'set digsiz 0.03';'set ccolor 6';'set cstyle 1';'set cmark 0';'set cthick 7'
        'd co2wrf'ista'z1'
        'set digsiz 0.03';'set ccolor 1';'set cstyle 0.2';'set cmark 3';'set cthick 5'
        'd co2obs'ista'z1'
*'set ccolor 1';'set cmark 3'
*'d co2obs'ista'z1'
         
*'d co2obs'ista'z1' ;* I don't know why it must be repeated 
        'drawstr -p 11 -z 0.15 -t "CO2 (ppm)" -b 0 -xo -yo -k 10'
        'drawstr -p 12 -z 0.15 -t "Height 1" -b 0 -xo -yo -k 10'
        zstr0(6,0.9,"WRF",0.15,6,7)
        zstr0(7,0.9,"OBS",0.15,1,7)


        subplot2gridm(8,1,2.5,1,2.5,1,3,0,0,0)
        'set grads off';'set ylab on';'set xlab on'
        'set ylint 100'
        'set vrange 'vd1' 'vd2
        'set cmark 3';'set ccolor 1'
        'd co2wrf'ista'z1-co2wrf'ista'z1'
        'set ccolor 12'
        'set digsiz 0.03'
        'd co2wrf'ista'z1-co2obs'ista'z1'
        'd ave(abs(co2wrf'ista'z1-co2obs'ista'z1),time='_time1',time='_time2')'
        say _StaName.ista' z=1'
        diff=sublin(result,2)
        diff=subwrd(diff,4)
        say diff
        zstr0(2.2,0.9,"WRF-OBS",0.15,12,7)
        zstr0(6,0.9,"MAE = "diff,0.15,3,7)
    endif

    if(_nz.ista>=2)
        'set z '_iz.ista.2
        subplot2gridm(8,1,5,1,3,1,3,0,0,0)
        'set grads off';'set grid on'
        'set gxout line'
        'set ylab on';'set xlab off'
        'set ylopts 1 3 0.11';'set ylint 100';'set vrange 'v1' 'v2
        'set cmark 0';'set ccolor 6';'set digsiz 0.03';'set cthick 7'
        'd co2wrf'ista'z2'
        'set cmark 3';'set ccolor 1';'set digsize 0.03';'set cthick 5'
        'd co2obs'ista'z2'
        'drawstr -p 11 -z 0.15 -t "CO2 (ppm)" -b 0 -xo -yo -k 10'
        'drawstr -p 12 -z 0.15 -t "Height 2" -b 0 -xo -yo -k 10'
        zstr0(6,0.9,"WRF",0.15,6,7)
        zstr0(7,0.9,"OBS",0.15,1,7)

        subplot2gridm(8,1,6.5,1,2.5,1,3,0,0,0)
        'set grads off';'set ylab on';'set xlab on'
        'set ylint 100'
        'set vrange 'vd1' 'vd2
        'set cmark 0';'set ccolor 1'
        'd co2wrf'ista'z2-co2wrf'ista'z2'
        'set ccolor 12'
        'set digsiz 0.03'
        'd co2wrf'ista'z2-co2obs'ista'z2'
        'd ave(abs(co2wrf'ista'z2-co2obs'ista'z2),time='_time1',time='_time2')'
        say _StaName.ista' z=2'
        diff=sublin(result,2)
        diff=subwrd(diff,4)
        say diff
        zstr0(2.2,0.9,"WRF-OBS",0.15,12,7)
        zstr0(6,0.9,"MAE = "diff,0.15,3,7)

    endif
    'q pos'
    'print'
    
    'clear'
    if(_nz.ista>=1)
        subplot2gridm(3,2,1,1,1,1,1,0,1,0)
        SCAT(ista,1,1)
        'drawstr -p 6 -z 0.13 -t "OBS" -b 1  -xo -yo  -k 10'
        'drawstr -p 9 -z 0.13 -t "WRF" -b 1  -xo -yo  -k 10'
        'drawstr -p 11 -z 0.15 -t "HEIGHT 1" -b -xo -yo -k 10'
    endif
    if(_nz.ista>=2)
        subplot2gridm(3,2,1,2,1,1,1,0,1,0)
        SCAT(ista,2,1)
        'drawstr -p 6 -z 0.13 -t "OBS" -b 1  -xo -yo  -k 10'
        'drawstr -p 9 -z 0.13 -t "WRF" -b 1  -xo -yo  -k 10'
        'drawstr -p 11 -z 0.15 -t "HEIGHT 2" -b -xo -yo -k 10'
    endif
    'set vpage off'
    zstr0(1,10.2,_StaName.ista,0.2,1,5)
    zstr0(1,9.8,'lon = '_lon.ista' lat = '_lat.ista,0.2,1,5)
    subplot2gridm(3,2,2,1,1,2,1,0,1,0)
    'set time '_time1' '_time2
    'set z '_profz1' '_profz2
    'set gxout shaded'
    'set grads off'
    'd co2profwrf'ista
    'cbar'
    'drawstr -p 2 -z 0.15 -t "CO2 profile (PPM)" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.15 -t "layers in WRF" -b 0 -xo -yo -k 10'
    subplot2gridm(3,2,3,1,1,2,1,0,1,0)
    'set time '_time1' '_time2
    'set z '_profz3' '_profz4
    'set gxout shaded'
    'set grads off'
    'd co2profwrf'ista
    'cbar'
    'drawstr -p 2 -z 0.15 -t "CO2 profile (PPM)" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.15 -t "layers in WRF" -b 0 -xo -yo -k 10'


    'q pos'
    'print'
*    'q gxout'
    
    'clear'
    subplot2gridm(6,1,1,1,2,1,1,0,0,0)
    'set grads off';'set grid on'
    'set gxout line'
    'set ylab on';'set xlab on'
    'set ylopts 1 3 0.11';'set ylint 5';'set vrange -30 30'
    'set cmark 0';'set ccolor 2';'set digsiz 0.03';'set cthick 7'
    'd uwrf'ista'z1'
    'set cmark 0';'set ccolor 3';'set digsiz 0.03';'set cthick 7'
    'd vwrf'ista'z1'
    'set cmark 0';'set ccolor 4';'set digsiz 0.03';'set cthick 7'
    'd windwrf'ista'z1'
    'set cmark 0';'set ccolor 1';'set digsiz 0.03';'set cthick 5'
    'd windwrf'ista'z1-windwrf'ista'z1'
    zstr0(6,0.9,"U",0.15,2,7)
    zstr0(6.5,0.9,"V",0.15,3,7)
    zstr0(7,0.9,"Speed",0.15,4,7)
    'drawstr -p 11 -z 0.15 -t "Wind (m/s)" -b 0 -xo -yo -k 10'
   
    subplot2gridm(6,1,3,1,2,1,1,0,0,0)
    'set grads off';'set grid on'
    'set gxout line'
    'set ylab on';'set xlab on'
    'set ylopts 1 3 0.11';'set ylint 500';'set vrange -600 4000'
    'set cmark 0';'set ccolor 7';'set digsiz 0.03';'set cthick 7'
    'd pblhwrf'ista
    'set cmark 0';'set ccolor 1';'set digsiz 0.03';'set cthick 5'
    'd pblhwrf'ista'-pblhwrf'ista
    'set ylpos 0.0 r'
    'set vrange '_v1' '_v2
    'set ylint 100'
    'set digsiz 0.03';'set ccolor 6';'set cmark 0';'set cthick 7'
    
    'd co2wrf'ista'z1'
    'drawstr -p 11 -z 0.15 -t "CO2 (ppm) & PBL height (m)" -b 0 -xo -yo -k 10'
    zstr0(6.25,2.3,"PBLH",0.15,7,7)
    zstr0(7,2.3,"CO2",0.15,6,7)

    subplot2gridm(6,1,5,1,2,1,1,0,0,0)
    'set grads off';'set grid on'
    'set gxout linefill'
    'set ylab on';'set xlab on'
    'set ylopts 1 3 0.11';'set ylint 500';'set vrange -100 1000'
    'set cmark 0';'set lfcols 9 9';'set digsiz 0.02';'set cthick 5'
    'd co2wrf'ista'z1-co2wrf'ista'z1;co2bck'ista'z1'
    'set cmark 0';'set lfcols 3 3';'set digsiz 0.02';'set cthick 5'
    'd co2bck'ista'z1;co2bck'ista'z1+co2vegas'ista'z1'
    'set cmark 0';'set lfcols 15 15';'set digsiz 0.02';'set cthick 5'
    'd co2bck'ista'z1+co2vegas'ista'z1;co2bck'ista'z1+co2vegas'ista'z1+co2ffe'ista'z1'
    
    zstr0(5.5,2.3,"BCK",0.15,9,7)
    zstr0(6.25,2.3,"VEGAS",0.15,3,7)
    zstr0(7.2,2.3,"FFE",0.15,15,7)
    'drawstr -p 11 -z 0.15 -t "CO2 components (ppm)" -b 0 -xo -yo -k 10'
    'set vpage off'
    zstr0(1,10.2,_StaName.ista,0.2,1,5)
    zstr0(1,9.8,'lon = '_lon.ista' lat = '_lat.ista,0.2,1,5) 
    'q pos'
    'print'
    
return

function plot1point(lon,lat,iz,name)
    StaVARdef(ista)
    'clear'
    'set vpage off'
    'set datawarn off'
    zstrc(2.3,9.5,name,0.3,1,7)
    zstrc(2.3,9,'lon = 'lon' lat = 'lat,0.16,1,5)

    
    subplot2gridm(1,2,1,2,1,1,0,8,0,0)
    'set lon '_lons' '_lone
    'set lat '_lats' '_late
    'set z 1'
    'set time '_time1
    'set grads off'
    'set gxout grfill'
    'set mpdset cnworld'
    'd hgt.2'
    drawpoint(lon,lat,0.415)

    'set z 'iz
    subplot2gridm(8,1,1.5,1,3,1,3,0,0,0)
    'set time '_time1' '_time2
    setLoc(lon,lat)
    'set grads off';'set ylab on';'set xlab off'
    'set ylopts 1 3 0.11'  ;*set ylopts color thick size
    'set ylint 100'
    'set vrange 200 800'
    'set gxout line'
    'set digsiz 0.03';'set ccolor 6';'set cmark 0';'set cthick 7'
    'd co2wrf'name'z1'
*    'set digsiz 0.08';'set ccolor 1';'set cmark 0';'set cthick 7'
*    'd co2obs'name'z1'
    'drawstr -p 11 -z 0.15 -t "CO2 (ppm)" -b 0 -xo -yo -k 10'
    'drawstr -p 12 -z 0.15 -t "Height 1" -b 0 -xo -yo -k 10'
    zstr0(6,0.9,"WRF",0.15,6,7)
*    zstr0(7,0.9,"OBS",0.15,1,7)


*    subplot2gridm(8,1,3.5,1,2.5,1,3,0,0,0)
*    'set grads off';'set ylab on';'set xlab on'
*    'set ylint 100'
*    'set vrange -200 200'
*    'set cmark 0';'set ccolor 1'
*    'd co2wrf'name'z1-co2wrf'name'z1'
*    'set ccolor 12'
*    'set digsiz 0.03'
*    'd co2wrf'name'z1-co2obs'name'z1'

    'print'
    
    'clear'
    subplot2gridm(6,1,1,1,2,1,1,0,0,0)
    'set grads off';'set grid on'
    'set gxout line'
    'set ylab on';'set xlab on'
    'set ylopts 1 3 0.11';'set ylint 5';'set vrange -30 30'
    'set cmark 0';'set ccolor 2';'set digsiz 0.03';'set cthick 7'
    'd uwrf'name'z1'
    'set cmark 0';'set ccolor 3';'set digsiz 0.03';'set cthick 7'
    'd vwrf'name'z1'
    'set cmark 0';'set ccolor 4';'set digsiz 0.03';'set cthick 7'
    'd windwrf'name'z1'
    'set cmark 0';'set ccolor 1';'set digsiz 0.03';'set cthick 5'
    'd windwrf'name'z1-windwrf'name'z1'
    zstr0(6,0.9,"U",0.15,2,7)
    zstr0(6.5,0.9,"V",0.15,3,7)
    zstr0(7,0.9,"Speed",0.15,4,7)
    'drawstr -p 11 -z 0.15 -t "Wind (m/s)" -b 0 -xo -yo -k 10'
   
    subplot2gridm(6,1,3,1,2,1,1,0,0,0)
    'set grads off';'set grid on'
    'set gxout line'
    'set ylab on';'set xlab on'
    'set ylopts 1 3 0.11';'set ylint 500';'set vrange -600 4000'
    'set cmark 0';'set ccolor 7';'set digsiz 0.03';'set cthick 7'
    'd pblhwrf'name
    'set cmark 0';'set ccolor 1';'set digsiz 0.03';'set cthick 5'
    'd pblhwrf'name'-pblhwrf'name
    zstr0(7,2.3,"PBLH",0.15,7,7)
    'drawstr -p 11 -z 0.15 -t "PBL height (m)" -b 0 -xo -yo -k 10'
   
    subplot2gridm(6,1,5,1,2,1,1,0,0,0)
    'set grads off';'set grid on'
    'set gxout linefill'
    'set ylab on';'set xlab on'
    'set ylopts 1 3 0.11';'set ylint 500';'set vrange -100 1000'
    'set cmark 0';'set lfcols 9 9';'set digsiz 0.02';'set cthick 5'
    'd co2wrf'name'z1-co2wrf'name'z1;co2bck'name'z1'
    'set cmark 0';'set lfcols 3 3';'set digsiz 0.02';'set cthick 5'
    'd co2bck'name'z1;co2bck'name'z1+co2vegas'name'z1'
    'set cmark 0';'set lfcols 15 15';'set digsiz 0.02';'set cthick 5'
    'd co2bck'name'z1+co2vegas'name'z1;co2bck'name'z1+co2vegas'name'z1+co2ffe'name'z1'
    
    zstr0(5.5,2.3,"BCK",0.15,9,7)
    zstr0(6.25,2.3,"VEGAS",0.15,3,7)
    zstr0(7.2.3,"FFE2",0.15,15,7)
    'drawstr -p 11 -z 0.15 -t "CO2 components (ppm)" -b 0 -xo -yo -k 10'
    'set vpage off'
    zstr0(1,10.2,name,0.2,1,5)
    zstr0(1,9.8,'lon = 'lon' lat = 'lat,0.2,1,5) 
*   'q pos'
    'print'
    
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

function getlons()
    'q dim'
    temp=sublin(result,2)
    lons=subwrd(temp,6)
return lons
function getlone()
    'q dim'
    temp=sublin(result,2)
    lone=subwrd(temp,8)
return lone
function getlats()
    'q dim'
    temp=sublin(result,3)
    lats=subwrd(temp,6)
return lats
function getlate()
    'q dim'
    temp=sublin(result,3)
    late=subwrd(temp,8)
return late

function station(station,lon,lat,t1,t2,istitle,col1,col2)
    'set lon 'lon;'set lat 'lat
    'set t 't1' 't2
    'set vrange 400 700'
    'set grads off'
    'set ccolor 'col1;'d co2(z=1)'
    'set ccolor 'col2;'d co2(z=3)'
    if(istitle=1)
        'draw title 'station
    endif
return

function drawpoint(lon,lat,siz)
    'q w2xy 'lon' 'lat
    x1=subwrd(result,3)
    y1=subwrd(result,6)
    'set string 1 c 9'
    'set strsiz 'siz
    'draw string 'x1' 'y1' `32'
return

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
    say 'set vpage 'x1+lr' 'x2+lr' 'y1+dr' 'y2+dr
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
