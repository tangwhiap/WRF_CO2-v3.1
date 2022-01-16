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
date1=03jan2020;date2=01feb2020
*date1=03jan2020;date2=05jan2020
_time1='00z'%date1;_time2='00z'%date2
*_time1=00z01jan2020;_time2=00z01feb2020
*_time1=00z01feb2020;_time2=00z01mar2020

_InDir='../data'
_WRFInDir=_InDir'/wrf'
_OBSInDir=_InDir'/obs'
_OutDir='/home/tangwh/public_html/WRF-CO2-grBench'
_OutName='ffe_jan1'
_dom=1

*iline=1
*while(iline<=100)
*    rf=read(".gs_input")
*    stat=subwrd(rf,1)
*    if(stat!=0)
*        break
*    endif 
*    info=sublin(rf,2)
*    if(iline=1) ; _CASENAME=info ; endif
*    if(iline=2) ; _time1=info ; endif
*    if(iline=3) ; _time2=info ; endif
*    if(iline=4) ; _WRFInDir=info ; endif
*    if(iline=5) ; _OutDir=info ; endif
*    if(iline=6) ; _dom=info ; endif
*    if(iline=7) ; _StaInfoDir=info ; endif
*    if(iline=8) ; _OBSInDir=info ; endif
*    iline=iline+1
**iline=iline+1 ;Set a infinitive cycle, until EOF.
*endwhile

*say '==================='
*say _CASENAME
*say _time1
*say _time2
*say _WRFInDir
*say _OutDir
*say _dom
*say _StaInfoDir
*say _OBSInDir
*say '==================='

*_OutName='stations_obs-wrf'


_dt=''
*_dt='_hourly'
*_dt='_daily'

*_v1=400;_v2=500
*_vd1=-50;_vd2=50

_v1=350;_v2=550;_vint=50
_vd1=-200;_vd2=200;_vdint=100

_vcbck1=400;_vcbck2=440;_intcbck=10
_vcffe1=-10;_vcffe2=60;_intcffe=10
_vcvgs1=-25;_vcvgs2=35;_intcvgs=5
_veffe1=0;_veffe2=30000;_inteffe=5000
_vevgs1=-20000;_vevgs2=20000;_intevgs=4000
_vfnet1=-20000;_vfnet2=20000;_intfnet=4000

_vchist1=350;_vchist2=550;_intchist=50
_vfhist1=-30000;_vfhist2=40000;_intfhist=10000

_vpblh1=0;_vpblh2=3300;_intpblh=1000

_profz1=1;_profz2=38
_profz3=1;_profz4=6

_vw1=-0.04;_vw2=0.04;_intw=0.02


if(_dt='');_period=95;endif
if(_dt='_hourly');_period=23;endif

'!mkdir -p '_OutDir
'reinit'
'enable print meta'
stainfo()
modelinfo()
VARdef(_dom)
*DIMdef(1)
StaVARdef(_dom)
ista=1
while(ista<=_Nsta)
    plot1sta(ista)
    ista=ista+1
endwhile
'disable print'
'!gxps -i -c meta -o '_OutDir'/'_OutName'.ps'
'!ps2pdf '_OutDir'/'_OutName'.ps '_OutDir'/'_OutName'.pdf'
'!rm -f meta'

function stainfo()
    _Nsta=0
    iline=1
    while(iline<=100)
        rf=read("stations_info.txt")
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

function modelinfo()
    _Nmod=0
    iline=1
    while(iline<=100)
        rf=read("wrf_info.txt")
        stat=subwrd(rf,1)
        if(stat!=0)
            break
        endif 
        info=sublin(rf,2)
        issta=subwrd(info,1)
        if(issta='o')
            _OBSName=subwrd(info,2)
            _OBSInDir=subwrd(info,3)
            _OBScolor=subwrd(info,4)
        endif
        if(issta='m')
            _Nmod=_Nmod+1
            _ModName._Nmod=subwrd(info,2)
            _ModDir._Nmod=subwrd(info,3)
            _Modcolor._Nmod=subwrd(info,4)
        endif
*iline=iline+1 ;Set a infinitive cycle, until EOF.
    endwhile
return

function VARdef(dom)
*   dir='/home/tangwh/analysis/OBS_WRF_v2/obs_wrf_ctl'
    say 'open '_OBSInDir
    say 'open '_OBSInDir'/obs_d0'dom''_dt'.ctl'
    'open '_OBSInDir'/obs_d0'dom''_dt'.ctl'
    imod=1
    while(imod<=_Nmod)
        'open '_ModDir.imod'/wrfco2_d0'dom''_dt'.ctl'
        imod=imod+1
    endwhile
