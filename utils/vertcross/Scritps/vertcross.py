#!/usr/bin/env python
if __name__ == "__main__":
    exit()

import numpy as np
from scipy.interpolate import interp1d
from pdb import set_trace

class vertcross:
    def __init__(self, wrfdom, point_A, point_B, Nbins, name = "section"):
        assert "lon_s" in wrfdom
        assert "lon_e" in wrfdom
        assert "lat_s" in wrfdom
        assert "lat_e" in wrfdom
        assert "dlon" in wrfdom
        assert "dlat" in wrfdom
        assert "nx" in wrfdom
        assert "ny" in wrfdom
        #assert "nz" in wrfdom
        assert Nbins >= 2
        assert len(point_A) == 2
        assert len(point_B) == 2
        assert (point_A[0] != point_B[0]) or (point_A[1] != point_B[1])
        assert np.fix(Nbins) == np.fix(Nbins)
        self.name = name
        self.parent_dom = wrfdom
        self.point_A = point_A
        self.point_B = point_B
        self.lon_A = point_A[0]
        self.lat_A = point_A[1]
        self.lon_B = point_B[0]
        self.lat_B = point_B[1]
        assert self.lon_A >= wrfdom["lon_s"] and self.lon_A <= wrfdom["lon_e"]
        assert self.lon_B >= wrfdom["lon_s"] and self.lon_B <= wrfdom["lon_e"]
        assert self.lat_A >= wrfdom["lat_s"] and self.lat_A <= wrfdom["lat_e"]
        assert self.lat_B >= wrfdom["lat_s"] and self.lat_B <= wrfdom["lat_e"]
        self.Nbins = Nbins
        self.crosslon = np.linspace(self.lon_A, self.lon_B, self.Nbins)
        self.crosslat = np.linspace(self.lat_A, self.lat_B, self.Nbins)
        self.nx = wrfdom["nx"]
        self.ny = wrfdom["ny"]
        self.init_config_compute()

    
    def init_config_compute(self):
        self.wsx = ((self.crosslon - self.parent_dom["lon_s"]) / self.parent_dom["dlon"]).astype("int")
        self.wslon = self.wsx * self.parent_dom["dlon"] + self.parent_dom["lon_s"]
        self.wsy = ((self.crosslat - self.parent_dom["lat_s"]) / self.parent_dom["dlat"]).astype("int")
        self.wslat = self.wsy * self.parent_dom["dlat"] + self.parent_dom["lat_s"]
        self.wel = self.crosslon - self.wslon
        self.wer = self.parent_dom["dlon"]- self.wel
        self.snb = self.crosslat - self.wslat
        self.snt = self.parent_dom["dlat"] - self.snb

    def belinear(self, array):
        ## Important !!!
        ## Make sure that the first two dimension of array must be lat and lon
        assert array.shape[0] == self.ny
        assert array.shape[1] == self.nx
        ws = array[self.wsy, self.wsx]
        es = array[self.wsy, self.wsx + 1]
        wn = array[self.wsy + 1, self.wsx]
        en = array[self.wsy + 1, self.wsx + 1]
        nz = len(ws)
        #set_trace()
        #A = np.matmul( ws.reshape(nz, 1), (self.wer * self.snt).reshape(1, self.Nbins) )
        #B = np.matmul( es.reshape(nz, 1), (self.wel * self.snt).reshape(1, self.Nbins) )
        #C = np.matmul( en.reshape(nz, 1), (self.wel * self.snb).reshape(1, self.Nbins) )
        #D = np.matmul( wn.reshape(nz, 1), (self.wer * self.snb).reshape(1, self.Nbins) )
        A = np.swapaxes(ws, 0, 1) * (self.wer * self.snt)
        B = np.swapaxes(es, 0, 1) * (self.wel * self.snt)
        C = np.swapaxes(en, 0, 1) * (self.wel * self.snb)
        D = np.swapaxes(wn, 0, 1) * (self.wer * self.snb)

        section = (A + B + C + D) / ((self.wel + self.wer) * (self.snb + self.snt))
        #array_interp = (ws * (self.wer * self.snt) + es * (self.wel * self.snt) + en * (self.wel * self.snb) + wn * (self.wer * self.snb)) / ((self.wel + self.wer) * (self.snb + self.snt))
        return section
       
def chg_vert_coords(section_old, coord1_section, coord2):
    def profile_interpolate_1D(profile_bef, coord1, coord2):
        assert len(profile_bef.shape) == len(coord1.shape), "Conflict dimensions of variable and coordinate"
        assert len(profile_bef) == len(coord1), "Conflict length of variable and coordinate"
        f=interp1d(coord1, profile_bef, bounds_error = False, kind = "quadratic")
        return f(coord2)
    nz1 = coord1_section.shape[0]
    nz2 = len(coord2)
    assert section_old.shape[0] == nz1
    Nbins = section_old.shape[1]
    section_new = np.full( (nz2, Nbins), np.nan) 
    for ibin in range(Nbins):
        section_new[:, ibin] = profile_interpolate_1D(section_old[:, ibin], coord1_section[:, ibin], coord2)
    return section_new

    



