import os
from pprint import pprint
import sys
import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, Point
import json


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
with open(farmlocs_path) as infile:
    data = json.load(infile)

farm_objects = {}
for datum in data:

    if datum['type'] not in farm_objects:
        farm_objects[datum['type']]=[]
    if location_categories[ datum['type'] ] ==  'area':
        print()
        coords = datum['coords']
        try:
            farm_objects[datum['type']].append(Polygon([*map(lambda i : (i['lng'],i['lat'] ), coords)]))
        except:
            ...
    # elif location_categories[ datum['type'] ] ==  'line':
    #     coords = datum['line_points']
    #     try:
    #         farm_objects[datum['type']].append(LineString([*map(lambda i : (i['lng'],i['lat'] ), coords)]))
    #     except:
    #         ...
    # if location_categories[ datum['type'] ] ==  'point':
    #     x = datum['point']['lng']
    #     y = datum['point']['lat']
    #     try:
    #         farm_objects.append(Point(x,y))
    #     except:
    #         ...

# pprint(farm_objects)
# map(lambda kv: farm_objects.update({kv[0]:geopandas.GeoSeries(kv[1])}), farm_objects.items()  )
# pprint(farm_objects)

# all objects:
all = []
for i in farm_objects:
    print(i)
    if i != 'barn' and i != "field":
        all = [*all, *farm_objects[i]]

plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':100})
other  = geopandas.GeoSeries(all)
barns  = geopandas.GeoSeries(farm_objects['barn'])
fields = geopandas.GeoSeries(farm_objects['field'])

# s = geopandas.GeoSeries(farm_objects) 


fig, ax = plt.subplots()
ax.set_aspect('equal')
fields.plot(ax=ax,color=None,edgecolor='green',linewidth = 1, facecolor='green', alpha=0.2);
barns.plot(ax=ax,color=None,edgecolor='orange',linewidth = 1, facecolor='orange',alpha=0.2);
other.plot(color=None,ax=ax,edgecolor='k',linewidth = 0.5, facecolor='none');


# plt.show()
plt.savefig(f'{os.path.basename(farmlocs_path)[0:-5]}.png', bbox_inches='tight')
