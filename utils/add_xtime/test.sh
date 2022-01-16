#!/bin/bash
input=/home/tangwh/WRF-CO2-v3.0/cases/eee/output/wrfco2
output=/home/tangwh/wrf-latlon/wrf2bin/data
StartDate='2019-01-01'
StartTime='00:00:00'
#echo $StartTime
./add_xtime.py $input $output $StartDate $StartTime
