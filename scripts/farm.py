import os
from pprint import pprint
import psycopg2
import dotenv
from typing import List

"""
The schema is roughly this:

farm_id   -> List[locations]
figure_id <---> location_id

    location_id <- barn | field | garden       | greenhouse      | residence |
                        | gate  | buffer_zone  | ceremonial_area | farm_site_boundary (all 50 of them)
                        | fence | natural_area | surface_water   | water_valve | watercourse

    figure_id   <- area | line  | point
"""

dotenv.load_dotenv('/home/rxz/.ssh/secrets.env')
connection = psycopg2.connect(
    dbname=os.environ.get("litefarm_db"),
    user=os.environ.get("litefarm_usr"),
    host=os.environ.get("litefarm_host"),
    port=os.environ.get("litefarm_port"),
    password=os.environ.get("litefarm_pwd"))

CUR = connection.cursor()


def lst2pgarr(_):
    return '{' + ','.join(_) + '}'

class Location:

    location_categories: dict = {

        # maps figure_type to location_category
        # i.e. barn -> area etc.
        "farm_site_boundary": "area",
        "field": "area",
        "garden": "area",
        "barn": "area",
        "greenhouse": "area",
        "natural_area": "area",
        "surface_water": "area",
        "residence": "area",
        "ceremonial_area": "area",

        # ------------
        "fence": "line",
        "watercourse": "line",
        "buffer_zone": "line",
        # "road"       : "line",
        # "footpath"   : "line",

        # -----
        "water_valve": "point",
        "gate": "point",
    }

    location_id : str
    location_cat: str  # point | area | line
    figure_id   : str
    figure_type : str
    farm_id     : str

    def __init__(self,
                 location_id: str,
                 farm_id: str = '',
                 ) -> None:
        CUR.execute(
            "SELECT figure_id, type FROM \"figure\" where location_id = \'%s\';" % location_id)
        (figure_id, figure_type) = CUR.fetchone()
        self.location_id = location_id
        self.figure_id = figure_id
        self.figure_type = figure_type
        self.farm_id = farm_id

    def get_farm_id(self) -> str:
        if self.farm_id == '':
            CUR.execute(
                "SELECT farm_id FROM \"locations\" where location_id = \'%s\';" % self.location_id)
            self.farm_id = CUR.fetchone()[0]
        return self.farm_id

    def yield_coordinates(self)->dict:
        ...

    def __repr__(self) -> str:

        return """  
        location: \033[95m{}\033[0m

        figure_id  : \033[95m{}\033[0m
        farm_id    : \033[95m{}\033[0m
        figure_type: \033[94m{} ({})\033[0m

        """.format(self.location_id,self.figure_id,self.farm_id,self.figure_type, self.location_categories[self.figure_type])

class Area(Location):

    grid_points: List[dict]
    total_area : int
    perimeter  : int

    def __init__(self, location_id: str, farm_id: str,
                 ) -> None:
        super().__init__(location_id, farm_id)
        # CUR.execute('SELECT * FROM "area" where figure_id = \'%s\';' % 'e0a949f2-3377-11ec-a74c-0242ac130002')
        CUR.execute('SELECT * FROM "area" where figure_id = \'%s\';' %
                    self.figure_id)
        (_, total_area, grid_points, perimeter,
         total_area_unit, perimeter_unit) = CUR.fetchone()

        self.grid_points = grid_points
        self.total_area  = total_area
        self.perimeter   = perimeter

    def yield_coordinates(self):
        return self.grid_points

class Line(Location):

    line_points: List[dict]
    length: int
    width: int

    def __init__(self, location_id: str, farm_id: str) -> None:
        super().__init__(location_id, farm_id)
        CUR.execute('SELECT * FROM "line" where figure_id = \'%s\';' %
                    self.figure_id)
        (_, length, width, line_points, length_unit, width_unit,
         total_area, total_area_unit) = CUR.fetchone()

        self.line_points = line_points
        self.width = width
        self.length = length

    def yield_coordinates(self):
        return self.line_points

class Point(Location):
    point = dict

    def __init__(self, location_id: str, farm_id: str) -> None:
        super().__init__(location_id, farm_id)
        CUR.execute('SELECT * FROM "point" where figure_id = \'%s\';' %
                    self.figure_id)
        (_, point) = CUR.fetchone()
        self.point = point
    def yield_coordinates(self):
        return self.point

class Farm:

    location_categories: dict = {

        # maps figure_type to location_category
        # i.e. barn -> area etc.
        "farm_site_boundary": "area",
        "field": "area",
        "garden": "area",
        "barn": "area",
        "greenhouse": "area",
        "natural_area": "area",
        "surface_water": "area",
        "residence": "area",
        "ceremonial_area": "area",

        # ------------
        "fence": "line",
        "watercourse": "line",
        "buffer_zone": "line",
        # "road"       : "line",
        # "footpath"   : "line",

        # -----
        "water_valve": "point",
        "gate": "point",
    }

    farm_id: str
    locations: List[Location]

    def __init__(self,
                 farm_id: str,
                 ) -> None:

        self.farm_id = farm_id
        self.locations = []

    def get_locations(self) -> List[Location]:
        if self.locations == []:
            CUR.execute("""select type, location.location_id from "location" join "figure" on location.location_id = figure.location_id where farm_id = \'%s\'""" % self.farm_id)
            type_locids = CUR.fetchall()
            print(type_locids)
            def class_from_locid(type:str,loc_id:str):
                if type == "area":
                    return Area(loc_id,self.farm_id)
                if type == "line":
                    return Line(loc_id,self.farm_id)
                if type == "point":
                    return Point(loc_id,self.farm_id)
            locs = [*map(lambda tpl : class_from_locid(self.location_categories[tpl[0]], tpl[1]),type_locids)]
            self.locations = locs
        return self.locations

# farm = Farm('0ad0ce20-3112-11ec-b36e-0242ac130002')

farm = Farm('094a2776-3109-11ec-ad47-0242ac130002')



x = farm.get_locations()
for _ in x:
    pprint(_.yield_coordinates())
# pprint(farm.locations)

# Ex.

# Location 954795b0-31d6-11ec-80b9-0242ac130002
# figure_type: field
# figure_id  : 95490f26-31d6-11ec-80b9-0242ac130002
# farm_id    : 0ad0ce20-3112-11ec-b36e-0242ac130002

# Location e1e8e7b0-3376-11ec-b121-0242ac130002
# figure_type: watercourse
# figure_id  : e1ea0852-3376-11ec-b121-0242ac130002
# farm_id    : 0ad0ce20-3112-11ec-b36e-0242ac130002

# Location b4f75a28-31d4-11ec-8ed0-0242ac130002
# figure_type: gate
# figure_id  : b4f7ba2c-31d4-11ec-8ed0-0242ac130002
# farm_id    : 0ad0ce20-3112-11ec-b36e-0242ac130002

# l = Line('e1e8e7b0-3376-11ec-b121-0242ac130002',
#          '0ad0ce20-3112-11ec-b36e-0242ac130002')
# print(l)

# p = Point('b4f75a28-31d4-11ec-8ed0-0242ac130002',
#           '0ad0ce20-3112-11ec-b36e-0242ac130002')
# print(p)

# for l in farm.locations:
