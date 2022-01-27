from copyreg import pickle
import os
from pprint import pprint
import sys
import geopandas
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, LineString, Point
import json
from pprint import pprint
import psycopg2
import dotenv
from typing import List

# """
# The schema is roughly this:

# farm_id   -> List[locations]
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

farmid = sys.argv[1]
def get_farm_locs(farm_id:str)->List:
    CUR.execute("""SELECT fig.type, area.grid_points, ln.line_points , pt.point
    FROM "userFarm" ufarm
    JOIN  "location" loc ON ufarm.farm_id    = loc.farm_id
    JOIN  "figure" fig ON  fig.location_id   = loc.location_id
    FULL  JOIN "area" area on area.figure_id = fig.figure_id
    FULL  JOIN "line" ln  on ln.figure_id    = fig.figure_id
    FULL  JOIN "point" pt  on pt.figure_id   = fig.figure_id 
    where ufarm.farm_id='%s'""" % farm_id)

    resp      = CUR.fetchall()
    farm_objects = []

    for datum in resp:
        (type,grid_points,line_points, point) =datum
        if location_categories[type] ==  'area':
            farm_objects.append({
                "type"  : type,
                "coords": grid_points})
        elif location_categories[type] ==  'line':
            farm_objects.append({
            "type"  : type,
            "coords": line_points
            })
        if location_categories[type] ==  'point':
            farm_objects.append({
                "type"  : type,
                "coords": [ point ]                })
        
    print(farm_objects)
    return farm_objects

# ex. farm_id = "094a2776-3109-11ec-ad47-0242ac130002"

farm_id = sys.argv[1]
r       = get_farm_locs(farm_id)
outpath = f"/home/rxz/dev/litefarm/locations/locations_{farm_id}.json"

if not os.path.exists(outpath):
    with open(outpath, 'w') as outfile:
        json.dump(r, outfile)



# class Location:
#     location_id : str
#     location_cat: str  # point | area | line
#     figure_id   : str
#     figure_type : str
#     farm_id     : str

#     def __init__(self,
#                  location_id: str,
#                  farm_id: str = '',
#                  ) -> None:
#         CUR.execute(
#             "SELECT figure_id, type FROM \"figure\" where location_id = \'%s\';" % location_id)
#         (figure_id, figure_type) = CUR.fetchone()
#         self.location_id = location_id
#         self.figure_id = figure_id
#         self.figure_type = figure_type
#         self.farm_id = farm_id

#     def get_farm_id(self) -> str:
#         if self.farm_id == '':
#             CUR.execute(
#                 "SELECT farm_id FROM \"locations\" where location_id = \'%s\';" % self.location_id)
#             self.farm_id = CUR.fetchone()[0]
#         return self.farm_id

#     def yield_coordinates(self)->dict:
#         ...

#     def __repr__(self) -> str:

#         return """  
#         location: \033[95m{}\033[0m

#         figure_id  : \033[95m{}\033[0m
#         farm_id    : \033[95m{}\033[0m
#         figure_type: \033[94m{} ({})\033[0m

#         """.format(self.location_id,self.figure_id,self.farm_id,self.figure_type, self.location_categories[self.figure_type])
# class Area(Location):

#     grid_points: List[dict]
#     total_area : int
#     perimeter  : int

#     def __init__(self, location_id: str, farm_id: str,
#                  ) -> None:
#         super().__init__(location_id, farm_id)
#         CUR.execute('SELECT * FROM "area" where figure_id = \'%s\';' %
#                     self.figure_id)
#         (_, total_area, grid_points, perimeter,
#          total_area_unit, perimeter_unit) = CUR.fetchone()

#         self.grid_points = grid_points
#         self.total_area  = total_area
#         self.perimeter   = perimeter

#     def yield_coordinates(self):
#         return self.grid_points
# class Line(Location):

#     line_points: List[dict]
#     length: int
#     width: int

#     def __init__(self, location_id: str, farm_id: str) -> None:
#         super().__init__(location_id, farm_id)
#         CUR.execute('SELECT * FROM "line" where figure_id = \'%s\';' %
#                     self.figure_id)
#         (_, length, width, line_points, length_unit, width_unit,
#          total_area, total_area_unit) = CUR.fetchone()

#         self.line_points = line_points
#         self.width = width
#         self.length = length

#     def yield_coordinates(self):
#         return self.line_points
# class Point(Location):
#     point = dict

#     def __init__(self, location_id: str, farm_id: str) -> None:
#         super().__init__(location_id, farm_id)
#         CUR.execute('SELECT * FROM "point" where figure_id = \'%s\';' %
#                     self.figure_id)
#         (_, point) = CUR.fetchone()
#         self.point = point
#     def yield_coordinates(self):
#         return self.point

# class Farm:

    # location_categories: dict = {

    #     # maps figure_type to location_category
    #     # i.e. barn -> area etc.
    #     "farm_site_boundary": "area",
    #     "field": "area",
    #     "garden": "area",
    #     "barn": "area",
    #     "greenhouse": "area",
    #     "natural_area": "area",
    #     "surface_water": "area",
    #     "residence": "area",
    #     "ceremonial_area": "area",

    #     # ------------
    #     "fence": "line",
    #     "watercourse": "line",
    #     "buffer_zone": "line",
    #     # "road"       : "line",
    #     # "footpath"   : "line",

    #     # -----
    #     "water_valve": "point",
    #     "gate": "point",
    # }

    # farm_id: str
    # locations: List[Location]

    # def __init__(self,
    #              farm_id: str,
    #              ) -> None:

    #     self.farm_id = farm_id
    #     self.locations = []

    # def get_locations(self) -> List[Location]:
        # if self.locations == []:
        #     CUR.execute("""select type, location.location_id from "location" join "figure" on location.location_id = figure.location_id where farm_id = \'%s\'""" % self.farm_id)
        #     type_locids = CUR.fetchall()
        #     print(type_locids)
        #     def class_from_locid(type:str,loc_id:str):
        #         if type == "area":
        #             return Area(loc_id,self.farm_id)
        #         if type == "line":
        #             return Line(loc_id,self.farm_id)
        #         if type == "point":
        #             return Point(loc_id,self.farm_id)
        #     locs = [*map(lambda tpl : class_from_locid(self.location_categories[tpl[0]], tpl[1]),type_locids)]
        #     self.locations = locs
        # return self.locations
# farm = Farm('094a2776-3109-11ec-ad47-0242ac130002')

# x = farm.get_locations()
# for _ in x:
#     pprint(_.yield_coordinates())
