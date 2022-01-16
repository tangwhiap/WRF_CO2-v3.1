#!/usr/bin/env python

def write_dict_info(dic, head_name = None, head_space = 0, sj = 4):
    if head_name is None:
        strw = " " * head_space + "{\n"
    #if head_name is not None:
    else:
        strw = " " * head_space + head_name + " = {\n"

    for strKey in dic:
        var = dic[strKey]
        strw += " " * (head_space + sj) + "\"" + strKey + "\": "
        if isinstance(var, dict):
            strw += "\n"
            strw_subDic = write_dict_info(var, head_space = head_space + sj, sj = sj)
            strw += strw_subDic

        elif isinstance(var, str):
            strw += "\"" + var + "\""

        else:
            strw += str(var)
        strw += ",\n"

    strw += " " * head_space + "}"
    return strw


test_dic = {
    "FFDAS":
    {
        "FluxName": "E_CO2_FFE_FFDAS",
        "data": "FFDAS",
        "kwargs": 
        {
            "sector": "wow",
            "num": 12,
        },
        "re": 12.345,
        "tt":
        {
            "fre":
            {
                "j": 1,
                "f": 2,
                "ke": {"1": "a", "2": 34.},
            }
        },
    }
}

if __name__ == "__main__":
    with open("test_dic.py", "w") as pf:
        strw = write_dict_info(test_dic, head_name = "test_dic", head_space = 0)
        pf.write(strw + "\n")

    from test_dic import test_dic as read_dic
    print(test_dic)
    print(read_dic)
    print(read_dic == test_dic)

