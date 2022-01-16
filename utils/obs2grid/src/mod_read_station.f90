MODULE mod_read_station
    use mod_defdir
    implicit none
    integer :: Nsta, Ntime
    integer :: ista, it
    real, allocatable :: lon_sta(:), lat_sta(:), height_sta(:)
    real, allocatable :: co2_sta(:, :)
    character(20), allocatable :: TimeList(:)
    integer,allocatable :: TimeSec(:), TimeMin(:), TimeHr(:), TimeDay(:), TimeMon(:), TimeYr(:)
    character(5) :: x
    contains
    subroutine read_data()
        open(1,file = trim(TempDir) // "/station.dat")
        read(1,*)
        read(1,'(I10)') Ntime
        read(1,'(I10)') Nsta
        allocate(lon_sta(Nsta))
        allocate(lat_sta(Nsta))
        allocate(height_sta(Nsta))
        allocate(co2_sta(Nsta,Ntime))
        allocate(TimeList(Ntime))
        allocate(TimeSec(Ntime))
        allocate(TimeMin(Ntime))
        allocate(TimeHr(Ntime))
        allocate(TimeDay(Ntime))
        allocate(TimeMon(Ntime))
        allocate(TimeYr(Ntime))
        do ista = 1, Nsta
            read(1,'(3F12.4)') lon_sta(ista), lat_sta(ista), height_sta(ista)
        end do
        do it = 1, Ntime
            read(1,'(A19)') TimeList(it)
            ! 2019-02-03_09:08:43
            read(TimeList(it),'(I4,5(A1,I2))') TimeYr(it), x, TimeMon(it), x, TimeDay(it), x, TimeHr(it), x, TimeMin(it), x, TimeSec(it)
            !print*, trim(TimeList(it))
            do ista = 1, Nsta
                read(1,'(F12.4)') co2_sta(ista, it)
            end do
        end do
        close(1)
    end subroutine read_data
    subroutine clean_vars_RS()
        deallocate(lon_sta)
        deallocate(lat_sta)
        deallocate(height_sta)
        deallocate(co2_sta)
        deallocate(TimeList)
        deallocate(TimeSec)
        deallocate(TimeMin)
        deallocate(TimeHr)
        deallocate(TimeDay)
        deallocate(TimeMon)
        deallocate(TimeYr)
    end subroutine clean_vars_RS
END MODULE mod_read_station

!program test
!    use read_station
!    call read_data()
!    print*,co2_sta
!    call clean_vars()
!end program test
