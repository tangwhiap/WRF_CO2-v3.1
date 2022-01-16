MODULE mod_mean
    use mod_read_station
    use mod_obs2grid
    use mod_defdir
    implicit none
    real, allocatable :: co2grid_hourly(:,:,:), co2grid_daily(:,:,:), co2grid_monthly(:,:,:)
    integer :: this_month, this_day, this_hour
    integer, allocatable :: num_this_month(:,:,:), num_this_day(:,:,:), num_this_hour(:,:,:)
    integer :: num_total_month, num_total_day, num_total_hour
    logical :: hourly, daily, monthly
    logical :: isInit_mean = .FALSE.
    logical :: num_out_modmean_save
    contains
    subroutine mean_Init(num_out_)
        logical num_out_
        namelist /mean/ hourly, daily, monthly
        call check_isInit_obs2grid()
        allocate(co2grid_hourly(nlon, nlat, nlev))
        allocate(co2grid_daily(nlon, nlat, nlev))
        allocate(co2grid_monthly(nlon, nlat, nlev))
        allocate(num_this_month(nlon, nlat, nlev))
        allocate(num_this_day(nlon, nlat, nlev))
        allocate(num_this_hour(nlon, nlat, nlev))
        open(1, file = "namelist.o2g", status = "old")
        read(1, nml = mean)
        close(1)
        num_out_modmean_save = num_out_
        isInit_mean = .TRUE.
    end subroutine mean_Init

    subroutine mean_caculate_Init()
        call check_isInit_mean
        co2grid_hourly = 0
        co2grid_daily = 0
        co2grid_monthly = 0
        if (hourly) then
            open(11,file=trim(OutDir)//"/"//"obs_d0"//trim(strdom)//"_hourly.gdat",form="binary")
        endif
        if (daily) then
            open(12,file=trim(OutDir)//"/"//"obs_d0"//trim(strdom)//"_daily.gdat",form="binary")
        endif
        if (monthly) then
            open(13,file=trim(OutDir)//"/"//"obs_d0"//trim(strdom)//"_monthly.gdat",form="binary")
        endif
        this_month = TimeMon(1)
        this_day = TimeDay(1)
        this_hour = TimeHr(1)
        num_this_month = 0
        num_this_day = 0
        num_this_hour = 0
        num_total_month = 0
        num_total_day = 0
        num_total_hour = 0
    end subroutine mean_caculate_Init

    subroutine mean_caculate(itime, co2grid, undef_out)
        integer :: itime, ix, iy, iz
        real :: co2grid(nlon, nlat, nlev), undef_out
        call check_isInit_mean
        if (hourly) then
            if (TimeHr(itime) .NE. this_hour ) then
                call Nan_divide(co2grid_hourly, num_this_hour, undef_out)
                write(11) (((co2grid_hourly(ix,iy,iz), ix = 1, nlon), iy = 1, nlat), iz = 1, nlev)
                if (num_out_modmean_save) then
                    write(11) (((num_this_hour(ix,iy,iz) * 1.0, ix = 1, nlon), iy = 1, nlat), iz = 1, nlev)
                endif
                num_total_hour = num_total_hour + 1
                this_hour = TimeHr(itime)
                co2grid_hourly = 0
                num_this_hour = 0
            endif
            call Nan_Add(co2grid_hourly, co2grid, num_this_hour, undef_out)
        endif
        if (daily) then
            if (TimeDay(itime) .NE. this_day) then
                call Nan_divide(co2grid_daily, num_this_day, undef_out)
                write(12) (((co2grid_daily(ix,iy,iz), ix = 1, nlon), iy = 1, nlat), iz = 1, nlev)
                if (num_out_modmean_save)then
                    write(12) (((num_this_day(ix,iy,iz) * 1.0, ix = 1, nlon), iy = 1, nlat), iz = 1, nlev)
                    !print*, sum(num_this_day)
                    !pause
                endif
                num_total_day = num_total_day + 1
                this_day = TimeDay(itime)
                co2grid_daily = 0
                num_this_day = 0
            endif
            call Nan_Add(co2grid_daily, co2grid, num_this_day, undef_out)
        endif
        if (monthly) then
            if (TimeMon(itime) .NE. this_month) then
                call Nan_divide(co2grid_monthly, num_this_month, undef_out)
                write(13) (((co2grid_monthly(ix,iy,iz), ix = 1, nlon), iy = 1, nlat), iz = 1, nlev)
                if (num_out_modmean_save) then
                    write(13) (((num_this_month(ix,iy,iz) * 1.0, ix = 1, nlon), iy = 1, nlat), iz = 1, nlev)
                    !print*, sum(num_this_month)
                    !pause
                endif
                num_total_month = num_total_month + 1
                this_month = TimeMon(itime)
                co2grid_monthly = 0
                num_this_month = 0
            endif
            call Nan_Add(co2grid_monthly, co2grid, num_this_month, undef_out)
        endif
    end subroutine mean_caculate

    subroutine mean_caculate_End(undef_out)
        real :: undef_out
        if (hourly) then
            close(11)
            print*, "Make CLT file for hourly data ..."
            call mkctl_meandata(1,undef_out)
        endif
        if (daily) then
            close(12)
            print*, "Make CLT file for daily data ..."
            call mkctl_meandata(2,undef_out)
        endif
        if (monthly) then
            close(13)
            print*, "Make CLT file for monthly data ..."
            call mkctl_meandata(3,undef_out)
        endif
    end subroutine mean_caculate_End

    subroutine Nan_Add(sum_arr, added_arr, num_total, undef)
        real :: sum_arr(nlon, nlat, nlev), added_arr(nlon, nlat, nlev)
        integer :: num_total(nlon, nlat, nlev)
        integer :: ix, iy, iz
        real :: undef
        do ix = 1, nlon
            do iy = 1, nlat
                do iz = 1, nlev
                    if (added_arr(ix,iy,iz) == undef) then
                        cycle
                    endif
                    sum_arr(ix,iy,iz) = sum_arr(ix,iy,iz) + added_arr(ix,iy,iz)
                    num_total(ix,iy,iz) = num_total(ix,iy,iz) + 1
                enddo
            enddo
        enddo
    end subroutine Nan_Add

    subroutine Nan_divide(sum_arr, num_total, undef)
        real :: sum_arr(nlon, nlat, nlev)
        integer :: num_total(nlon, nlat, nlev)
        integer :: ix, iy, iz
        real :: undef
        do ix = 1, nlon
            do iy = 1, nlat
                do iz = 1, nlev
                    if (num_total(ix,iy,iz) == 0) then
                        sum_arr(ix,iy,iz) = undef
                        cycle
                    endif
                    sum_arr(ix,iy,iz) = sum_arr(ix,iy,iz) / (num_total(ix,iy,iz) * 1.0)
                enddo
            enddo
        enddo
    end subroutine Nan_divide

    subroutine check_isInit_mean()
        if ( .NOT. isInit_mean) then
            print*, "Please call mean_Init before."
            stop 
        endif
    end subroutine check_isInit_mean

    subroutine mkctl_meandata(dtime_id, undef_out)
        use mod_obs2grid
        use mod_read_station
        implicit none
        integer :: dtime_id ! =1 for hourly; =2 for daily; =3 for monthly
        real :: undef_out
        character(100) :: varname, varLongName, dtime, str_undef, str_nlon,&
        str_nlat, str_nlev, str_Ntime, str_datetime_gradstype, str_dtime
        namelist /Name/ varname, varLongName, dtime
        open(1, file="namelist.o2g", status='old')
        read(1, nml = Name)
        close(1)
        if (dtime_id /= 1 .AND. dtime_id /= 2 .AND. dtime_id /= 3) then
            print*, "dtime_id Error."
            stop
        endif
        !write(strdom,'(I1)') dom
        write(str_undef,'(E15.4)') undef_out
        write(str_nlon,'(I0)') nlon
        !write(str_lon_s,'(F12.6)') lon_s
        !write(str_dlon,'(F12.6)') dlon
        write(str_nlat,'(I0)') nlat
        !write(str_lat_s,'(F12.6)') lat_s
        !write(str_dlat,'(F12.6)') dlat
        write(str_nlev,'(I0)') nlev
        !print*,trim(dtime)
        if (dtime_id == 1) then
            write(str_dtime,'(A5)') "1hr"
            write(str_Ntime,'(I0)') num_total_hour
        else if (dtime_id == 2) then
            write(str_dtime,'(A5)') "1dy"
            write(str_Ntime,'(I0)') num_total_day
        else
            write(str_dtime,'(A5)') "1mo"
            write(str_Ntime,'(I0)') num_total_month
        endif
        !print*,trim(dtime)
        call datetime_wrf2grads(TimeList(1), str_datetime_gradstype)
        !write(9,*) "DSET "//trim(OutDir)//"/"//"obs_d0"//trim(strdom)//"_%y4-%m2-%d2_%h2:%n2:00"
        if (dtime_id == 1) then
            open(9,file=trim(OutDir)//"/"//"obs_d0"//trim(strdom)//"_hourly.ctl")
            write(9,*) "DSET ^obs_d0"//trim(strdom)//"_hourly.gdat"
        else if (dtime_id == 2) then
            open(9,file=trim(OutDir)//"/"//"obs_d0"//trim(strdom)//"_daily.ctl")
            write(9,*) "DSET ^obs_d0"//trim(strdom)//"_daily.gdat"
        else
            open(9,file=trim(OutDir)//"/"//"obs_d0"//trim(strdom)//"_monthly.ctl")
            write(9,*) "DSET ^obs_d0"//trim(strdom)//"_monthly.gdat"
        endif
        write(9,*) "TITLE OBS2GRID. data from sense, grid from wrf output"
        write(9,*) "UNDEF "//trim(str_undef)
        write(9,*) "xdef "//trim(str_nlon)//" linear "//trim(str_lon_s)//" "//trim(str_dlon)
        write(9,*) "ydef "//trim(str_nlat)//" linear "//trim(str_lat_s)//" "//trim(str_dlat)
        write(9,*) "zdef "//trim(str_nlev)//" linear 0 1"
        if (dtime_id == 1) then
            write(9,*) "tdef "//trim(str_Ntime)//" linear "//trim(str_datetime_gradstype(4:15))//" "//trim(str_dtime)
        else if (dtime_id == 2) then
            write(9,*) "tdef "//trim(str_Ntime)//" linear "//trim(str_datetime_gradstype(7:15))//" "//trim(str_dtime)
        else
            write(9,*) "tdef "//trim(str_Ntime)//" linear "//trim(str_datetime_gradstype(9:15))//" "//trim(str_dtime)
        endif
        if(num_out_modmean_save) then
            write(9,*) "vars 2"
        else
            write(9,*) "vars 1"
        endif
        write(9,*) trim(varname)//" "//trim(str_nlev)//" 99 "//trim(varLongName)
        if(num_out_modmean_save)then
            write(9,*) "num "//trim(str_nlev)//" 99 Number of each grid"
        endif
        write(9,*) "endvars"
        close(9)
    end subroutine mkctl_meandata

    subroutine datetime_wrf2grads(wrftype, gradstype)
        character(20) :: wrftype, gradstype
        character(5) :: year, mon, day, hour, min
        character(4) :: MonthName(12), mon_name
        integer :: imon
        DATA MonthName/"JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"/
        ! 2019-02-03_00:34:12
        ! 1234567890123456789
        year = wrftype(1:4)
        mon = wrftype(6:7)
        day = wrftype(9:10)
        hour = wrftype(12:13)
        min = wrftype(18:19)
        read(mon,'(I2)') imon
        mon_name = MonthName(imon)
        ! 00:34Z03FEB2019
        ! 123456789012345
        gradstype = trim(hour)//":"//trim(min)//"Z"//trim(day)//trim(mon_name)//trim(year)
    end subroutine datetime_wrf2grads

    subroutine clean_vars_mean()
        deallocate(co2grid_hourly)
        deallocate(co2grid_daily)
        deallocate(co2grid_monthly)
    end subroutine clean_vars_mean
END MODULE mod_mean