return

function StaVARdef(ista,iz)
    'set time '_time1' '_time2
    iz=1
    while(iz<=_nz.ista)
        'set z '_iz.ista.iz
        setLoc(_lon.ista,_lat.ista)
        'define co2obs'ista'z'iz'=co2'
        climatology('co2obs'ista'z'iz,'co2obs'ista'z'iz'd',_time1,_time2,diurnal)
        say 'co2obs'ista'z'iz' loaded'
        imod=1
        while(imod<=_Nmod)
            fileID=imod+1
            'define co2wrf'ista'z'iz'm'imod'=co2_tot.'fileID
            say 'co2wrf'ista'z'iz'm'imod' loaded'
            climatology('co2wrf'ista'z'iz'm'imod,'co2wrf'ista'z'iz'm'imod'd',_time1,_time2,diurnal) ;*climatology(var,A,tim1,tim2,type)
*            'define uwrf'ista'z'iz'm'imod'=u.'fileID
*            say 'uwrf'ista'z'iz'm'imod' loaded'
*            'define vwrf'ista'z'iz'm'imod'=v.'fileID
*            say 'vwrf'ista'z'iz'm'imod' loaded'
*            'define windwrf'ista'z'iz'm'imod'=mag(uwrf'ista'z'iz'm'imod',vwrf'ista'z'iz'm'imod')'
*            say 'windwrf'ista'z'iz'm'imod' loaded'
            
            'define co2bck'ista'z'iz'm'imod'=co2_bck.'fileID
            climatology('co2bck'ista'z'iz'm'imod,'co2bck'ista'z'iz'm'imod'd',_time1,_time2,diurnal) ;*climatology(var,A,tim1,tim2,type)
             say 'co2bck'ista'z'iz'm'imod' loaded'
             'define co2vegas'ista'z'iz'm'imod'=co2_vegas.'fileID'-1200'
            climatology('co2vegas'ista'z'iz'm'imod,'co2vegas'ista'z'iz'm'imod'd',_time1,_time2,diurnal) ;*climatology(var,A,tim1,tim2,type)
             say 'co2vegas'ista'z'iz'm'imod' loaded'
             'define co2ffe'ista'z'iz'm'imod'=co2_ffe.'fileID
            climatology('co2ffe'ista'z'iz'm'imod,'co2ffe'ista'z'iz'm'imod'd',_time1,_time2,diurnal) ;*climatology(var,A,tim1,tim2,type)
             say 'co2ffe'ista'z'iz'm'imod' loaded'
            imod=imod+1
        endwhile
        iz=iz+1
    endwhile
    imod=1
    while(imod<=_Nmod)
        fileID=imod+1
        'set z 1'
        'define pblhwrf'ista'm'imod'=PBLH.'fileID'(z=1)'
        climatology('pblhwrf'ista'm'imod,'pblhwrf'ista'm'imod'd',_time1,_time2,diurnal) ;*climatology(var,A,tim1,tim2,type)
        say 'pblhwrf'ista'm'imod' loaded'
        'define ffe'ista'm'imod'=e_co2_ffe.'fileID'(z=1)'
        climatology('ffe'ista'm'imod,'ffe'ista'm'imod'd',_time1,_time2,diurnal) ;*climatology(var,A,tim1,tim2,type)
        say 'ffe'ista'm'imod' loaded'
        'define vegas'ista'm'imod'=e_bio_vegas.'fileID'(z=1)'
        climatology('vegas'ista'm'imod,'vegas'ista'm'imod'd',_time1,_time2,diurnal) ;*climatology(var,A,tim1,tim2,type)
        say 'vegas'ista'm'imod' loaded'
        'define fnet'ista'm'imod'=ffe'ista'm'imod'+vegas'ista'm'imod
        climatology('fnet'ista'm'imod,'fnet'ista'm'imod'd',_time1,_time2,diurnal) ;*climatology(var,A,tim1,tim2,type)
        say 'fnet'ista'm'imod' loaded'
        'set z '_profz1' '_profz2
        'define co2profwrf'ista'm'imod'=co2_tot.'fileID
        climatology('co2profwrf'ista'm'imod,'co2profwrf'ista'm'imod'd',_time1,_time2,diurnal) ;*climatology(var,A,tim1,tim2,type)
        'define co2profwrf'ista'm'imod'm=ave(co2profwrf'ista'm'imod',time='_time1',time='_time2')'

        say 'co2profwrf'ista'm'imod' loaded'
        'define wprofwrf'ista'm'imod'=w.'fileID
        say 'wprofwrf'ista'm'imod' loaded'
        imod=imod+1
    endwhile
    'set z 1'
