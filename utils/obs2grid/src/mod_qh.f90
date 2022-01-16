MODULE mod_QH
    use mod_defdir
    implicit none
    character(100) :: QH_strlon, QH_strlat, QH_strnz, QH_strdom
    real, allocatable :: QH_eta_height(:)
    integer :: QH_nz_memory, QH_dom_memory
    logical :: isInit_QH = .FALSE.

    contains
    subroutine QH_init(nz,dom)
        integer :: nz, dom
        QH_nz_memory = nz
        QH_dom_memory = dom
        write(QH_strnz,'(I3)') QH_nz_memory
        write(QH_strdom, '(I1)') QH_dom_memory
        allocate(QH_eta_height(QH_nz_memory))
        isInit_QH = .True.
    end subroutine QH_init

    subroutine check_init_QH()
        if( .NOT. isInit_QH)then
            print*,  "Please call QH_init before."
            stop
        endif
    end subroutine check_init_QH

    subroutine deallvarQH()
        call check_init_QH()
        deallocate(QH_eta_height)
    end subroutine deallvarQH

    subroutine writeQH(lon,lat,staid)
        real :: lon, lat
        integer :: staid
        character(100) :: str_staid
        call check_init_QH()
        write(QH_strlon,*) lon
        write(QH_strlat,*) lat
        write(str_staid,'(I0)') staid
        call system("grads -lbcx  'qh.gs " // trim(QH_strlon) // " " // trim(QH_strlat) // " "&
         // trim(QH_strnz) // " 1 " // trim(WRFDir) // "/" // "wrfco2_d0" // trim(QH_strdom) //&
         "_center.ctl" // " "// trim(WRFDir) // "/" // "wrfco2_d0" // trim(QH_strdom) //&
         "_w.ctl" // " " // trim(TempDir) // "/" // "eta_out_" // trim(str_staid) // ".txt" //"'")

    end subroutine writeQH
    
    subroutine readQH(staid)
        integer :: iz, staid
        character(100) :: str_staid
        write(str_staid,'(I0)') staid
        call check_init_QH()
        open(1,file=trim(TempDir) // "/" // "eta_out_" // trim(str_staid) // ".txt")
        read(1,*)
        do iz = 1, QH_nz_memory
            read(1,*) QH_eta_height(iz)
        end do
        close(1)
    end subroutine readQH

END MODULE mod_QH
