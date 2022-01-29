#!/usr/bin/python3

from cmath import inf
from json import load
import os
import sys
from typing import List
from matplotlib import pyplot as plt
from matplotlib.patches import Patch, Polygon
import pickle
from shapely.ops  import unary_union
import seaborn as sns

from farm import Farm, farm_profile

# def farm_ids()->List[str]:
#     with open("/home/rxz/dev/litefarm/resources/farm_ids.txt",'r', encoding='utf-8') as infile:
#         lines = list(map(str.strip,infile.readlines()))
#         return lines

# with open(f'/home/rxz/dev/litefarm/farms/{sys.argv[1]}.pickle', 'wb') as handle:
#     pickle.dump(farm_profile(sys.argv[1]), handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open(sys.argv[1], 'rb') as infile:
#     p = pickle.load(infile)
#     print(p)

farms:List[Farm] = []
def load_farms():
    for file in os.listdir('/home/rxz/dev/litefarm/farms/'):
        try:
            with open('/home/rxz/dev/litefarm/farms/'+file,'rb') as infile:
                farms.append(Farm(pickle.load(infile)))
        except:
            ...
load_farms()



# "farm_site_boundary" : { "loctype":"area" , "color":"indigo"    },
# "field"              : { "loctype":"area" , "color":"green"     },
# "garden"             : { "loctype":"area" , "color":"indianred" },
# "barn"               : { "loctype":"area" , "color":"orange"    },
# "greenhouse"         : { "loctype":"area" , "color":"olive"     },
# "natural_area"       : { "loctype":"area" , "color":"seagreen"  },
# "surface_water"      : { "loctype":"area" , "color":"royalblue" },
# "residence"          : { "loctype":"area" , "color":"peru"      },
# "ceremonial_area"    : { "loctype":"area" , "color":"orchid"    },



areas = []
for f in farms:
    if 'barn' in f.locations and 'field' in f.locations:
        dtm = {"barn_to_field": unary_union(f.locations['barn']).area/unary_union(f.locations['field']).area}
        print(f.farm_id)
        areas.append(f.total_area)
        print(dtm)
        # print("True : {} fields. Area {}".format(len(f.locations['field']), ))
    else:
        print("False")
    

    
sns.displot(areas)
plt.show()

# labels  = 'Frogs', 'Hogs', 'Dogs', 'Logs'
# sizes   = [15, 30, 45, 10]
# explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

# fig1, ax1 = plt.subplots()
# ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',shadow=True, startangle=90)
# ax1.axis('equal')  

# plt.show()