return

function SCAT(ista,iz)
    'set time '_time1' '_time2
*    'set z '_iz.ista.iz
    'set gxout scatter'
    'set grads off'
    'set vrange '_v1' '_v2
    'set vrange2 '_v1' '_v2
    imod=1
    while(imod<=_Nmod)
        'set ccolor '_Modcolor.imod
        'd co2obs'ista'z'iz';co2wrf'ista'z'iz'm'imod
        'set ccolor 1'
        'd co2obs'ista'z'iz';co2obs'ista'z'iz
        'set ccolor 1'
        'd co2wrf'ista'z'iz'm'imod';co2wrf'ista'z'iz'm'imod
        imod=imod+1
    endwhile
    'set gxout vector'
return


function StaLocation(ista)
    'set lon 113.392 119.398'
    'set lat 37.7233 42.2567'
    'set z 1'
    'set time '_time1
    'set grads off'
    'set gxout grfill'
    'set mpdset cnworld'
    'd hgt.2'
    drawpoint(_lon.ista,_lat.ista)
return

function obswrf(ista,iz)
    'set z '_iz.ista.iz
    'set time '_time1' '_time2
    setLoc(_lon.ista,_lat.ista)
    'set grads off';'set ylab on';'set xlab off'
    'set ylopts 1 3 0.11'  ;*set ylopts color thick size
    'set ylint '_vint
    'set vrange '_v1' '_v2
    'set gxout line'
    imod=1
    while(imod<=_Nmod)
        'set digsiz 0.03';'set ccolor '_Modcolor.imod;'set cmark 0';'set cthick 7'
        'd co2wrf'ista'z1m'imod
        imod=imod+1
    endwhile
    'set digsiz 0.008';'set ccolor '_OBScolor;'set cmark 3';'set cthick 7'
    'd co2obs'ista'z1'
    'drawstr -p 11 -z 0.15 -t "CO2 (ppm)" -b 0 -xo -yo -k 10'
    'drawstr -p 12 -z 0.15 -t "Height 1" -b 0 -xo -yo -k 10'
    nameLegend(0.9,2.8,1.5,0.15,7,1)
return
    
function obswrfdiff(ista,iz)
    'set z '_iz.ista.iz
    'set time '_time1' '_time2
    setLoc(_lon.ista,_lat.ista)
    'set grads off';'set ylab on';'set xlab on'
    'set ylint '_vdint
    'set vrange '_vd1' '_vd2
    'set cmark 0';'set ccolor 1'
    'd co2wrf'ista'z1m1-co2wrf'ista'z1m1'
    difflist=''
    colorlist=''
    imod=1
    while(imod<=_Nmod)
        'set ccolor '_Modcolor.imod
        'set digsiz 0.015'
        'd co2wrf'ista'z'iz'm'imod'-co2obs'ista'z'iz
        'd ave(abs(co2wrf'ista'z'iz'm'imod'-co2obs'ista'z'iz'),time='_time1',time='_time2')'
        diff=sublin(result,2)
        diff=subwrd(diff,4)
        say _StaName.ista' z='iz
        say diff
        difflist=difflist%diff%' '
        colorlist=colorlist%_Modcolor.imod%' '
        imod=imod+1
    endwhile
    say difflist
    say colorlist
    listLegend(difflist,colorlist,0.9,2.8,1.5,0.15,7)
*zstr0(2.2,0.9,"WRF-OBS",0.15,12,7)
*zstr0(6,0.9,"MAE = "diff,0.15,3,7)
    'drawstr -p 11 -z 0.10 -t "WRF-OBS" -b 0 -xo -yo -k 10'
return

