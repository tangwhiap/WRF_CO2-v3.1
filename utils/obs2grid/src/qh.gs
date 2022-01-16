* qh.gs , in obs2grid system
* A GrADS script used to compute the height of each eta layers in WRF.
* = Authors :
*   TangWenhan (09/2020) original version
*   ...
*
* = Usage: 
*   =>input:
*    longitude, latitude, number of layers (center grid, not stagger grid), datetime. directory of ctl (vertical center grid), directory of ctl (vertical stagger grid)
*   =>output:
*    screen: number of each layer and it's height (in meter)
*    file: height of each layer.
*   =>example:
*   (in shell script)   grads -lbcx "qh.gs "$lon" "$lat" "$nz" "$time" "$CenterDir" "$WRFDir" "$OutDir
*   


function main(argv)
    lon=subwrd(argv,1)
    lat=subwrd(argv,2)
    nz=subwrd(argv,3)
    t=subwrd(argv,4)
    dc=subwrd(argv,5)
    dw=subwrd(argv,6)
    do=subwrd(argv,7)
    say argv
    'reinit'
    say 'open 'dw
    say 'open 'dc
    'open 'dw
    'open 'dc
    file=do
    z=1
    fw=1
    while(z<=nz+1)
*    'define hh=(PH(z='z+1')+PH(z='z'))/2+(PHB(z='z+1')+PHB(z='z')/2)/9.81-hgt.2'
    'define hh = (PH(z='z') + PHB(z='z'))/9.81-HGT.2'
    'set gxout shaded'
    'set mpdset cnworld'
    'set t 't
    'set lat 'lat
    'set lon 'lon
    'd hh'
    height=subwrd(result,4)
    say 'z='z' H='height'(m)'
    if(fw=1)
        rc=write(file,height)
        fw=0
    else
        rc=write(file,height,append)
    endif
    z=z+1
    endwhile
return
;
