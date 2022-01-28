from cmath import pi
from enum import unique
import os
from pprint import pprint
import sys
from typing import List, Mapping
import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import json

# plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':100})

location_categories: dict = {
    # ------------------- Area
   "farm_site_boundary": "area",
    "field"             : "area",
    "garden"            : "area",
    "barn"              : "area",
    "greenhouse"        : "area",
    "natural_area"      : "area",
    "surface_water"     : "area",
    "residence"         : "area",
    "ceremonial_area"   : "area",
    # ------------ Line
      "fence"      : "line",
      "watercourse": "line",
      "buffer_zone": "line",
    # "road"       : "line",
    # "footpath"   : "line",

    # ----- Point

    "water_valve": "point",
    "gate"       : "point",
}

def is_self_intersecting(E: List[Point])->bool:
    """
    E: a collection of shapely Point objects (projected from lat/lon via basemap)
    True if a polygon has lines that intersect anywhere except endpoints else false.
    """
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

def farm_get_objects(farm_locations:List[dict])->dict:
    """Return a location_type->List[Polygon] mapping given @farm_locations of shape  
    ```json
    {
        type: str 
        lat: float
        lng: float
    }
    ```
    
    """
    # sinusoid projection for converting lon/lat to metric
    m = Basemap(projection='sinu',lon_0=0,resolution='c') 
    farm_objects = {
        'barns' : [],
        'fields': [],
        "other" : []
    }
    areas            = []
    # selfintersecting = [] 
    for datum in farm_locations:
        if location_categories[ datum['type'] ] in  [ 'area', 'line' ] :
            try:
                pts  = [*map(lambda i : Point(np.round(m(i['lng'],i['lat'] ),4)), datum['coords'])]
                poly = Polygon(pts)
                if is_self_intersecting(pts):
                    # selfintersecting.append(poly)
                    continue
                areas.append(poly)
                if datum['type'] == "field":
                    if not any(p.equals(poly) for p in farm_objects['fields']):
                        farm_objects['fields'].append(poly)
                if datum['type'] == "barn":
                    if not any(p.equals(poly) for p in farm_objects['barns']):
                        farm_objects['barns'].append(poly)
                else:
                    if not any(p.equals(poly) for p in farm_objects['other']):
                        farm_objects['other'].append(poly)
            except Exception:
                # print("Likely not enough points to construct a polygon")
                ...

    uniq_areas = [] # Filter out duplicate areas
    for poly in areas:
        if not any(p.equals(poly) for p in uniq_areas):
            uniq_areas.append(poly)
    return farm_objects

def farm_get_area(objects)->float:
    """Return scalar area in square meters given a list of polygons (possibly overlapping)"""
    # unary_union dissolved overlapping polygons into one

    if type(objects)==dict:
        all_poly = [];[all_poly.extend(list_of_poly) for list_of_poly in objects.values()]
        return unary_union(all_poly).area
    elif type(objects)==list:
        return unary_union(farm_get_objects).area 
    else:
        print("Pass either a list or dict with farm location polygons")
        exit(1)



def plot_farm(
    farm_objects:Mapping[str, List[Polygon]], 
    **kwargs):
    """
    --merged to display unary_union
    """

    # ideally this bit is a comprehension over all types of loc.. gardens etc

    other  = geopandas.GeoSeries(farm_objects['other'])
    fields = geopandas.GeoSeries(farm_objects['fields'])
    barns  = geopandas.GeoSeries(farm_objects['barns'])

    if kwargs.pop('merged', False):
        other  = geopandas.GeoSeries(unary_union(farm_objects['other']))
        fields = geopandas.GeoSeries(unary_union(farm_objects['fields']))
        barns  = geopandas.GeoSeries(unary_union(farm_objects['barns'] ))


    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    other.plot(color=None,ax=ax,edgecolor='k',linewidth = 0.5, facecolor='none')
    fields.plot(color=None,ax=ax,edgecolor='green',linewidth = 0.5, facecolor='none')
    barns.plot(color=None,ax=ax,edgecolor='orange',linewidth = 0.5, facecolor='none')

    if kwargs.pop('savepath', False):
        plt.savefig(kwargs['savepath'], bbox_inches='tight')
    plt.show()




farmlocs_path = sys.argv[1]
with open(farmlocs_path,'rb') as infile:
    data = json.load(infile)
objs = farm_get_objects(data['locations'])
pprint(objs)


plot_farm(objs)
print(farm_get_area(objs))
