#!/usr/bin/python3

import pickle
from dataclasses import dataclass
from dacite import from_dict
import geopandas as gpd
from shapely.ops import unary_union
import os
from pprint import pprint
from matplotlib.patches import Patch, Polygon
import matplotlib.pyplot as plt
import psycopg2
import dotenv
from typing import List, Mapping
from farm_plot_locs import farm_get_area, locations_to_polygons, LOCTYPES

# """
# The schema is roughly this:
# farm_id   ----> List[locations]
# figure_id <---> location_id
#     location_id <- barn | field | garden       | greenhouse      | residence |
#                         | gate  | buffer_zone  | ceremonial_area | farm_site_boundary (all 50 of them)
#                         | fence | natural_area | surface_water   | water_valve | watercourse

#     figure_id   <- area | line  | point
# """

dotenv.load_dotenv('/home/rxz/.ssh/secrets.env')
connection = psycopg2.connect(
    dbname=os.environ.get("litefarm_db"),
    user=os.environ.get("litefarm_usr"),
    host=os.environ.get("litefarm_host"),
    port=os.environ.get("litefarm_port"),
    password=os.environ.get("litefarm_pwd"))

CUR = connection.cursor()

def get_farm_locs(farm_id:str)->List:
    CUR.execute("""
    SELECT fig.type, area.grid_points, ln.line_points , pt.point
    FROM "userFarm" ufarm
    JOIN  "location" loc ON ufarm.farm_id    = loc.farm_id
    JOIN  "figure" fig ON  fig.location_id   = loc.location_id
    FULL  JOIN "area" area on area.figure_id = fig.figure_id
    FULL  JOIN "line" ln  on ln.figure_id    = fig.figure_id
    FULL  JOIN "point" pt  on pt.figure_id   = fig.figure_id 
    where ufarm.farm_id='%s'""" % farm_id)
    resp         = CUR.fetchall()
    farm_objects = []

    for datum in resp:
        (_type,grid_points,line_points, point) =datum

        if LOCTYPES[_type]['loctype'] ==  'area':
            farm_objects.append({
                "type"  : _type,
                "coords": grid_points
            })

        elif LOCTYPES[_type]['loctype'] == 'line':
            farm_objects.append({
                "type"  : _type,
                "coords": line_points
            })

        elif LOCTYPES[_type]['loctype'] ==  'point':
            farm_objects.append({
                "type"  : _type,
                "coords": [ point ]                
            })
    return farm_objects

def farm_profile (farm_id:str)->dict:
    locations = get_farm_locs(farm_id)
    polygons  = locations_to_polygons(locations)
    return {
        "farm_id"   : farm_id,
        "locations" : polygons,
        "total_area": farm_get_area(polygons)
    }

@dataclass
class Location: 
      type    : str
      lng     : float
      lat     : float

class Farm:
    locations : dict
    total_area: float
    farm_id   : str
    def __init__(self, farm_id:str, pickled:dict={}) -> None:

        if pickled =={}:
            D = farm_profile(farm_id)
        else:
            D = pickled
        self.total_area = D['total_area']
        self.locations  = D['locations']
        self.farm_id    = D['farm_id']
        pprint(D)

    def plot_farm(
        self,
        **kwargs):
        """
        @merged=True to display unary_union
        """
        plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':100})
        fig, ax = plt.subplots(figsize=(4,4))
        ax.set_aspect('equal')
        legendPatches = [ ]

        for kvp in self.locations.items():
            loctype  = kvp[0]
            polygons = kvp[1]

            if kwargs.pop('merged', False):
                polygons = unary_union(polygons)

            gpd.GeoSeries(polygons).plot( 
                color     = None,
                ax        = ax,
                edgecolor = LOCTYPES[loctype]['color'],
                linewidth = 0.5,
                facecolor = 'none',
                )

            legendPatches.append(Patch(facecolor=LOCTYPES[loctype]['color'], label= loctype,))
        if kwargs.pop('savepath', False):
            plt.savefig(kwargs['savepath'], bbox_inches='tight')

        handles, _ = ax.get_legend_handles_labels()
        ax.legend(handles=[*handles,*legendPatches], loc='best')
        plt.show()

# farms:List[Farm] = []

# def farm_ids()->List[str]:
#     with open("/home/rxz/dev/litefarm/resources/farm_ids.txt",'r', encoding='utf-8') as infile:
#         lines = list(map(str.strip,infile.readlines()))
#         return lines

def load_farms()->List[Farm]:
    farms=[]
    for file in os.listdir('/home/rxz/dev/litefarm/farms/'):
        print("Opening {}".format(file))
        with open('/home/rxz/dev/litefarm/farms/'+file,'rb') as infile:
            d = pickle.load(infile)
            farm_id= d['farm_id']
            farms.append(Farm(farm_id, pickled=d))
    return farms

# all = farm_ids()
# for farm in all:
#     print(farm)
    # print(Farm(farm))

fms = load_farms()


filtered = [*filter(lambda f: f.total_area != 0, fms)]
f:Farm;

def alllocs(f:Farm):
    o = []
    for x in f.locations.values():
        o.append(list(x)) 
    return o

filtered_loc = [*filter(lambda f: len( alllocs(f) ) > 5, fms)]

filtered_loc.sort(key=int(len( Farm.locations )))
print(filtered_loc)


# areas = []
# for f in farms:
#     if 'barn' in f.locations and 'field' in f.locations:
#         dtm = {"barn_to_field": unary_union(f.locations['barn']).area/unary_union(f.locations['field']).area}
#         areas.append(f.total_area)
#     else:
#         print("False")
    

    
# sns.displot(areas)
# plt.show()

# afarm = farm_profile("094a2776-3109-11ec-ad47-0242ac130002")
# farm  = from_dict(data_class=Farm, data=afarm)

# farm.plot_farm(merged=True)