function component(ista,iz)

    'set vpage off'
    zstr0(1,10.3,_StaName.ista,0.2,1,5)
    zstr0(1,9.8,'lon = '_lon.ista' lat = '_lat.ista,0.2,1,5)
    'set time '_time1' '_time2
    setLoc(_lon.ista,_lat.ista)
    'set z 1'
    subplots(6,1,10.4,0,2.8,8,0,-1.4) ;*subplots(ny,nx,ys,xs,yL,xL,hint,vint)

    setaxes(1)
    imod=1
    while(imod<=_Nmod)
        'set grads off';'set grid on'
        'set gxout line'
        'set ylab on';'set xlab off'
        'set ylopts 1 3 0.11';'set ylint '_intcbck;'set vrange '_vcbck1' '_vcbck2
        'set cmark 0'
        'set ccolor '_Modcolor.imod
        'set cthick 7'
        'd co2bck'ista'z'iz'm'imod
        imod=imod+1
    endwhile
    'drawstr -p 11 -z 0.10 -t "CO2_BCK" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.13 -t "ppm" -b 1  -xo -yo  -k 10'

    setaxes(2)
    imod=1
    while(imod<=_Nmod)
        'set grads off';'set grid on'
        'set gxout line'
        'set ylab on';'set xlab off'
        'set ylopts 1 3 0.11';'set ylint '_intcffe;'set vrange '_vcffe1' '_vcffe2
        'set ylpos 0.0 r'
        'set cmark 0'
        'set ccolor '_Modcolor.imod
        'set cthick 7'
        'd co2ffe'ista'z'iz'm'imod
        imod=imod+1
    endwhile
    'drawstr -p 11 -z 0.10 -t "CO2_FFE" -b 0 -xo -yo -k 10'
    'drawstr -p 10 -z 0.13 -t "ppm" -b 1  -xo -yo  -k 10'

    setaxes(3)
    imod=1
    while(imod<=_Nmod)
        'set grads off';'set grid on'
        'set gxout line'
        'set ylab on';'set xlab off'
        'set ylopts 1 3 0.11';'set ylint '_intcvgs;'set vrange '_vcvgs1' '_vcvgs2
        'set cmark 0'
        'set ccolor '_Modcolor.imod
        'set cthick 7'
        'd co2vegas'ista'z'iz'm'imod
        imod=imod+1
    endwhile
    'drawstr -p 11 -z 0.10 -t "CO2_VEGAS" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.13 -t "ppm" -b 1  -xo -yo  -k 10'

    setaxes(4)
    imod=1
    while(imod<=_Nmod)
        'set grads off';'set grid on'
        'set gxout line'
        'set ylab on';'set xlab off'
        'set ylopts 1 3 0.11';'set ylint '_inteffe;'set vrange '_veffe1' '_veffe2
        'set ylpos 0.0 r'
        'set cmark 0'
        'set ccolor '_Modcolor.imod
        'set cthick 7'
        'd ffe'ista'm'imod
        imod=imod+1
    endwhile
    'drawstr -p 11 -z 0.10 -t "FFE" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.13 -t "mol/km^2/yr" -b 1  -xo -yo  -k 10'
    
    setaxes(5)
    imod=1
    while(imod<=_Nmod)
        'set grads off';'set grid on'
        'set gxout line'
        'set ylab on';'set xlab off'
        'set ylopts 1 3 0.11';'set ylint '_intevgs;'set vrange '_vevgs1' '_vevgs2
        'set cmark 0'
        'set ccolor '_Modcolor.imod
        'set cthick 7'
        'd vegas'ista'm'imod
        imod=imod+1
    endwhile
    'drawstr -p 11 -z 0.10 -t "BIO flux" -b 0 -xo -yo -k 10'
    'drawstr -p 10 -z 0.13 -t "mol/km^2/yr" -b 1  -xo -yo  -k 10'

    setaxes(6)
    imod=1
    while(imod<=_Nmod)
        'set grads off';'set grid on'
        'set gxout line'
        'set ylab on';'set xlab on'
        'set ylopts 1 3 0.11';'set ylint '_intfnet;'set vrange '_vfnet1' '_vfnet2
        'set ylpos 0.0 r'
        'set cmark 0'
        'set ccolor '_Modcolor.imod
        'set cthick 7'
        'd ffe'ista'm'imod
        colorlist=colorlist%_Modcolor.imod%' '
        imod=imod+1
    endwhile
    'drawstr -p 11 -z 0.10 -t "Fnet" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.13 -t "mol/km^2/yr" -b 1  -xo -yo  -k 10'
    'set vpage off'
    nameLegend(0.80,2.8,1.5,0.15,7,0) ;*nameLegend(y,xs,dx,siz,thick,obs)
return

