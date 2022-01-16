MODULE mod_obs2grid
    use mod_defdir
    implicit none
    integer :: nlon, nlat, nlev, dom
    real :: lon_s, lat_s, lon_e, lat_e, dlon, dlat
    character(20) :: str_lon_s, str_lat_s, str_dlon, str_dlat
    logical :: isInit_obs2grid = .False.
    character(20) :: strdom

    contains
    subroutine gridInit()
        namelist /grid/ nlon, nlat, nlev, str_lon_s, str_lat_s, str_dlon, str_dlat , dom
        open(1,file="namelist.o2g",status='old')
        read(1,nml=grid)
        close(1)
        !print*, "Get variables defined in namelist.o2g"
        read(str_lon_s,*)lon_s
        read(str_lat_s,*)lat_s
        read(str_dlon,*) dlon
        read(str_dlat,*) dlat
        write(strdom,'(I1)') dom
        !print*, lon_s, lat_s, dlon, dlat
        lon_e = lon_s + (nlon - 1) * dlon
        lat_e = lat_s + (nlat - 1) * dlat
        isInit_obs2grid = .True.
    end subroutine gridInit

    subroutine Index_in_grid(lon, lat, height, height_list, ixr, iyr, izr)
        real :: lon, lat, height, height_list(nlev)
        real :: ixr, iyr, izr
        real,parameter :: TINYg = 1.e-5
        integer :: iz
        if (check_isOut(lon, lat)) then
            print*, "Error: Location is out of grid range. "
            print*, "Location: lon = ", lon, "lat = ", lat
            print*, "Grid range: lon: ", lon_s, "~", lon_e, "lat: ", lat_s, "~", lat_e
            stop
        endif
        ixr = (lon - lon_s) / dlon + 1 + TINYg
        iyr = (lat - lat_s) / dlat + 1 + TINYg
        if (height .le. height_list(1)) then
            izr = 1.
        else if (height > height_list(nlev)) then
            izr = nlev * 1.0
        else
            do iz = 1, nlev
                if (height > height_list(iz) .and. height <= height_list(iz+1)) then
                    !izr = iz * 1.0 + (height - height_list(iz)) / (height_list(iz+1) - height_list(iz))
                    izr = (iz + 1) * 1.0
                endif
            end do
        endif
    end subroutine Index_in_grid

    subroutine check_isInit_obs2grid()
        if (.NOT. isInit_obs2grid) then
            print*,  "Please call gridInit before."
            stop
        endif
    end subroutine check_isInit_obs2grid

    function check_isOut(lon, lat)
        real :: lon, lat
        logical :: check_isOut
        check_isOut = .False.
        if (lon < lon_s .or. lon > lon_e) then
            check_isOut = .True.
        endif
        if (lat < lat_s .or. lat > lat_e) then
            check_isOut = .True.
        endif
    end function check_isOut

    subroutine Index_r2i(ixr, iyr, izr, ix, iy, iz)
        real :: ixr, iyr, izr
        integer :: ix, iy, iz 
        if (ixr > nlon) then
            ix = nlon
        else
            ix = nearestInt(ixr)
        endif
        if(iyr > nlat) then
            iy = nlat
        else
            iy = nearestInt(iyr)
        endif
        iz = nearestInt(izr)
    end subroutine Index_r2i


    function nearestInt(values_real)
        real :: values_real
        integer :: nearestInt
        if (values_real - int(values_real) .ge. 0.5) then
            nearestInt = int(values_real) + 1
        else
            nearestInt = int(values_real)
        endif
    end function nearestInt

END MODULE mod_obs2grid

!program test
!    use mod_defdir
!    use mod_obs2grid
!    use mod_qh
!    implicit none
!    integer,parameter :: nz = 38
!    real :: lon, lat, height, ixr, iyr, izr
!    integer :: ix, iy, iz, dom
!    lat = 3
!    lon = 4.5
!    height = 140
!    dom = 1
!    call defdir_Init()
!    print*, "defdir_Init done."
!    call gridInit()
!    print*, "gridInit done."
!    call QH_init(nz, dom)
!    print*, "QH_init done."
!    call writeQH(lon,lat)
!    print*, "QH writing done."
!    call readQH()
!    print*, "QH Get done."
!    call Index_in_grid(lon, lat, height, QH_eta_height, ixr, iyr, izr)
!    print*, ixr, iyr, izr
!    call Index_r2i(ixr, iyr, izr, ix, iy, iz)
!    print*, ix, iy, iz
!end program test

