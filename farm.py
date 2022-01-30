#!/usr/bin/python3

def dir_path(string):
    if string == "0":
        return None
    if os.path.isdir(string):
        return string
    else:
        try:
            if not os.path.exists(string):
                os.makedirs(string, exist_ok=True)
                return string
        except:
            raise PermissionError(string)
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
from scripts.farm_plot_locs import farm_get_area, locations_to_polygons, LOCTYPES
import argparse


dotenv.load_dotenv('/home/rxz/.ssh/secrets.env')
connection = psycopg2.connect(
    dbname=os.environ.get("litefarm_db"),
    user=os.environ.get("litefarm_usr"),
    host=os.environ.get("litefarm_host"),
    port=os.environ.get("litefarm_port"),
    password=os.environ.get("litefarm_pwd"))
CUR    = connection.cursor()

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

class Farm:
    locations : dict
    total_area: float
    farm_id   : str
    def __init__(self, farm_id:str, pkl:dict={}) -> None:
        if pkl =={}:
            D = farm_profile(farm_id)
        else:
            D = pkl

        self.total_area = D['total_area']
        self.locations  = D['locations']
        self.farm_id    = D['farm_id']

    def all_poly(self)->List[Polygon]:
        o = []
        for _ in self.locations.values():
            o.extend(list(_)) 
        return o

    def get_owner(self):
        CUR.execute("""
        """)

    def nloc(self)->int:
        return len(self.all_poly())

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


        # if kwargs.pop('savepath', False):
        #     plt.savefig(kwargs['savepath'], bbox_inches='tight')

        if 'merged' in kwargs:
            
            gpd.GeoSeries(unary_union(self.all_poly())).plot( 
                color     = None,
                ax        = ax,
                edgecolor = "royalblue",
                linewidth = 0.4,
                facecolor = 'blue',
                alpha     = 0.3
                )
        else: 

            for kvp in self.locations.items():
                loctype  = kvp[0]
                polygons = kvp[1]

                if kwargs.pop('merged', False):
                    print("GOT MERGED TRUE")
                    polygons = unary_union(polygons)

                gpd.GeoSeries(polygons).plot( 
                    color     = None,
                    ax        = ax,
                    edgecolor = LOCTYPES[loctype]['color'],
                    linewidth = 0.5,
                    facecolor = 'none',
                    )

                legendPatches.append(Patch(facecolor=LOCTYPES[loctype]['color'], label= loctype,))
        legendPatches.append(Patch(facecolor=None, label= "Total Area: {} km^2".format(round(self.total_area/10**6, 3))))
        legendPatches.append(Patch(facecolor=None, label= "Number of Locations: {}".format(self.nloc())))
        handles, _ = ax.get_legend_handles_labels()
        ax.legend(handles=[*handles,*legendPatches], loc='best')
        plt.show()

def main():


    parser = argparse.ArgumentParser(description='Hola')
    parser.add_argument("-f", "--farm", type=str, help="Farm id. i.e. 094a2776-3109-11ec-ad47-0242ac130002")
    parser.add_argument("--all", action='store_true')
    args    = parser.parse_args()
    if args.farm:
        Farm(args.farm).plot_farm()                        
    if args.all:
        f:Farm
        print(load_all_farms().sort(key=lambda f: f.nloc()))

main()

def load_all_farms() ->List[ Farm ]:
    pklpath = lambda farm_id: '/home/rxz/dev/litefarm/farms/{}.pickle'.format(farm_id)
    pklopen = lambda path:  pickle.load(open(pklpath(path),'rb'));
    from farm import Farm, farm_profile
    agg        = []
    missingids = []

    for id in farm_ids():
        try:
            agg.append(Farm(id, pkl=pklopen(id)))
        except FileNotFoundError:
            print("Missing: ", id)
            missingids.append(id)
    print("Len aggregate : ",len(agg))
    return agg

def farm_ids()->List[str]:
    with open("/home/rxz/dev/litefarm/resources/farm_ids.txt",'r', encoding='utf-8') as infile:
        lines = list(map(str.strip,infile.readlines()))
        return lines