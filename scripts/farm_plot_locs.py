from typing import List, Mapping
from shapely.geometry import Polygon, LineString, Point 
from shapely.ops import unary_union
from mpl_toolkits.basemap import Basemap
import numpy as np

LOCTYPES: dict = {
    # maps figure_type to location_category
    # i.e. barn -> area etc.
    "farm_site_boundary" : { "loctype":"area" , "color":"indigo"    },
    "field"              : { "loctype":"area" , "color":"green"     },
    "garden"             : { "loctype":"area" , "color":"indianred" },
    "barn"               : { "loctype":"area" , "color":"orange"    },
    "greenhouse"         : { "loctype":"area" , "color":"olive"     },
    "natural_area"       : { "loctype":"area" , "color":"seagreen"  },
    "surface_water"      : { "loctype":"area" , "color":"royalblue" },
    "residence"          : { "loctype":"area" , "color":"peru"      },
    "ceremonial_area"    : { "loctype":"area" , "color":"orchid"    },

    "fence"              : { "loctype":"line" , "color":"yellow"    },
    "watercourse"        : { "loctype":"line" , "color":"aquamarine"},
    "buffer_zone"        : { "loctype":"line" , "color":"darkgrey"  },

    "water_valve"        : { "loctype":"point", "color":"blue"      },
    "gate"               : { "loctype":"point", "color":"khaki"     },
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
                    if pt.equals(pt_of_intersection):
                        assume_is_edge = True
                if assume_is_edge == False:
                    return True
                # print("Yep, one of the edges")
        i = i+1
    return False
def locations_to_polygons(farm_locations:List[dict])->dict:
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

    m            = Basemap(projection='sinu',lon_0=0,resolution='c')
    farm_objects = {

    }

    for datum in farm_locations:
        try:
            pts  = [*map(lambda i : Point(np.round(m(i['lng'],i['lat'] ),4)), datum['coords'])]
            poly = Polygon(pts)
            if is_self_intersecting(pts):
                continue
            loctype = datum['type']
            if loctype not in farm_objects:
                farm_objects[loctype] = []

            if not any(p.equals(poly) for p in farm_objects[loctype]):
                farm_objects[loctype].append(poly)
        except Exception:
            ...
    return farm_objects

def farm_get_area(objects)->float:
    """Return scalar area in square meters given a list of polygons (possibly overlapping)"""
    # unary_union dissolved overlapping polygons into one
    if type(objects)==dict:
        all_poly = [];[all_poly.extend(list_of_poly) for list_of_poly in objects.values()]
        return unary_union(all_poly).area
    elif type(objects)==list:
        return unary_union(objects).area 
    else:
        print("Pass either a list or dict with farm location polygons")
        exit(1)



