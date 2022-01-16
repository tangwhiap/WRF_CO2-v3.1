#!/usr/bin/env python

# Authors:
#    Wenhan TANG - 06/2021
#    ...

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import shapefile
import shapely.geometry as geometry
from pdb import set_trace

ShpDir = "/home/tangwh/datasets/china_shp/new/data/CHN_adm1.shp"

class Maskout(object):
    def __init__(self, LON, LAT, Region_list, ShpDir = ShpDir):
        self.ShpDir = ShpDir
        self.shp = shapefile.Reader(self.ShpDir)
        assert LON.shape == LAT.shape

        self.Region_list = Region_list 
        self.LON, self.LAT = LON, LAT
        self.nlat, self.nlon = LON.shape

        self.LONf = LON.flatten()
        self.LATf = LAT.flatten()

        self.points = []
        for ilon, ilat in zip(self.LONf, self.LATf):
            self.points.append(geometry.Point([ilon, ilat]))

        self.valid_regions = []
        for rcd in self.shp.shapeRecords():
            if rcd.record[4] in Region_list:
                self.valid_regions.append(geometry.shape(rcd.shape))

        self.mask_array = None
        self.search_valid_points()
        #print("Successfully create maskout object of " + str(Region_list))
            

    def search_valid_points(self):
        valid_point_ind = []
        for igrid, point in enumerate(self.points):
            #print(igrid, len(self.points))
            isValid = False
            for region in self.valid_regions:
                if point.within(region):
                    isValid = True
                    break
            if isValid:
                valid_point_ind.append(igrid)
        self.valid_point_ind = np.array(valid_point_ind)

    def mask_array_out(self, valid = 1, invalid = 0):
        if self.mask_array is not None:
            return self.mask_array.copy()

        mask_array = np.full((len(self.points)), invalid)
        mask_array[self.valid_point_ind] = valid
        mask_array = mask_array.reshape(self.nlat, self.nlon)
        self.mask_array = mask_array
        return self.mask_array.copy()

    def plot(self):
        if self.mask_array is None:
            self.mask_array_out()
        plt.pcolormesh(self.LON, self.LAT, self.mask_array)
        plt.show()



if __name__ == "__main__":
    ds = xr.open_dataset("/home/tangwh/modeling/BIS_v5.0/output/prior/Prior_2020-08-10_17:00:00.nc")
    lon = ds.lon.values
    lat = ds.lat.values
    a = Maskout(lonlist = lon, latlist = lat, Region_list = ["Beijing"])
    print(a)

