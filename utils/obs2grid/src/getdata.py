# A python script to extract a time series of CO2 concentration from sense4 data in a specific location(lon,lat,height) and time range.
# Authors:
# TangWenhan 08/2020 (Original Version)

# This Script can be used by >>>from getdata import getdata

# Usage of the function "getdata":
# TimeList, CO2List = getdata(start,end,InputDir):
# == Input:
# start: start time of the specific time range. (format: YYYY-MM-DD hh:mm:ss)
# end: end time of the specific time range. (format: YYYY-MM-DD hh:mm:ss)
# InputDir: Directory of the wrfout files.
# == Output:
# TimeList: A list of time following with the data.
# OutputDir : A list of CO2 concentration data stracted from sense4 data.

import numpy as np
import datetime as dtm


def open_newfile(Time, InputDir):
    Time_file = dtm.datetime(Time.timetuple().tm_year,Time.timetuple().tm_mon,Time.timetuple().tm_mday)
    year_f = Time_file.timetuple().tm_year
    mon_f = Time_file.timetuple().tm_mon
    day_f = Time_file.timetuple().tm_mday
    FileName = str(year_f).zfill(4)+str(mon_f).zfill(2)+str(day_f).zfill(2)+".txt"
    #print(FileName)
    file=open(InputDir+"/"+FileName)
    return file, FileName, Time_file

def read_file(file):
    line=file.readline()
    if len(line) == 0:
        return False, None, None
    else:
        date_in_line = line.strip().split()[0]
        time_in_line = line.strip().split()[1]
        datetime_in_line = dtm.datetime.strptime(date_in_line+time_in_line,"%Y%m%d%H%M%S")
        co2 = float(line.strip().split()[5])
        return True, datetime_in_line, co2 

def other_undef(data):
    return data > 200

def getdata(start,end,dtData,InputDir):
    dTime_data = dtm.timedelta(minutes=dtData)
    dTime_file = dtm.timedelta(days=1)
    #Time_Lastest = dtm.datetime(2025,1,1)
    No_File_since_then = False
    StartDate_str=start
    EndDate_str=end
    #if len(StartDate_str) > 16 or len(EndDate_str) > 16:
    #    StartDate_str = StartDate_str[:-3]
    #    EndDate_str = EndDate_str[:-3]

    #StartDate=dtm.datetime.strptime(StartDate_str, '%Y-%m-%d_%H:%M:%S')
    #EndDate=dtm.datetime.strptime(EndDate_str, '%Y-%m-%d_%H:%M:%S')
    StartDate=dtm.datetime.strptime(StartDate_str[:-3], '%Y-%m-%d_%H:%M')
    EndDate=dtm.datetime.strptime(EndDate_str[:-3], '%Y-%m-%d_%H:%M')
 
    Time_Lastest = EndDate
    TimeList=[]
    CO2List=[]

    Time_data = StartDate
    Time_file = dtm.datetime(StartDate.timetuple().tm_year,StartDate.timetuple().tm_mon,StartDate.timetuple().tm_mday)
    while(True):
        if Time_file > Time_Lastest:
            No_File_since_then = True
            break
        try:
            file, FileName, Time_file = open_newfile(Time_file, InputDir)
            isEOF, Time_next, co2_next = read_file(file)
            assert isEOF, "The file " + FileName + " is an empty file."
        except:
            Time_file = Time_file + dTime_file
            #print("The file of "+str(Time_file)+" is not exit, try to open the next file")
            continue
        break        

    while(Time_data <= EndDate):
        if No_File_since_then:
            TimeList.append(Time_data)
            CO2List.append(np.nan)
            Time_data = Time_data + dTime_data
            continue            
        #print(str(Time_data), str(Time_next))
        if Time_data == Time_next:
            #print("record")
            print("Get a valid record on "+str(Time_data)+" from "+FileName)
            TimeList.append(Time_data)
            if other_undef(co2_next):
                CO2List.append(co2_next)
            else:
                CO2List.append(np.nan)
            isEOF, Time_next, co2_next = read_file(file)
            if not(isEOF):
                file.close()
                while(True):
                    if Time_file > Time_Lastest:
                        No_File_since_then = True
                        break
                    try:
                        Time_file = Time_file + dTime_file
                        file, FileName, Time_file = open_newfile(Time_file, InputDir)
                        isEOF, Time_next, co2_next = read_file(file)
                        assert isEOF, "The file " + FileName + " is  empty."
                    except:
                        #print("The file of "+str(Time_file)+" is not exit, try to open the next file")
                        continue
                    break

        elif Time_data > Time_next:
            #print("waiting")
            isEOF, Time_next, co2_next = read_file(file)
            if not(isEOF):
                file.close()
                while(True):
                    if Time_file > Time_Lastest:
                        No_File_since_then = True
                        break
                    try:
                        Time_file = Time_file + dTime_file
                        file, FileName, Time_file = open_newfile(Time_file, InputDir)
                        isEOF, Time_next, co2_next = read_file(file)
                        assert isEOF, "The file " + FileName + " is  empty."
                    except:
                        #print("The file of "+str(Time_file)+" is not exit, try to open the next file")
                        continue
                    break
            Time_data = Time_data - dTime_data
    
        else:
            #print("missing data")
            TimeList.append(Time_data)
            CO2List.append(np.nan)
            
        Time_data = Time_data + dTime_data
    try:
        file.close()
    except:
        pass

    assert len(TimeList) == len(CO2List), "The length of time list isn't equal to that of data, there must be some bug."
    return TimeList, CO2List
