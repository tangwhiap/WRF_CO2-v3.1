#!/usr/bin/env python

'''
Top-level python script of Namelist Generator System (NGS)
Authors:
  Wenhan Tang - 11/2020 (Original version)
  ...

Usage: 
   ./main_ngs script.ngs
   "script.ngs" refers to a NGS script file, contains operations(open, add, modify, delete, save, etc.) of namelist, defined by users.

Output:
   Depends on the "save" command in script.ngs

*** for more information of NGS script file, please read README.ngs ***

'''
import sys
from NGS_interpretor import interpretor
from NGS_command import ngs_open, ngs_mod, ngs_add, ngs_del,  ngs_delg, ngs_save
    
def NGS(scriptDir):        
    script = open(scriptDir)
    for iline in script:
        cmd = iline.strip()
        cmd_dic = interpretor(cmd)
        if cmd_dic == "continue":
            continue
        #print(cmd_dic)
        command = cmd_dic["command"].strip().lower()
        if command == "open":
            nmlfile = ngs_open(cmd_dic)
        if command == "mod":
            nmlfile = ngs_mod(cmd_dic, nmlfile)
        if command == "add":
            nmlfile = ngs_add(cmd_dic, nmlfile)
        if command == "del":
            nmlfile = ngs_del(cmd_dic, nmlfile)
        if command == "delg":
            nmlfile = ngs_delg(cmd_dic, nmlfile)
        if command == "save":
            ngs_save(cmd_dic, nmlfile)
        
    script.close()


if __name__ == "__main__":
    scriptDir = sys.argv[1]
    NGS(scriptDir)
