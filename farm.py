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
import reverse_geocoder as rg
import pycountry
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
import matplotlib.pyplot as plt

dotenv.load_dotenv('/home/rxz/.ssh/secrets.env')
connection = psycopg2.connect(
    dbname   = os.environ.get("litefarm_prod_db"),
    user     = os.environ.get("litefarm_prod_usr"),
    host     = os.environ.get("litefarm_prod_host"),
    port     = os.environ.get("litefarm_prod_port"),
    password = os.environ.get("litefarm_prod_pwd"))
CUR     = connection.cursor()
pklpath = lambda farm_id: '/home/rxz/dev/litefarm/farms_prod/{}.pickle'.format(farm_id)
pklopen = lambda _id:  pickle.load(open(pklpath(_id),'rb'))

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
    country_code_2letter: str
    grid_pts: dict

    users     : List[dict]

    def __init__(self, farm_id:str, pkl=True) -> None:
        if pkl:
            try:
                D = pklopen(farm_id)
            except FileNotFoundError:
                D = {
                    'total_area': 0,
                    'locations' : [],
                    'farm_id'   : farm_id
                }
        else:
            D = pkl

        self.total_area = D['total_area']
        self.locations  = dict(D['locations'])
        self.farm_id    = D['farm_id']

    def farm_get_geocords(self)->dict:
        CUR.execute("""select f.farm_id, f.grid_points, c.country_name from "farm" f  join "countries" c on f.country_id = c.id where f.farm_id ='%s';""" % self.farm_id)
        [ fid, grid_pts, country ] = CUR.fetchall()[0]
        lat = grid_pts['lat']
        lng = grid_pts['lng']

        return {
            "lat"    : lat,
            "lng"    : lng,
            "country": country
        }

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

    def farm_get_crops(self):
        CUR.execute("""
        select * from (select array_agg(cv.crop_variety_name) as variety,
        array_agg(c.crop_subgroup) as subgroup,
        array_agg(c.crop_group) as group,
        cv.farm_id 
        from "crop_variety" cv  join "crop" c on c.crop_id = cv.crop_id 
        GROUP BY cv.farm_id ) subq where subq.farm_id ='%s'""" % self.farm_id)

        [varieties,subgroups,groups, farmid ] = CUR.fetchall()[0]
        print(varieties)
        print(subgroups)
        print(groups)

    def plot_farm(
        self,
        **kwargs):
        """
        @merged=True to display unary_union
        """

        print("got kwargs")
        pprint(kwargs)
        # plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':100})
        plt.rcParams["figure.figsize"] = (20,3)
        highlight = kwargs.pop('highlight', 'NONE')
        fig, ax = plt.subplots(figsize = (4,4))
        ax.set_aspect('equal')
        legendPatches = [ ]
                    # color     = None,
                    # ax        = ax,
                    # edgecolor = LOCTYPES[loctype]['color'],
                    # linewidth = 0.7,
                    # facecolor = LOCTYPES[loctype]['color'],
                    # alpha     = 0.5,

        for kvp in self.locations.items():
            loctype   = kvp[0]
            polygons  = kvp[1]
            print("HIGHLIGHT IS ", highlight)
            print("Loctype: ", loctype)
            legendPatches.append(Patch(facecolor=LOCTYPES[loctype]['color'], label= loctype,))

            gpd.GeoSeries(unary_union(polygons)).plot( 
                color     = None,
                ax        = ax,
                edgecolor = LOCTYPES[loctype]['color'],
                linewidth = 1,
                alpha     = 1 if highlight != loctype else 0.5,
                facecolor = LOCTYPES[loctype]['color'] if highlight == loctype else 'none',
                )

        legendPatches.append(Patch(facecolor=None, label= "Total Area: {} km^2".format(round(self.total_area/10**6, 3))))
        legendPatches.append(Patch(facecolor=None, label= "Number of Locations: {}".format(self.nloc())))
        handles, _ = ax.get_legend_handles_labels()

        U = self.get_users()
        ownern = 1
        for u in U:
            print(u)
            legendPatches.append(Patch(facecolor=None, fill=None, label= "Owner {}: {}(owns {} other farms)".format(ownern,u['first_name'] + " " + u['last_name'], int( u['nfarms'] )-1)))
            ownern+=1
            

        ax.legend(handles=[*handles,*legendPatches], loc='best')
        ax.set_title("")

        if 'save' in kwargs:
            figure = plt.gcf() # get current figure
            figure.set_size_inches(16, 8)
            plt.savefig("/home/rxz/dev/litefarm/prod_plots/{}.png".format(self.farm_id),  dpi = 300)
            return
        plt.show()

