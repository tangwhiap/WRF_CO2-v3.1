!!! ----------------------------------------------------------------- !!!
!!!                             WARNING                               !!!
!!! This code is generated automatically by MAKE CASES get_maxdom.sh  !!!
!!!        Don't edit it, your changes to this file will be lost.     !!!
!!! ----------------------------------------------------------------- !!!
Program main
    integer :: max_dom = 0
    real :: xs(99), xe(99), ys(99), ye(99), dx(99), dy(99)
    namelist/BTH_d01/max_dom, xs, xe, ys, ye, dx, dy
    open(1,file="/mnt/tiantan/tangwh/modeling/WRF-CO2-v3.1/cases/test1/config/setdom.nml", status="old", action="read")
    read(1,nml=BTH_d01)
    close(1)
    if(max_dom .ge. 100)then
        stop
    endif
    print*,"# Region: BTH_d01 "
    if(max_dom < 10)then
        print'(A8,I1)',"max_dom=",max_dom
    else
        print'(A8,I2)',"max_dom=",max_dom
    endif
end
