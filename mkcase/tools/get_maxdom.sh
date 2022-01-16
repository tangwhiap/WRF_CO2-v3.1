#!/bin/bash

CASECONFIG=$1
SetdomFile=$2
Region=$3

source ../.model_def_dir.sh
source $Trashrc $ROOTDIR
mkdir .get_maxdom
cd .get_maxdom
cat > get_maxdom.f90 << EOF
!!! ----------------------------------------------------------------- !!!
!!!                             WARNING                               !!!
!!! This code is generated automatically by MAKE CASES get_maxdom.sh  !!!
!!!        Don't edit it, your changes to this file will be lost.     !!!
!!! ----------------------------------------------------------------- !!!
Program main
    integer :: max_dom = 0
    real :: xs(99), xe(99), ys(99), ye(99), dx(99), dy(99)
    namelist/${Region}/max_dom, xs, xe, ys, ye, dx, dy
    open(1,file="${CASECONFIG}/${SetdomFile}", status="old", action="read")
    read(1,nml=${Region})
    close(1)
    if(max_dom .ge. 100)then
        stop
    endif
    print*,"# Region: ${Region} "
    if(max_dom < 10)then
        print'(A8,I1)',"max_dom=",max_dom
    else
        print'(A8,I2)',"max_dom=",max_dom
    endif
end
EOF
LD_LIBRARY_PATH=
gfortran -o get_maxdom.exe get_maxdom.f90
cat > $CASECONFIG/max_dom.sh << EOF
### ----------------------------------------------------------------------- ###
###                                 WARNING                                 ###
###   This scripts is generated automatically by MAKE CASES get_maxdom.sh   ###
### Don't edit it after the case is running, otherwise it will be damaged ! ###
### ----------------------------------------------------------------------- ###
EOF
./get_maxdom.exe >> $CASECONFIG/max_dom.sh
