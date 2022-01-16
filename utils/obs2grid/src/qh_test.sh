#!/bin/bash

###############
lon=116.5
lat=39.5
nz=38
time=4
dom=1
#WRFoutCTLDir=/home/tangwh/modeling/WRFs/WRF-CO2-d1c/WRF-CO2/WCofl/output/WRF-out-ctl
#WRFoutCTLDir=/home/tangwh/utils/obs2grid_v2/data/WRF
WRFoutCTLDir=/home/tangwh/datasets/WRF/FFDAS_vs_NDRC_744hr_test/NDRC/output/WRF-out-ctl
##############

CenterDir=$WRFoutCTLDir/wrfout_d0${dom}_center.ctl
WDir=$WRFoutCTLDir/wrfout_d0${dom}_w.ctl
OutDir=../temp/eta_out1.txt
grads -lbcx "run qh.gs "$lon" "$lat" "$nz" "$time" "$CenterDir" "$WDir" "$OutDir
