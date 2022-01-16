#!/usr/bin/env python
import numpy as np
class domain:
    """
    WRF-CO2 latlon domain class.
    Authors:
      Wenhan Tang - 11/2020 (Original Version)
      ...  
    """
    def __init__(self, input_dic):

        # Set global variables.

        # Parent grid ratio offset value (pr_offset)
        # Used to modify the value of parent_grid_ratio by add(minus) 1, if parent_grid_ratio is and even, which doesn't meet the requirements of real data simulation in WRF.
        # set it to zeros means ignoring this problem, it is legal only if the feed_back = 0 in ideal data simulation. 
        self.pr_offset = 1 # set 1, -1 or 0
        assert self.pr_offset in [-1,0,1], "pr_offset must be one of -1, 0, 1"

        # Check the input value.
        assert "lon_s" in input_dic
        assert "lon_e" in input_dic
        assert "lat_s" in input_dic
        assert "lat_e" in input_dic
        assert "dlon" in input_dic
        assert "dlat" in input_dic
        assert "name" in input_dic
        lon_s = input_dic["lon_s"]
        lon_e = input_dic["lon_e"]
        lat_s = input_dic["lat_s"]
        lat_e = input_dic["lat_e"]
        dlon = input_dic["dlon"]
        dlat = input_dic["dlat"]
        name = input_dic["name"]
        
        # Check the name.
        self.name = name
        assert len(name) == 3 and name[0] == "d", "Domain name format error!"
        self.domid = int(self.name[1:])

        if self.domid == 1:
            self.first_dom = True
    
        # Check the region configure.
        assert lat_s >= -90 and lat_s <= 90 and lat_e >= -90 and lat_e <= 90, "Latitude must be >= -90 and <=90."
        assert lon_s >= -180 and lon_s <= 180 and lon_e >= -180 and lon_e <= 180, "Lontitude must be >= -180 and <= 180."
        assert lat_e > lat_s, "lat_e must be larger than lat_s."
        self.lat_s = lat_s
        self.lat_e = lat_e

        # Whether the domain spans across the 180-degrees line
        if lon_s > lon_e:
            self.cross_180 = True
        else:
            self.cross_180 = False
        if self.cross_180:
            self.lon_e = lon_e + 360
        else:
            self.lon_e = lon_e
        self.lon_s = lon_s
        assert self.lon_e > self.lon_s, "lon_e can't equal to lon_s."
       
        assert dlon > 0
        assert dlat > 0
        self.dlon = dlon
        self.dlat = dlat
        #### Within the coordinate defined in this class,
        #### longitude variables (lon_s, lon_e) have the value between -180 and 540,
        #### latitude vairables (lat_s, lat_e) have the values between -90 and 90.
        #### You can imagine there are two world maps (from -180 to 180) concatenating horizontally.
        #### left: -180 -> 0 -> 180, right: 180 -> 360 -> 540.
      
        # Caculate the center point.
        self.lon_c = (self.lon_s + self.lon_e) / 2.0
        self.lat_c = (self.lat_s + self.lat_e) / 2.0
        
        # Caculate nx, ny.
        self.nx = round((self.lon_e - self.lon_s) / self.dlon) + 1
        self.ny = round((self.lat_e - self.lat_s) / self.dlat) + 1
        assert self.nx >= 1
        assert self.ny >= 1
        # Initialize the nesting configures.
        self.pid = 1
        self.ips = 1
        self.jps = 1
        self.parent_ratio = 1
        self.firstdom_ratio = 1

        if self.domid == 1:
            self.justify_boundary()

    def justify_boundary(self):
        # fine tunning the boundary features. (lon_s, lon_e, lat_s, lat_e)
        # Of course, user did have set the boundary features such as lon_s, lon_e ..., but with the specfic resolution, we should fine tune these boundary features to let both nx and ny are integer.
        # The center point of domain remains unchanged during the fine tunning.
        true_lon_s = self.lon_c - (self.nx - 1) * self.dlon / 2
        true_lon_e = self.lon_c + (self.nx - 1) * self.dlon / 2
        true_lat_s = self.lat_c - (self.ny - 1) * self.dlat / 2
        true_lat_e = self.lat_c + (self.ny - 1) * self.dlat / 2
        if true_lon_s != self.lon_s:
            print("SetDomLib: Modify " + self.name + " \"lon_s\" from " + str(self.lon_s) + " to " + str(true_lon_s))
            self.lon_s = true_lon_s
        if true_lon_e != self.lon_e:
            print("SetDomLib: Modify " + self.name + " \"lon_e\" from " + str(self.lon_e) + " to " + str(true_lon_e))
            self.lon_e = true_lon_e
        if true_lat_s != self.lat_s:
            print("SetDomLib: Modify " + self.name + " \"lat_s\" from " + str(self.lat_s) + " to " + str(true_lat_s))
            self.lat_s = true_lat_s
        if true_lat_e != self.lat_e:
            print("SetDomLib: Modify " + self.name + " \"lat_e\" from " + str(self.lat_e) + " to " + str(true_lat_e))
            self.lat_e = true_lat_e

    def __repr__(self):
        outshow = "\n<object: WRF-CO2 latlon grid domain class>\n\n"
        outshow += "name = " + self.name + "\n\n"
        outshow += "region:\n"
        outshow += str(self.lon_s) + " -> " + str(self.lon_e) + "\n"
        outshow += str(self.lat_s) + " -> " + str(self.lat_e) + "\n\n"
        outshow += "Resolution:\n"
        outshow += str(self.dlon) + " x " + str(self.dlat) + "\n\n"
        outshow += "center:\n"
        outshow += "( " + str(self.lon_c) + " , " + str(self.lat_c) + " )\n\n"
        outshow += "nesting:\n"
        outshow += "nx = " + str(self.nx) + "\n"
        outshow += "ny = " + str(self.ny) + "\n"
        outshow += "parent_id = " + str(self.pid) + "\n"
        outshow += "i_parent_start = " + str(self.ips) + "\n"
        outshow += "j_parent_start = " + str(self.jps) + "\n"
        outshow += "parent_grid_ratio = " + str(self.parent_ratio) + "\n"
        outshow += "firstdom_ratio = " + str(self.firstdom_ratio) + "\n\n"
        return outshow

    def __str__(self):
        return self.__repr__()

    def is_contain(self,pdom):
        contain = False
        if self.cross_180:
            if self.lon_s >= pdom.lon_s and self.lon_e <= pdom.lon_e and self.lat_s >= pdom.lat_s and self.lat_e <= pdom.lat_e:
                contain = True
        else:
            if self.lon_s >= pdom.lon_s and self.lon_e <= pdom.lon_e and self.lat_s >= pdom.lat_s and self.lat_e <= pdom.lat_e:
                contain = True
            else:
                if self.lon_s + 360 >= pdom.lon_s and self.lon_e + 360 <= pdom.lon_e and self.lat_s >= pdom.lat_s and self.lat_e <= pdom.lat_e:
                    contain = True
        return contain

    def nesting(self, pdoms):
        # make a dictionary like {"d01":dom1, "d02":dom2, "d03":dom3}
        pdoms_dic = {}
        for idom in pdoms:
            pdoms_dic[idom.name] = idom
        # search for the parent domain
        # What is the parent domain of a specific domain ("domain A" represents the specific domain ):
        # 1. The id is smaller than the id of domain A.
        # 2. Must contain domain A. (i.e. parent_domain_of_A.is_contain(A) == True)
        # 3. If there are many domains meet the above requirements, the domain which has the neareast id (i.e. has the largest id number) can be the parent domain of A.

        have_parent = False
        for id_search in range(self.domid - 1, 0, -1):
            name_search = "d" + str(id_search).zfill(2)
            assert name_search in pdoms_dic, name_search + " not found in parent domain list"
            if self.is_contain(pdoms_dic[name_search]):
                have_parent = True
                self.pid = id_search
                parent = pdoms_dic[name_search]
                break
        assert have_parent, "Can not find a parent domain of " + self.name
        
        # Caculate the parent grid ratio
        self.parent_ratio = round(parent.dlon / self.dlon)

        # Check if the parent_grid_ratio computed by longitude is consistent with it computed by latitude. (if not, raise a fatal error)
        # I think maybe just raising a warning (not an error) here is better, because dlat would be modified by self.parent_ratio, if they are conflict, use the value of parent.dlon / self.dlon as parent_ratio and adjust the value of dlat. 
        #                                                                     --- Wenhan Tang - 2020/12/17
        #assert self.parent_ratio == round(parent.dlat / self.dlat), "ratio dlon/dlat of " + self.name + " conflict with " + parent.name
        if not(self.parent_ratio == round(parent.dlat / self.dlat)):
            print("Warning !!! ratio dlon/dlat of " + self.name + " conflict with " + parent.name + ", use the value of parent.dlon / self.dlon as \"parent_ratio\" and adjust the dlat of " + self.name + " later.")

        # Check if parent_grid_ratio is even. (if not, raise a warning)
        if np.mod(self.parent_ratio,2) == 0:
            print("SetDomLib: Warning !!! " + self.name + " parent_grid_ratio is even, which doesn't meet the requirements of real data simulation.")
            print("SetDomLib: modigy the parent_grid_ratio by adding " + str(self.pr_offset))
            self.parent_ratio += self.pr_offset

        self.firstdom_ratio = self.parent_ratio * parent.firstdom_ratio
        
        # Check if dlon and dlat should be justified.
        if self.dlon * self.parent_ratio != parent.dlon:
            true_dlon = parent.dlon / self.parent_ratio
            print("SetDomLib: Modify " + self.name + " \"dlon\" from " + str(self.dlon) + " to " + str(true_dlon))
            self.dlon = true_dlon

        if self.dlat * self.parent_ratio != parent.dlat:
            true_dlat = parent.dlat / self.parent_ratio
            print("SetDomLib: Modify " + self.name + " \"dlat\" from " + str(self.dlat) + " to " + str(true_dlat))
            self.dlat = true_dlat

        # Recaculate nx, ny after changing of dlon and dlat.
        self.nx = round((self.lon_e - self.lon_s) / self.dlon) + 1
        self.ny = round((self.lat_e - self.lat_s) / self.dlat) + 1

        # Check if the nx-1 and ny-1 is an interger mutiple of parent_grid_ratio, nest should end on mother grid domain point.
        if np.mod(self.nx - 1,self.parent_ratio) != 0:
            nx_near = round((self.nx - 1) / self.parent_ratio) * self.parent_ratio + 1
            print("SetDomLib: Modify " + self.name + " \"nx\" from " + str(self.nx) + " to " + str(nx_near))
            self.nx = nx_near



        if np.mod(self.ny - 1, self.parent_ratio) != 0:
            ny_near = round((self.ny - 1) / self.parent_ratio) * self.parent_ratio + 1
            print("SetDomLib: Modify " + self.name + " \"ny\" from " + str(self.ny) + " to " + str(ny_near))
            self.ny = ny_near

        self.justify_boundary()
        # Caculate the i_parent_start and j_parent_start
        # By the same time, caculate the moving offset.
        if self.lon_s < parent.lon_s:
            print("Extending longitude coordinates ...")
            self.ips = round((self.lon_s + 360 - parent.lon_s) / parent.dlon) + 1
            #print("lon_s before mod:", self.lon_s)
            #print("lon_s after mod:" ,(self.ips - 1) * parent.dlon +  parent.lon_s - 360)
            offset_x = (self.ips - 1) * parent.dlon +  parent.lon_s - 360 - self.lon_s

        else:
            self.ips = round((self.lon_s - parent.lon_s) / parent.dlon) + 1
            #print("lon_s before mod:", self.lon_s)
            #print("lon_s after mod:" ,(self.ips - 1) * parent.dlon +  parent.lon_s)
            offset_x = (self.ips - 1) * parent.dlon +  parent.lon_s - self.lon_s


        self.jps = round((self.lat_s - parent.lat_s) / parent.dlat) + 1
        #print("lat_s before mod:", self.lat_s)
        #print("lat_s after mod:" ,(self.jps - 1) * parent.dlat +  parent.lat_s)
        offset_y = (self.jps - 1) * parent.dlat +  parent.lat_s - self.lat_s

        # Move the child domain to align the nesting point in parent domain.
        print("SetDomLib: Nesting move of " + self.name + " offset_x = " + str(offset_x))
        self.lon_s = self.lon_s + offset_x
        self.lon_e = self.lon_e + offset_x
        self.lon_c = (self.lon_s + self.lon_e) / 2

        print("SetDomLib: Nesting move offset_y = " + str(offset_y))
        self.lat_s = self.lat_s + offset_y
        self.lat_e = self.lat_e + offset_y
        self.lat_c = (self.lat_s + self.lat_e) / 2
