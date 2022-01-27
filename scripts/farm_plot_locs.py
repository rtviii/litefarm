from cmath import pi
import os
from pprint import pprint
import sys
from typing import List
import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np

import json

plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':100})

location_categories: dict = {


    # maps figure_type to location_category
    # i.e. barn -> area etc.
    "farm_site_boundary": "area",
    "field"             : "area",
    "garden"            : "area",
    "barn"              : "area",
    "greenhouse"        : "area",
    "natural_area"      : "area",
    "surface_water"     : "area",
    "residence"         : "area",
    "ceremonial_area"   : "area",

    # ------------
      "fence"      : "line",
      "watercourse": "line",
      "buffer_zone": "line",
    # "road"       : "line",
    # "footpath"   : "line",

    # -----
    "water_valve": "point",
    "gate"       : "point",
}

farmlocs_path = sys.argv[1]
# farmlocs_path= "/home/rxz/dev/litefarm/locations/locations_26608372-54ab-11eb-9564-22000ab2b8c4.json"

with open(farmlocs_path) as infile:
    data = json.load(infile)

m = Basemap(projection='sinu',lon_0=0,resolution='c')
farm_objects = {
    'barns' : [],
    'fields': [],
    "other" : []
}

def is_self_intersecting(E: List[Point])->bool:
    ll = len(E)
    if ll < 3:
        return False
    i = 0;
    while i <= ll-2:
        current_ls = LineString([E[i],E[i+1]] )
        for j in range((i+1),ll):
            if j == ll-1:
                # print("comparing against the wraparound")
                against_ls = LineString([ 
                    E[j],
                    E[0]
                ])
            else:
                # print(f"I is {i} to {i+1}")
                # print(f"J is {j} to {j+1}")
                against_ls = LineString([E[j], E[j+1]])


            if against_ls.intersects(current_ls):
                pt_of_intersection = against_ls.intersection(current_ls)
                assume_is_edge = False
                for pt in E:
                    if pt.almost_equals(pt_of_intersection):
                        assume_is_edge = True
                if assume_is_edge == False:
                    return True
                # print("Yep, one of the edges")


        i = i+1
    return False





    


areas = []
for datum in data:
    # print(datum['coords'])
    if location_categories[ datum['type'] ] in  [ 'area', 'line' ] :
        try:
            poly = Polygon([*map(lambda i : np.round(m(i['lng'],i['lat'] ),4), datum['coords'])])
            areas.append(poly)



            points = [*map(lambda i : Point(np.round(m(i['lng'],i['lat'] ),4)), datum['coords'])]
            print("Intersects self:" ,is_self_intersecting(points))
            # print("line string:",LineString([points[0],points[1], points[2]]))

            if datum['type'] == "field":
                farm_objects["fields"].append(poly)
            if datum['type'] == "barn":
                farm_objects["barns"].append(poly)
            else:
                farm_objects['other'].append(poly)
        except Exception:
            # print("Not enough points to construct a polygon")
            ...

fig, ax = plt.subplots()
ax.set_aspect('equal')
# all_areas = [ *farm_objects['fields'], *farm_objects['barns'], *farm_objects['other'] ]


# print(unary_union(farm_objects['barns']))

geopandas.GeoSeries(unary_union(farm_objects['barns'])).plot(color=None,ax=ax,edgecolor='k',linewidth = 0.5, facecolor='none')
print("Area of unary union:",unary_union(farm_objects['barns']).area)
print("Area of unary union:",unary_union(farm_objects['fields']).area)
# print("Area of unary union:",unary_union(farm_objects['other']).area)


# Filter duplicates:
uniq_other = []
for poly in farm_objects['other']:
    if not any(p.equals(poly) for p in uniq_other):
        uniq_other.append(poly)

print("uniq", len(uniq_other))

geopandas.GeoSeries(uniq_other).plot(color=None,ax=ax,edgecolor='k',linewidth = 0.5, facecolor='none')
# geopandas.GeoSeries(farm_objects['other']).plot(color=None,ax=ax,edgecolor='k',linewidth = 0.5, facecolor='none')
geopandas.GeoSeries(unary_union(farm_objects['fields'])).plot(color=None,ax=ax,edgecolor='green',linewidth = 0.5, facecolor='none')
geopandas.GeoSeries(unary_union( farm_objects['barns'] )).plot(color=None,ax=ax,edgecolor='orange',linewidth = 0.5, facecolor='none')
# gpd.GeoSeries([ Point(14047665.998083537,5433135.0446869321) ]).plot(color='red',ax=ax,edgecolor='orange')
plt.show()

# print("area of fields is", np.round(fields.area, 3))

# fields.plot(ax=ax,color=None,edgecolor='green',linewidth = 1, facecolor='green', alpha=0.2);
# barns.plot(ax=ax,color=None,edgecolor='orange',linewidth = 1, facecolor='orange',alpha=0.2);
# other.plot(color=None,ax=ax,edgecolor='k',linewidth = 0.5, facecolor='none');

# print("Showing ", sys.argv[1])
# plt.savefig(f'{os.path.basename(farmlocs_path)[0:-5]}.png', bbox_inches='tight')



# ---------------------------------- AREA CALCULATIONS as per https://gis.stackexchange.com/a/413350/162472
#  b4c9ceb6-2e6e-11ea-9a69-22000b628b95 |  330
#  0ad0ce20-3112-11ec-b36e-0242ac130002 |  248
#  353f0b9e-5c6a-11ec-8795-0242ac130002 |  203
#  2d930078-31a7-11ec-b8f3-0242ac130002 |  180
#  094a2776-3109-11ec-ad47-0242ac130002 |  159
#  06f0c1c8-329f-11ec-a4ff-0242ac130002 |  136
#  26608372-54ab-11eb-9564-22000ab2b8c4 |  135
#  ca713386-3050-11ec-b23b-0242ac130002 |  120