function comhist(ista,iz,imod)
    'set time '_time1' '_time2
    setLoc(_lon.ista,_lat.ista)
    'set z 'iz
    'set grads off';'set grid on'
    'set gxout linefill'
    'set ylab on';'set xlab on'
    'set ylopts 1 3 0.11'
    'set ylint '_intchist;'set vrange '_vchist1' '_vchist2
    'set cmark 0';'set lfcols 9 9';'set digsiz 0.02';'set cthick 5'
    'd co2wrf'ista'z'iz'm'imod'-co2wrf'ista'z'iz'm'imod';co2bck'ista'z'iz'm'imod
    'set cmark 0';'set lfcols 15 15';'set digsiz 0.02';'set cthick 5'
    'd co2bck'ista'z'iz'm'imod';co2bck'ista'z'iz'm'imod'+co2ffe'ista'z'iz'm'imod
    'set cmark 0';'set lfcols 3 8';'set digsiz 0.02';'set cthick 5'
    'd co2bck'ista'z'iz'm'imod'+co2ffe'ista'z'iz'm'imod';co2bck'ista'z'iz'm'imod'+co2ffe'ista'z'iz'm'imod'+co2vegas'ista'z'iz'm'imod
    zstr0(5.2,2.2,"BCK",0.15,9,5)
    zstr0(5.8,2.2,"FFE",0.15,15,5)
    zstr0(6.3,2.2,"SOURCE",0.15,8,5)
    zstr0(7.3,2.2,"SINK",0.15,3,5)
    'drawstr -p 11 -z 0.15 -t "CO2 components" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.13 -t "ppm" -b 1  -xo -yo  -k 10'
return

function fluxhist(ista,imod)
    'set time '_time1' '_time2
    setLoc(_lon.ista,_lat.ista)
    'set z 1'
    'set grads off';'set grid on'
    'set gxout linefill'
    'set ylab on';'set xlab on'
    'set ylopts 1 3 0.11'
    'set ylint '_intfhist;'set vrange '_vfhist1' '_vfhist2
    'set cmark 0';'set lfcols 15 15';'set digsiz 0.02';'set cthick 5'
    'd ffe'ista'm'imod'-ffe'ista'm'imod';ffe'ista'm'imod
    'set cmark 0';'set lfcols 3 8';'set digsiz 0.02';'set cthick 5'
    'd ffe'ista'm'imod';ffe'ista'm'imod'+vegas'ista'm'imod
    zstr0(5.8,2.2,"FFE",0.15,15,5)
    zstr0(6.3,2.2,"SOURCE",0.15,8,5)
    zstr0(7.3,2.2,"SINK",0.15,3,5)
    'drawstr -p 11 -z 0.15 -t "flux components" -b 0 -xo -yo -k 10'
    'drawstr -p 9 -z 0.13 -t "mol/km^2/yr" -b 1  -xo -0.2  -k 10'
return

function co2pblh(ista,iz,imod)
    'set time '_time1' '_time2
    setLoc(_lon.ista,_lat.ista)
    say "come in"
    'set z 'iz

    'set grads off';'set grid on'
    'set gxout line'
    'set ylab on';'set xlab on'
    'set ylopts 1 3 0.11';'set ylint '_vint;'set vrange '_v1' '_v2
    'set cmark 0'
    'set ccolor 1'
    'set cthick 7'
    'd co2wrf'ista'z'iz'm'imod
    'set ylopts 1 3 0.11';'set ylint '_intpblh;'set vrange '_vpblh1' '_vpblh2
    'set ylpos 0.0 r'
    'set cmark 0'
    'set ccolor 8'
    'set cthick 7'
    'd pblhwrf'ista'm'imod
    zstr0(6.3,2.2,"CO2",0.15,1,5)
    zstr0(7.3,2.2,"PBLH",0.15,8,5)
    'drawstr -p 9 -z 0.13 -t "ppm" -b 1  -xo -yo  -k 10'
    'drawstr -p 10 -z 0.13 -t "meter" -b 1  -xo -yo  -k 10'
return

function PlotProfile(var,ista,imod,all)
    'set time '_time1' '_time2
    if (all=1)
        'set z '_profz1' '_profz2
    else
        'set z '_profz3' '_profz4
    endif
    'set gxout shaded'
    'set grads off'
    'd 'var'profwrf'ista'm'imod
    'cbar'
    'drawstr -p 10 -z 0.15 -t "'var'" -b 0 -xo -0.2 -k 10'
    'drawstr -p 9 -z 0.15 -t "layers in WRF" -b 0 -xo -yo -k 10'
return

