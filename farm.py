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
import numpy as np
from shapely.ops import unary_union
import os
from pprint import pprint
from matplotlib.patches import Patch, Polygon
import matplotlib.pyplot as plt
import psycopg2
import dotenv
from typing import List, Mapping
from scripts.farm_plot_locs import farm_get_area, locations_to_polygons, LOCTYPES
import seaborn as sns
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
    users : List[dict]
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

    def get_users(self):
        CUR.execute("""
                select  json_build_object(
            'id'         , u       .user_id    ,
            'first_name' , u       .first_name ,
            'last_name'  , u       .last_name  ,
            'email'      , u       .email      ,
            'bday'       , u       .birth_year ,
            'logincount', count(ul.user_log_id),
            'nfarms', userfarms.nfarms,
            'farmids', userfarms.farmids
        )
        from "userFarm" uf
        join "users"    u  on uf.user_id = u.user_id
        join "userLog"  ul on  u.user_id = ul.user_id
        join (
            select uf.user_id,
            array_agg(uf.farm_id) as farmids,
            count(distinct( uf.farm_id )) as nfarms
            from "userFarm" uf 
            GROUP BY uf.user_id ) userfarms
        on uf.user_id = userfarms.user_id
        where uf.farm_id = '%s'
        GROUP BY u.user_id,u.first_name,u.last_name, u.email,u.birth_year, 
        userfarms.nfarms, userfarms.farmids
        """%self.farm_id)
        _ = CUR.fetchall()
        self.users = []
        for o in _:
            self.users.append(o[0])
        return self.users

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

def load_all_farms(hasarea=False) ->List[ Farm ]:
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
    agg.sort(key=lambda f: f.nloc())
    if hasarea:
        agg =list(filter(lambda f: f.total_area > 5, agg))
    return agg

def farm_ids()->List[str]:
    with open("/home/rxz/dev/litefarm/resources/farm_ids.txt",'r', encoding='utf-8') as infile:
        lines = list(map(str.strip,infile.readlines()))
        return lines

def locations_by_number()->dict:
    d ={}
    for i in load_all_farms():
        for item in i.locations.items():
            if item[0] not in d:
                d[item[0]] =0
            d[item[0]] +=len( item[1] )
    return d

def plot_locations_n_pie():
    sns.set_theme()
    nlocs= locations_by_number()
    y         = np.array([ *nlocs.values() ])
    labels =[]
    for key in nlocs.keys():
        labels.append( "{}: {}".format   ( str( key[0] ).upper() + key[1:],nlocs[key]) )   
    plt.pie(y, 
    labels = labels, 
    # explode = myexplode,
    textprops={'fontsize':14},
    # labeldistance=0.8,
    shadow = True)
    plt.legend(title = "")
    plt.show() 

def main():
    parser = argparse.ArgumentParser(description='Hola')
    parser.add_argument("-f", "--farm", type=str, help="Farm id. i.e. 094a2776-3109-11ec-ad47-0242ac130002")
    parser.add_argument("-fu", "--farm_users", type=str, help="Farm id. i.e. 094a2776-3109-11ec-ad47-0242ac130002")
    parser.add_argument("--all", action='store_true')
    parser.add_argument("--pie", action='store_true')
    parser.add_argument("--test", action='store_true')
    args    = parser.parse_args()
    if args.farm:
        Farm(args.farm).plot_farm()                        

    if args.farm_users:
        for user in Farm(args.farm_users).get_users():
            pprint(user)

    if args.all:
        print("{} \t{} \t{}".format("Total Area", "# Locations", "Farm Id"))
        for f in load_all_farms():
            print("{} \t{} \t{}".format(f.total_area, f.nloc(), f.farm_id))

    if args.pie:
        plot_locations_n_pie()

    if args.test:
        pprint(list(set(farm_ids())))

main()


sns.set_theme()
all = load_all_farms()
print(len(all))
total_areas = []
for i in all:
    total_areas.append(i.total_area)