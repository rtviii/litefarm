#!/usr/bin/python3
def dir_path(string):
    if string == "0":
        return None
    if os.path.isdir(string):
        return string
    else:
        try:
            if not os.path.exists(string):
                os.makedirs(string, exist_ok=True)
                return string
        except:
            raise PermissionError(string)
import pickle
import numpy as np
from shapely.ops import unary_union
import os, sys
from pprint import pprint
from matplotlib.patches import Patch, Polygon
import matplotlib.pyplot as plt
from typing import List, Mapping
from scripts.farm_plot_locs import farm_get_area, locations_to_polygons, LOCTYPES
from farm import Farm, farm_profile, get_farm_locs
import matplotlib.pyplot as plt


fid           = sys.argv[1]
farmlocs      = get_farm_locs(fid)
total_area    = unary_union(locations_to_polygons(farmlocs, get_list=True)).area
polygons      = locations_to_polygons(farmlocs)
lentotal_dict = 0


pklpath = lambda farm_id: '/home/rxz/dev/litefarm/farms_prod/{}.pickle'.format(farm_id)

D = {
    # in square meters
    'total_area': total_area,
    'farm_id'   : fid,
    'locations' : locations_to_polygons (farmlocs),
}

with open(pklpath(fid), 'wb') as infile:
    pickle.dump(D, infile)
    print("Saved farm {}".format(fid) )



