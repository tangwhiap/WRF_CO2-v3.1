MODULE mod_defdir
    implicit none
    !character(100) :: PDir
    character(100) :: TempDir
    !character(100) :: SrcDir
    character(100) :: DataDir
    !character(100) :: SENSEDir
    character(100) :: WRFDir
    !character(100) :: StainfoDir
    character(100) :: OutDir

    contains
    subroutine defdir_Init()
        !PDir = ".."
        !TempDir = trim(PDir) // "/temp"
        !SrcDir = trim(PDir) // "/src"
        !DataDir = trim(PDir) // "/data" 
        !SENSEDir = trim(DataDir) // "/SENSE"
        !WRFDir = trim(DataDir) // "/WRF"
        !StainfoDir = trim(DataDir) // "/stations_info"
        !OutDir = trim(PDir) // "/output"
        namelist /dir/ TempDir, DataDir, WRFDir, OutDir
        open(1,file="namelist.o2g",status='old')
        read(1,nml = dir)
        close(1)
    end subroutine defdir_Init
END MODULE mod_defdir