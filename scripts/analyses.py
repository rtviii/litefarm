#!/usr/bin/python3

from cmath import inf
from json import load
import os
import sys
from typing import List
from matplotlib import pyplot as plt
from matplotlib.patches import Patch, Polygon
from shapely.ops  import unary_union
import seaborn as sns

from farm import Farm, farm_profile

def farm_ids()->List[str]:
    with open("/home/rxz/dev/litefarm/resources/farm_ids.txt",'r', encoding='utf-8') as infile:
        lines = list(map(str.strip,infile.readlines()))
        return lines

# with open(f'/home/rxz/dev/litefarm/farms/{sys.argv[1]}.pickle', 'wb') as handle:
#     pickle.dump(farm_profile(sys.argv[1]), handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open(sys.argv[1], 'rb') as infile:
#     p = pickle.load(infile)
#     print(p)



