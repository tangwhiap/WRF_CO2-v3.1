program main
    implicit none
    call Init
    call obs2grid
    call CleanVars
end program main

subroutine obs2grid()
    use mod_defdir
    use mod_qh
    use mod_read_station
    use mod_obs2grid
    use mod_mean
    implicit none
    real,parameter :: undef_in = -9999.0, undef_out = -9.98e+8
    real :: value, ixr, iyr, izr 
    real, allocatable :: co2grid(:,:,:),  height_each_station(:,:)
    integer :: ix, iy, iz
    integer, allocatable :: ix_each_station(:), iy_each_station(:), iz_each_station(:)
    integer, allocatable :: number_each_gridpoint(:,:,:)
    logical :: num_out, output_split
    namelist /control/ num_out, output_split
    open(1, file="namelist.o2g", status = "old")
    read(1, nml = control)
    close(1)
    print*, "Read stations info."
    call read_data
    allocate(co2grid(nlon, nlat, nlev))
    allocate(number_each_gridpoint(nlon, nlat, nlev))
    allocate(height_each_station(Nsta, nlev))
    allocate(ix_each_station(Nsta))
    allocate(iy_each_station(Nsta))
    allocate(iz_each_station(Nsta))
    call QH_each_station(height_each_station)
    do ista = 1, Nsta
        call Index_in_grid(lon_sta(ista), lat_sta(ista), height_sta(ista),&
             height_each_station(ista,:), ixr, iyr, izr)
        call Index_r2i(ixr, iyr, izr, ix, iy, iz)
        ix_each_station(ista) = ix
        iy_each_station(ista) = iy
        iz_each_station(ista) = iz
    enddo
    print*, "Start processing Observation ==> Grid data ..."
    if ( .not. output_split)then
        open(8,file=trim(OutDir)//"/"//"obs_d0"//trim(strdom)//".gdat",form="binary")
    endif
    call mean_caculate_Init
    do it = 1, Ntime
        !print*, "time", it
        !print*, TimeYr(it), TimeMon(it), TimeDay(it), TimeHr(it), TimeMin(it), TimeSec(it)
        if (it .eq. 1 .or. mod(it,100) .eq. 0)then
            print*, "itime = ", it
        endif
        co2grid = undef_out
        number_each_gridpoint = 0
        do ista = 1, Nsta
            value = co2_sta(ista, it)
            if (value .eq. undef_in)then
                cycle
            endif
            ix = ix_each_station(ista)
            iy = iy_each_station(ista)
            iz = iz_each_station(ista)
            if (number_each_gridpoint(ix, iy, iz) .eq. 0)then
                co2grid(ix, iy, iz) = value
            else
                co2grid(ix, iy, iz) = (co2grid(ix, iy, iz) * number_each_gridpoint(ix, iy, iz) + value)/&
                (number_each_gridpoint(ix, iy, iz) + 1)
                !print*, "OK",number_each_gridpoint(ix, iy, iz)
                !call sleep(5)
            endif
            number_each_gridpoint(ix, iy, iz) = number_each_gridpoint(ix, iy, iz) + 1
            !if (number_each_gridpoint(ix, iy, iz) > 1)then
            !    print*,number_each_gridpoint(ix, iy, iz) 
            !endif
        end do
        !print*, "writing ..."
        if (output_split)then
            open(8,file=trim(OutDir)//"/"//"obs_d0"//trim(strdom)//"_"//trim(TimeList(it)),form = "binary")
        endif
        write(8)(((co2grid(ix,iy,iz), ix=1, nlon), iy=1, nlat), iz=1, nlev)
        if(num_out) write(8)(((number_each_gridpoint(ix,iy,iz) * 1.0, ix=1, nlon), iy=1,nlat), iz=1, nlev)
        !print*, "done"
        if(output_split)then
            close(8)
        endif
        call mean_caculate(it, co2grid, undef_out)
    end do
    if( .not. output_split)then
        close(8)
    endif
    print*, "Make CTL file for output data ..."
    call mkctl(undef_out)
    call mean_caculate_End(undef_out)
    print*, "========================="
    print*, "   Sucessful Complete!"
    print*, "========================="
    print*, "Location of each station:"
    open(9,file=trim(OutDir)//"/"//"obs_d01_staloc.txt")
    do ista = 1, Nsta
        print*, "station", ista
        print*, "ix =", ix_each_station(ista), "iy =", iy_each_station(ista), "iz =", iz_each_station(ista)
        write(9,*) "station", ista
        write(9,*) "ix =", ix_each_station(ista), "iy =", iy_each_station(ista), "iz =", iz_each_station(ista)
    enddo
    print*, "All data saved in " // trim(OutDir)
    close(9)
End subroutine obs2grid


subroutine Init()
    use mod_defdir
    use mod_qh
    use mod_read_station
    use mod_obs2grid
    use mod_mean
    implicit none
    logical :: num_out, output_split
    namelist /control/ num_out, output_split
    open(1,file = "namelist.o2g",status="old")
    read(1,nml = control)
    close(1)
    call defdir_Init
    call gridInit
    call QH_init(nlev, dom)
    call mean_Init(num_out)
end subroutine Init

subroutine QH_each_station(height_each_station)
    use mod_defdir
    use mod_read_station
    use mod_qh
    use mod_obs2grid
    implicit none
    real :: height_each_station(Nsta, nlev)
    do ista = 1, Nsta
        print*, "Processing station", ista
        call writeQH(lon_sta(ista),lat_sta(ista),ista)
        call readQH(ista)
        height_each_station(ista, :) = QH_eta_height
    enddo
end subroutine QH_each_station

subroutine CleanVars()
    use mod_qh
    use mod_read_station
    use mod_mean
    implicit none
    call clean_vars_RS
    call deallvarQH
    call clean_vars_mean
end subroutine CleanVars

!subroutine datetime_wrf2grads(wrftype, gradstype)
!    character(20) :: wrftype, gradstype
!    character(5) :: year, mon, day, hour, min
!    character(4) :: MonthName(12), mon_name
!    integer :: imon
!    DATA MonthName/"JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"/
!    ! 2019-02-03_00:34:12
!    ! 1234567890123456789
!    year = wrftype(1:4)
!    mon = wrftype(6:7)
!    day = wrftype(9:10)
!    hour = wrftype(12:13)
!    min = wrftype(18:19)
!    read(mon,'(I2)') imon
!    mon_name = MonthName(imon)
!    gradstype = trim(hour)//":"//trim(min)//"Z"//trim(day)//trim(mon_name)//trim(year)
!end subroutine datetime_wrf2grads

subroutine mkctl(undef_out)
    use mod_obs2grid
    use mod_read_station
    use mod_mean, only: datetime_wrf2grads 
    implicit none
    real :: undef_out
    character(100) :: varname, varLongName, dtime, str_undef, str_nlon,&
    str_nlat, str_nlev, str_Ntime, str_datetime_gradstype, str_dtime
    logical :: num_out, output_split
    namelist /Name/ varname, varLongName, dtime
    namelist /control/ num_out, output_split
    open(1, file="namelist.o2g", status='old')
    read(1, nml = Name)
    read(1, nml = control)
    close(1)
    !write(strdom,'(I1)') dom
    write(str_undef,'(E15.4)') undef_out
    write(str_nlon,'(I0)') nlon
    !write(str_lon_s,'(F12.6)') lon_s
    !write(str_dlon,'(F12.6)') dlon
    write(str_nlat,'(I0)') nlat
    !write(str_lat_s,'(F12.6)') lat_s
    !write(str_dlat,'(F12.6)') dlat
    write(str_nlev,'(I0)') nlev
    write(str_Ntime,'(I0)') Ntime
    !print*,trim(dtime)
    write(str_dtime,'(A5)') dtime
    !print*,trim(dtime)
    call datetime_wrf2grads(TimeList(1), str_datetime_gradstype)
    open(9,file=trim(OutDir)//"/"//"obs_d0"//trim(strdom)//".ctl")
    !write(9,*) "DSET "//trim(OutDir)//"/"//"obs_d0"//trim(strdom)//"_%y4-%m2-%d2_%h2:%n2:00"
    if(output_split)then
        write(9,*) "DSET ^obs_d0"//trim(strdom)//"_%y4-%m2-%d2_%h2:%n2:00"
    else
        write(9,*) "DSET ^obs_d0"//trim(strdom)//".gdat"
    endif
    write(9,*) "TITLE OBS2GRID. data from sense, grid from wrf output"
    write(9,*) "UNDEF "//trim(str_undef)
    if (output_split) then
        write(9,*) "options template"
    endif
    write(9,*) "xdef "//trim(str_nlon)//" linear "//trim(str_lon_s)//" "//trim(str_dlon)
    write(9,*) "ydef "//trim(str_nlat)//" linear "//trim(str_lat_s)//" "//trim(str_dlat)
    write(9,*) "zdef "//trim(str_nlev)//" linear 0 1"
    write(9,*) "tdef "//trim(str_Ntime)//" linear "//trim(str_datetime_gradstype(1:15))//" "//trim(str_dtime)
    if(num_out) then
        write(9,*) "vars 2"
    else
        write(9,*) "vars 1"
    endif
    write(9,*) trim(varname)//" "//trim(str_nlev)//" 99 "//trim(varLongName)
    if(num_out)then
        write(9,*) "num "//trim(str_nlev)//" 99 Number of each grid"
    endif
    write(9,*) "endvars"
    close(9)
end subroutine mkctl
