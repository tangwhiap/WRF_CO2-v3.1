#!/bin/bash
# Define directories for the frame of WRF-CO2 model
# ------ WARNING ------
# This script is generated automatically by ${ROOTDIR}/ini/init.sh
# ---------------------
ROOTDIR=/mnt/tiantan/tangwh/modeling/WRF-CO2-v3.1
# === MODEL FRAMEWORK DIRECTORY  ===

#Initialazation
INIDIR=$ROOTDIR/ini
# Cases directory
CASESDIR=$ROOTDIR/cases
# Make Case
MKCASEDIR=$ROOTDIR/mkcase
MKCASEDCDIR=$MKCASEDIR/default_config
# Directories of input_API
APIDir=$ROOTDIR/input_API
APIBckgDir=$APIDir/bckg
APIEmissDir=$APIDir/emiss
APICftaDir=$APIDir/cfta
APIMetDir=$APIDir/met
APIGeogDir=$APIDir/geog
APISSTDir=$APIDir/sst
APIRegDir=$APIDir/Registry
# Directories of WRF-CO2-core
SrcDir=$ROOTDIR/src
ScriptsDir=$SrcDir/Scripts
WRFDir=$SrcDir/WRF-chem/WRF
WPSDir=$SrcDir/WRF-chem/WPS
WRFRegDir=$WRFDir/Registry
WRFchemDir=$WRFDir/chem
DriverDir=$ScriptsDir/driver
BckgProcDir=$ScriptsDir/process_bckg
InputProcDir=$ScriptsDir/process_input
CftaProcDir=$InputProcDir
EmissProcDir=$InputProcDir
InputProcConfigDir=$InputProcDir/config
BckgProcConfigDir=$BckgProcDir/config
RunScriptsDir=$ScriptsDir/run_scripts
# Directories of utils
UtilsDir=$ROOTDIR/utils
SetdomDir=$UtilsDir/setdom
NGSDir=$UtilsDir/ngs
ADDTMDir=$UtilsDir/add_xtime
CRCTLDir=$UtilsDir/wrfctl
WRF2BINDir=$UtilsDir/wrf2bin
OBS2GRIDDir=$UtilsDir/obs2grid
BENCHDir=$UtilsDir/BenchPlots
XCO2Dir=$UtilsDir/XCO2
XCO2SrcDir=$XCO2Dir/Scripts
XCO2ConfigDir=$XCO2SrcDir/config
# Directories of tracers registry
TracersDir=$ROOTDIR/tracers
TracersSrc=$TracersDir/Scripts
TracersFiles=$TracersDir/registry_files
TracersSrcDemo=$TracersDir/src_demo
# Direcotory of web plot
WebDir=$HOME/public_html/WRF-CO2-v3_public
# Trash
TrashDir=$ROOTDIR/.trash
Trashrc=$ROOTDIR/.trashrc
