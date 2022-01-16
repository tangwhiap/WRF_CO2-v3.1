'''
Functions of NGS command, imported by main_ngs.py
Authors:
  Wenhan Tang - 11/2020
  ...

'''
import f90nml as nml

def ngs_open(cmd_dic):
    command = cmd_dic["command"].strip()
    assert command == "open", "Function Calling Error! Check the code."
    fileDir = cmd_dic["content"].strip()
    file = open(fileDir)
    nmlfile = nml.read(file)
    return nmlfile
    
def ngs_mod(cmd_dic,nmlfile):
    command = cmd_dic["command"].strip()
    assert command == "mod", "Function Calling Error! Check the code."
    content = cmd_dic["content"].strip()
    var = content.split("=")[0].strip() # variables to modify.
    value = content.split("=")[1].strip() # values to substitude.

    isFind = False # Bool variable to show whether the variable can be found.
    for group in nmlfile:
        if var in nmlfile[group]:
            isFind = True
            break
    assert isFind, "NGS_MOD Error: Variable: " + var + " couldn't be found in namelist file."
    exec("nmlfile[group][var] = " + value)
    return nmlfile

def ngs_add(cmd_dic,nmlfile):
    command = cmd_dic["command"].strip()
    assert command == "add", "Function Calling Error! Check the code."
    content = cmd_dic["content"].strip()
    group_var = content.split("=")[0].strip() # variables to modify.
    value = content.split("=")[1].strip() # values to substitude.
    group = group_var.split("/")[0].strip()
    var = group_var.split("/")[1].strip()

    # If the group does not exist, create it.
    if not(group in nmlfile):
        nmlfile[group] = nml.Namelist([])

    # If the vairable already exits, raise a warning, and modify it.
    if var in nmlfile[group]:
        print("NGS_ADD: Warning! variable: " + var + " already exits, just modify it.")

    exec("nmlfile[group][var] = " + value)
    return nmlfile

def ngs_del(cmd_dic,nmlfile):
    command = cmd_dic["command"].strip()
    assert command == "del", "Function Calling Error! Check the code."
    var = cmd_dic["content"].strip()

    isFind = False # Bool variable to show whether the variable can be found.
    for group in nmlfile:
        if var in nmlfile[group]:
            isFind = True
            break
    if not isFind:
        print("NGS_DEL: Warning! variable: " + var + " does not exit, skip.")
        return nmlfile
    del nmlfile[group][var]
    return nmlfile

def ngs_delg(cmd_dic,nmlfile):
    command = cmd_dic["command"].strip()
    assert command == "delg", "Function Calling Error! Check the code."
    group = cmd_dic["content"].strip()

    if not(group in nmlfile):
        print("NGS_DEL: Warning! group: " + group + " does not exit, skip.")
        return nmlfile
    del nmlfile[group]
    return nmlfile

def ngs_save(cmd_dic,nmlfile):
    command = cmd_dic["command"].strip()
    assert command == "save", "Function Calling Error! Check the code."
    fileDir = cmd_dic["content"].strip()
    nmlfile.write(fileDir,force=True)