def load_all_farms(hasarea=False) ->List[ Farm ]:
    agg        = []
    missingids = []

    for id in farm_ids_prod():
        try:
            agg.append(Farm(id, pkl=pklopen(id)))
        except FileNotFoundError:
            print("Missing: ", id)
            missingids.append(id)
    agg.sort(key=lambda f: f.nloc())

    if hasarea:
        agg =list(filter(lambda f: f.total_area > 5, agg))
    return agg

def farm_ids_prod()->List[str]:
    with open("/home/rxz/dev/litefarm/resources/farmids_prod.txt",'r', encoding='utf-8') as infile:
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
    nlocs  = locations_by_number()
    y      = np.array([ *nlocs.values() ])
    labels = []
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

def user_by_farm():
    CUR.execute("""
    select uf.user_id, u.first_name, u.last_name,
    array_agg(uf.farm_id) as farmids,
    count(distinct( uf.farm_id )) as nfarms
    from "userFarm" uf 
    join "users" u on uf.user_id = u.user_id
    GROUP BY uf.user_id, u.first_name, u.last_name
    ORDER BY nfarms DESC""")
    rows = CUR.fetchall()
    print(rows)
    agg  = []
    for row in rows:
        (userid, fname, lname,farms,nfarms) = row
        farms                               = farms[1:-1].split(',')
        w_agg                               = 0
        for farm in farms:
            w_agg += Farm(farm).total_area
        agg.append({
            "userid"    : userid,
            "last_name" : lname,
            "first_name": fname,
            "aum_km2"   : w_agg/10**6,
            "aum"       : w_agg,
            "fum"       : nfarms
        })
    return agg

def main():

    parser = argparse.ArgumentParser(description='Hola')

    parser.add_argument("-i"       ,        "--farm_id"   , type=str, help="Farm id. i.e. 094a2776-3109-11ec-ad47-0242ac130002")
    parser.add_argument("-fu"      ,        "--farm_users", type=str                                                           )
    parser.add_argument("--all"    , action='store_true'                                                                       )
    parser.add_argument("--allhist", action='store_true'                                                                       )
    parser.add_argument("--pie"    , action='store_true'                                                                       )
    parser.add_argument("--prod"   , action='store_true'                                                                       )
    parser.add_argument("--test"   , action='store_true'                                                                       )
    parser.add_argument("--save_farm_profile", type=str, help="generate a polygon-profile of a farm and save it as a pkl")

    parser.add_argument("--by_country", type=str)
    # ------ Single farm flags
    parser.add_argument("--plot", action='store_true')
    parser.add_argument("--plotsave", action='store_true')

    parser.add_argument("--hl_loctype", type=str)  # highlihgt loctype

    # Throwaway
    parser.add_argument("--merged", action='store_true')
    parser.add_argument("--hasarea", action='store_true')

    args    = parser.parse_args()

    if args.save_farm_profile:
        farmid=args.save_farm_profile
        profile = farm_profile(farmid)
        with open(pklpath(farmid), 'wb') as outfile:
            pickle.dump(profile, outfile)
        print(pklpath(farmid))
        exit(0)

    if args.farm_id:
        if args.merged:
            Farm(args.farm_id).plot_farm(merged=True)                        
            return
        if args.plotsave:
            Farm(args.farm_id).plot_farm(save=True)                        
            return
        if args.plot:
            Farm(args.farm_id).plot_farm(**{
                'highlight':args.hl_loctype
                                            })
            return
        # return

    if args.farm_users:
        for user in Farm(args.farm_users).get_users():
            pprint(user)
            return

    if args.all:
        print("{} \t{} \t{}".format("Total Area", "# Locations", "Farm Id"))
        all = load_all_farms(hasarea=args.hasarea)
        for f in all:
            print("{} \t{} \t{}".format(f.total_area, f.nloc(), f.farm_id))

    if args.pie:
        plot_locations_n_pie()

    if args.test:
        print(Farm(args.farm_id).farm_get_geocords())

    if args.by_country:
        print(args.by_country)
        
if __name__ == "__main__":
    main()
 

#  barplots 
#  crop varieties for a given farm
#  more differentiated plotting of fields etc.
#  shape annotations