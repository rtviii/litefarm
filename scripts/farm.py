import os
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
# for a given farm, have to:
#     - collect all locations
#     - identify the type of location
#     - collect area measurements

dotenv.load_dotenv('/home/rxz/.ssh/secrets.env')
connection =psycopg2.connect(
    dbname   = os.environ.get("litefarm_db"),
    user     = os.environ.get("litefarm_usr"),
    host     = os.environ.get("litefarm_host"),
    port     = os.environ.get("litefarm_port"),
    password = os.environ.get("litefarm_pwd"))
CUR = connection.cursor()

class Location:
    def __init__(self,
                   location_id: str,
                   farm_id    : str,
                 ) -> None: 
        pass


class Area(Location):
    def __init__(self, location_id: str, farm_id: str, name: str,
                   grid_points    : List[dict],
                   total_area     : int,
                   total_area_unit: str,
                   perimiter_unit : str
                 ) -> None: 

        super().__init__(location_id, farm_id)


class Line(Location):
    def __init__(self, location_id: str, farm_id: str, name: str) -> None:
        super().__init__(location_id, farm_id)


class Point(Location):
    def __init__(self, location_id: str, farm_id: str, name: str) -> None:
        super().__init__(location_id, farm_id)


class Farm:
    def __init__(self,
                   farm_id    : str,
                 ) -> None    : 
                 self.farm_id = farm_id

    def get_locations(self)->List[Location]:
        CUR.execute("""
        select array_agg( location_id ) from "location" where farm_id = \'%s\'
        """ % self.farm_id)
        x:str = len(CUR.fetchall()[0][0][1:-1].split(','))
        # x:str = len(CUR.fetchall()[0][0][1:-1].split(','))
        print(x)
        

farm = Farm('0ad0ce20-3112-11ec-b36e-0242ac130002')

farm.get_locations()