function wpblh(ista,iz,imod)
    'set time '_time1' '_time2
    setLoc(_lon.ista,_lat.ista)
    'set z 'iz
    'set gxout linefill'
    'set grads off'
    'set ylopts 1 3 0.11';'set ylint '_intw;'set vrange '_vw1' '_vw2
    'set lfcols 4 2'
    'd wprofwrf'ista'm'imod' - wprofwrf'ista'm'imod';wprofwrf'ista'm'imod
    'set gxout line'
    'set ylopts 1 3 0.11';'set ylint '_intpblh;'set vrange '_vpblh1' '_vpblh2
    'set ylpos 0.0 r'
    'set cmark 0'
    'set ccolor 8'
    'set cthick 7'
    'd pblhwrf'ista'm'imod
*zstr0(6.3,2.2,"CO2",0.15,1,5)
*zstr0(7.3,2.2,"PBLH",0.15,8,5)
    'drawstr -p 9 -z 0.13 -t "W (m/s)" -b 1  -xo -yo  -k 10'
    'drawstr -p 10 -z 0.13 -t "PBLH (meter)" -b 1  -xo -yo  -k 10'
return

function co2diurnal(ista,iz)
    t1climo=time2t(_time1)
    'set t 't1climo' 't1climo+_period    
    setLoc(_lon.ista,_lat.ista)
    'set z 'iz
    'set gxout line'
    'set grads off'
*'set ylopts 1 3 0.11';'set ylint '_vint;'set vrange '_v1' '_v2
    'set ylopts 1 3 0.11';'set ylint 20';'set vrange 420 500'
    'set cmark 1';'set digsiz 0.07'
    'set ccolor 1';'set cthick 7'
    'd co2obs'ista'z'iz'd'
    imod=1
    while(imod<=_Nmod)
        'set ccolor '_Modcolor.imod
        'd co2wrf'ista'z'iz'm'imod'd'
        imod=imod+1
    endwhile
    'drawstr -p 11 -z 0.10 -t "CO2 (ppm)" -b 0 -xo -yo -k 10'
    'drawstr -p 12 -z 0.10 -t "Height'iz'" -b 0 -xo -yo -k 10'
return

function vardiurnal(var,label,vint,v1,v2,ista)
    t1climo=time2t(_time1)
    'set t 't1climo' 't1climo+_period    
    setLoc(_lon.ista,_lat.ista)
    'set z 1'
    'set gxout line'
    'set grads off'
    'set ylopts 1 3 0.11';'set ylint 'vint;'set vrange 'v1' 'v2

    imod=1
    while(imod<=_Nmod)
        'set ccolor '_Modcolor.imod
        'd 'var'm'imod'd'
        imod=imod+1
    endwhile
    'drawstr -p 11 -z 0.10 -t "'label'" -b 0 -xo -yo -k 10'
return
function profmean(var,label,vint,v1,v2,ista,imod)
    'set time '_time1
    'set z '_profz1' '_profz2
    'set grads off'
    'set gxout line'
*'set xyrev on'
    'set ylint 'vint;'set vrange 'v1' 'v2
    'd 'var''ista'm'imod'm'
    'drawstr -p 12 -z 0.10 -t "'label' mean" -b 0 -xo -yo -k 10'
return
function profhour(var,label,vint,v1,v2,ista,imod)
    'set z '_profz1' '_profz2
    'set grads off'
    'set gxout line'
    'set ylint 'vint;'set vrange 'v1' 'v2
    hourlist="00 06 12 18"
    colorlist="2 3 4 5"
    Nhours=4
    ih=1
    while(ih<=Nhours)
        hour=subwrd(hourlist,ih)
        color=subwrd(colorlist,ih)
        say 'hour: 'hour
        'set ccolor 'color
        'set time 'hour'z'_date1
        'd 'var''ista'm'imod'd'
        ih=ih+1
    endwhile
    'drawstr -p 12 -z 0.10 -t "'label' hourly mean" -b 0 -xo -yo -k 10'
    listLegend(hourlist,colorlist,0.9,2.8,0.3,0.15,7) ;*listLegend(strlist,colorlist,y,xs,dx,siz,thick)
return
function plot1sta(ista)
*v1=_v1;v2=_v2
*vd1=_vd1;vd2=_vd2
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
    StaLocation(ista)
    if(_nz.ista>=1)
        subplot2gridm(8,1,1,1,3,1,3,0,0,0)
        obswrf(ista,1)   

        subplot2gridm(8,1,2.5,1,2.5,1,3,0,0,0)
        obswrfdiff(ista,1)
        
    endif

    if(_nz.ista>=2)
        subplot2gridm(8,1,5,1,3,1,3,0,0,0)
        obswrf(ista,2)
        
        subplot2gridm(8,1,6.5,1,2.5,1,3,0,0,0)
        obswrfdiff(ista,2)
    endif
    'q pos'
    'print'

    'clear'
    'set vpage off'
    zstr0(1,10.2,_StaName.ista,0.2,1,5)
    zstr0(1,9.8,'lon = '_lon.ista' lat = '_lat.ista,0.2,1,5)
    if(_nz.ista>=1)
        subplot2gridm(2,1,1,1,1,1,1,0,1,0)
        SCAT(ista,1)
        'drawstr -p 6 -z 0.13 -t "OBS" -b 1  -xo -yo  -k 10'
        'drawstr -p 9 -z 0.13 -t "WRF" -b 1  -xo -yo  -k 10'
        'drawstr -p 11 -z 0.15 -t "HEIGHT 1" -b -xo -yo -k 10'
    endif
    if(_nz.ista>=2)
        subplot2gridm(2,1,2,1,1,1,1,0,1,0)
        SCAT(ista,2)
        'drawstr -p 6 -z 0.13 -t "OBS" -b 1  -xo -yo  -k 10'
        'drawstr -p 9 -z 0.13 -t "WRF" -b 1  -xo -yo  -k 10'
        'drawstr -p 11 -z 0.15 -t "HEIGHT 2" -b -xo -yo -k 10'
    endif
    'set vpage off'
    nameLegend(5,2.8,1.5,0.15,7,0)
    'q pos'
    'print'
    'clear'
    component(ista,1)
    'q pos'
    'print'

    'clear'
    'set vpage off'
    zstr0(1,10.3,_StaName.ista,0.2,1,5)
    zstr0(1,9.8,'lon = '_lon.ista' lat = '_lat.ista,0.2,1,5)
    subplots(3,1,10,0,3,8,0,0) ;*subplots(ny,nx,ys,xs,yL,xL,hint,vint)
    setaxes(1)
    comhist(ista,1,1)
    setaxes(2)
    fluxhist(ista,1)
    setaxes(3)
    co2pblh(ista,1,1)
    
    'q pos'
    'print'


    'clear'
    'set vpage off'
    zstr0(1,10.2,_StaName.ista,0.2,1,5)
    zstr0(1,9.8,'lon = '_lon.ista' lat = '_lat.ista,0.2,1,5)
    subplots(5,1,10,0,2.4,8,0,-0.6)
    setaxes(1)
    PlotProfile(co2,ista,1,1);*PlotProfile(var,ista,imod,all)
    setaxes(2)
    PlotProfile(w,ista,1,1)
    setaxes(3)
    PlotProfile(co2,ista,1,0)
    setaxes(4)
    PlotProfile(w,ista,1,0)
    setaxes(5)
    wpblh(ista,1,1)
    'q pos'
    'print'

    'clear'
    'set vpage off'
    zstr0(1,10.2,_StaName.ista,0.2,1,5)
    zstr0(1,9.8,'lon = '_lon.ista' lat = '_lat.ista,0.2,1,5)
    subplots(5,2,10,0,2.4,4,0,-0.6)
    setaxes(1)
    co2diurnal(ista,1)
    setaxes(2)
    co2diurnal(ista,2)
*vardiurnal(var,lable,vint,v1,v2,ista)
    setaxes(3)
    vardiurnal('co2ffe'ista'z1','CO2 FFE',5,0,30,ista)
    setaxes(4)
    vardiurnal('co2vegas'ista'z1','CO2 VEGAS',10,-20,20,ista)
    setaxes(5)
    vardiurnal('ffe'ista,'FFE flux',10000,5000,30000,ista)
    setaxes(6)
    vardiurnal('vegas'ista,'VEGAS flux',10000,0,10000,ista)
    setaxes(7)
    vardiurnal('fnet'ista,'Fnet',10000,-40000,40000,ista)
    setaxes(8)
    vardiurnal('pblhwrf'ista,'PBLH',1000,0,2000,ista)
    setaxes(9)
    vardiurnal('co2bck'ista'z1','CO2 BCK',1,410,435,ista)
    'set vpage off'
