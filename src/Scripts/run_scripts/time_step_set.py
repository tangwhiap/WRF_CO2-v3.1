#!/usr/bin/env python
'''
Authors:
    Wenhan TANG - 11/2020
    ...
'''
import numpy as np
import f90nml as nml
import sys
from pdb import set_trace
import os
nml_wrf_dirname = sys.argv[1]

time_step_distant_ratio = 6.0 / 1000.0

def set_time_step(L, parent_time_step_ratio, file_interval):
    global time_step_distant_ratio
    assert len(parent_time_step_ratio) == len(file_interval)
    max_dom = len(parent_time_step_ratio)
    ts_maxdom = L * time_step_distant_ratio
    print("Original: ", ts_maxdom)
    ts = (ts_maxdom / np.array(parent_time_step_ratio)).astype("int")
    #set_trace()
    ts_mindom = ts[-1]
    file_interval = np.array(file_interval).astype("int") * 60
    print("File_interval: ", file_interval)
    #offset = 0
    while(ts_mindom >= 1):
        #ts_mindom -= offset
        ts_maxdom = ts_mindom * np.array(parent_time_step_ratio)[-1]
        ts = (ts_maxdom / np.array(parent_time_step_ratio)).astype("int")
        print("ts: ", ts)
        mod_arr = np.mod(file_interval, ts)
        print("mod(file_interval, ts): ", mod_arr)
        if (mod_arr == 0).all():
            print("OK~~!")
            break
        ts_mindom = ts[-1]
        ts_mindom -= 1
        #offset += 1
    ts_maxdom = ts[0]
    return ts_maxdom

if __name__ == "__main__":
    print("Best time step caculating ...")
    nmlf = nml.read(nml_wrf_dirname)
    max_dom = nmlf["domains"]["max_dom"]
    dx_list = nmlf["domains"]["dx"]
    dy_list = nmlf["domains"]["dy"]
    parent_time_step_ratio_list = nmlf["domains"]["parent_time_step_ratio"]
    file_interval_list =  nmlf["time_control"]["auxhist23_interval"]
    try:
        temp = dx_list[0]
    except:
        dx_list = [dx_list]
    try:
        temp = dy_list[0]
    except:
        dy_list = [dy_list]
    try:
        temp = parent_time_step_ratio_list[0]
    except:
        parent_time_step_ratio_list = [parent_time_step_ratio_list]
    try:
        temp = file_interval_list[0]
    except:
        file_interval_list = [file_interval_list]
    #set_trace()
    dx = dx_list[0]
    dy = dy_list[0]
    parent_time_step_ratio = parent_time_step_ratio_list[:max_dom]
    for i in range(1, len(parent_time_step_ratio)):
        parent_time_step_ratio[i] = parent_time_step_ratio[i] * parent_time_step_ratio[i-1]
    file_interval = file_interval_list[:max_dom]
    L = min(dx,dy)
    time_step = set_time_step(L, parent_time_step_ratio, file_interval)
    print("Select time_step = " + str(time_step))
    cmd = "source config/configure.sh;$NGSDir/NLO \"mod &: time_step = " + str(time_step) + " | $CASEWORK/nml/nml-wrf\""
    os.system(cmd)