*nameLegend(5,2.8,1.5,0.15,7,0)
    nameLegend(0.50,2.8,1.5,0.15,7,0)

    'q pos'
    'print'
    
    'clear'
    'set vpage off'
    zstr0(1,10.2,_StaName.ista,0.2,1,5)
    zstr0(1,9.8,'lon = '_lon.ista' lat = '_lat.ista,0.2,1,5)

    subplots(4,2,10,0,3.5,5,-1.5,0)
    setaxes(1)
    profmean(co2profwrf,CO2,5,400,460,ista,1);*profmean(var,label,vint,v1,v2,ista,imod)
    setaxes(2)
    profhour(co2profwrf,CO2,5,400,460,ista,1);*profmean(var,label,vint,v1,v2,ista,imod)


    'q pos'
    'print'
    return   
    
    
return

*************** Tools *****************
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

function drawpoint(lon,lat)
    'q w2xy 'lon' 'lat
    x1=subwrd(result,3)
    y1=subwrd(result,6)
    'set string 1 c 9'
    'set strsiz 0.415'
    'draw string 'x1' 'y1' `32'
return

function zstr0(x,y,str,siz,col,thick)
*    'set vpage off'
    'set strsiz 'siz
    'set string 'col' bl 'thick
    say 'set string 'col' bl 'thick
    'draw string 'x' 'y' 'str
return

function zstrc(x,y,str,siz,col,thick)
*    'set vpage off'
    'set strsiz 'siz
    'set string 'col' c 'thick
    'draw string 'x' 'y' 'str
return

function climatology(var,A,tim1,tim2,type)
    t1climo=time2t(tim1)    ;* convert calendar time tim1 to time index t_1
*if(type='seasonal');'set t 't1climo' 't1climo+11;dt='1yr';endif
    say period
    if(type='diurnal');'set t 't1climo' 't1climo+_period;dt='1dy';endif
*'ltrend 'var' 'A'trend'
*'orig='var
*RunMean(orig,tim1,tim2)
    say A'=ave('var',t+0,time='tim2','_period+1')'
    A'=ave('var',t+0,time='tim2','_period+1')'  ;* climatology
*A'd=ave(origd,t+0,time='tim2','dt')' ;* dtrend climatology
    'modify 'A' 'type
*'modify 'A'd 'type
    'set time 'tim1' 'tim2
*A'a='var'-'A                        ;*anomaly
*A'ad=origd-'A'd'
return


function time2t(time)
* convert calendar time to index t; Modified from convert_t()  Zeng 12/2012
    'set time 'time
    'q dim'; dinf = result; timedim = sublin(dinf,5)
    t= subwrd(timedim,9)
return t

function t2time(t)
* convert index t to calendar timet; Modified from convert_time()  Zeng 12/2012
    'set t 't
    'q dim'; dinf = result; timedim = sublin(dinf,5); str= subwrd(timedim,6)
    time=substr(str,6,7)
return time



function nameLegend(y,xs,dx,siz,thick,obs)
    imod=1
    xnow=xs
    while(imod<=_Nmod)
        zstr0(xnow,y,_ModName.imod,siz,_Modcolor.imod,thick)
        xnow=xnow+dx
        imod=imod+1
    endwhile
    if(obs=1)
        zstr0(xnow,y,_OBSName,siz,_OBScolor,thick)
    endif
return

function listLegend(strlist,colorlist,y,xs,dx,siz,thick)
    ilist=1
    xnow=xs
    while(1)
        string=subwrd(strlist,ilist)
        color=subwrd(colorlist,ilist)
        if(string="" | color="")
            break
        endif
        zstr0(xnow,y,string,siz,color,thick)
        xnow=xnow+dx
        ilist=ilist+1
    endwhile 
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

function subplots(ny,nx,ys,xs,yL,xL,hint,vint)
    cx=xs
    cy=ys
    iax=1
    iy=1
    while(iy<=ny)
        ix=1
        while(ix<=nx)
            x1=xs+(ix-1)*(xL+hint)
            x2=x1+xL
            y2=ys-(iy-1)*(yL+vint)
            y1=y2-yL
            _axx1.iax=x1
            _axx2.iax=x2
            _axy1.iax=y1
            _axy2.iax=y2
            iax=iax+1
            ix=ix+1
        endwhile
        iy=iy+1
    endwhile
return

function setaxes(iax)
    say 'set vpage '_axx1.iax' '_axx2.iax' '_axy1.iax' '_axy2.iax
    'set vpage '_axx1.iax' '_axx2.iax' '_axy1.iax' '_axy2.iax
return
