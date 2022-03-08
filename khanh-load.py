from farm import *
import scripts.farm_plot_locs as farmlocs
import countries_cleanup as countries
from shapely import geometry





# -------------- A row is something like this:
#
#
# Farm ID                        - sql
# Country                        - sql 
# Coordinates                    - sql
# FarmArea                       - script
# Natural Area                   - script
# Industrial Area                - script
# Field Area                     - script
# Resource Spatial Boundaries    - sql
# spatial boundaries for fields  - script
# number of unique subgroups     - script
# number of unique varieties     - script
# crop list                      - sql
# variety list                   - sql

CUR.execute("""
select 
    f.farm_id,
    (select c.country_name from "countries" c where c.id = f.country_id),
    f.grid_points,
    array_agg(cv.crop_variety_name) as variety,
    array_agg(c.crop_subgroup) as subgroup
from "farm" f 
left join "crop_variety" cv  on cv.farm_id = f.farm_id
left join "crop" c on c.crop_id = cv.crop_id
GROUP BY f.farm_id""")

allfarms = CUR.fetchall()
headers = [                       'farm_id'              ,
                                  'country'              ,
                                  'global_coordinates'   ,
                                  'total_area'           ,
                                  'natural_area'         ,
                                  'industrial_area'      ,
                                  'field_only_area'      ,

                                  "farm_site_boundary_S",
                                  "field_S"              ,
                                  "garden_S"             ,
                                  "barn_S"               ,
                                  "greenhouse_S"         ,
                                  "natural_area_S"       ,
                                  "surface_water_S"      ,
                                  "residence_S"          ,
                                  "ceremonial_area_S"    ,
                                  "fence_S"              ,
                                  "watercourse_S"        ,
                                  "buffer_zone_S"        ,
                                  "water_valve_S"        ,
                                  "gate_S"               ,

                                  'crop_varieties'      ,
                                  'crop_subgroups'
                      ]
rows = []

        
def get_natural_industrial_areas(f:Farm):    
    locs = {
        "production": [
            "field",
            "garden",
            "barn",
            "greenhouse",
            "residence",
        ],
        "natural": [
            "farm_site_boundary",
            "natural_area",
            "surface_water",
        ]
    }

    if f.total_area < 0.01:

        return [ 
            0.0,f.total_area
         ]

    else:
        nat  = []
        prod = []
        for loc in f.locations:
            if loc in  locs['natural']:
                nat.extend(f.locations[loc])

            if loc in  locs['production']:
                prod.extend(f.locations[loc])
        return [ 
             unary_union(nat).area,
             unary_union(prod).area
         ]
import pandas as pd
def listofpoly_to_listofpts(l:List)->List:
    poly_to_pts = lambda poly: list(poly.exterior.coords)
    return list(map(poly_to_pts, l))

spgdf  = pd.read_excel('./spg-filled1.xlsx')
spgids = spgdf['Farm ID'].to_list()
spgids = list(filter(lambda _ : str(_) != str('nan'), spgids))


for ( i,f ) in enumerate( allfarms ):

    (farmid, country, coordinates,varieties_arr, subgroups_arr) = f
    if farmid not in spgids:
        continue

    try:
        _farm = Farm(farmid)
    except:
        print("could not find farmid ", farmid)
        continue

    
    farm_id            =  _farm.farm_id
    country            =  country
    global_coordinates =  coordinates
    total_area         = _farm.total_area
    natural_area, industrial_area =  get_natural_industrial_areas(_farm)
    if 'field' in _farm.locations:
        field_only_area      =  unary_union(_farm.locations['field']).area
    else:
        field_only_area = 0.0

    farm_site_boundary_S = [] if 'farm_site_boundary' not in _farm.locations else listofpoly_to_listofpts( _farm.locations['farm_site_boundary'] )
    field_S              = [] if 'field'              not in _farm.locations else listofpoly_to_listofpts( _farm.locations['field'             ] )
    garden_S             = [] if 'garden'             not in _farm.locations else listofpoly_to_listofpts( _farm.locations['garden'            ] )
    barn_S               = [] if 'barn'               not in _farm.locations else listofpoly_to_listofpts( _farm.locations['barn'              ] )
    greenhouse_S         = [] if 'greenhouse'         not in _farm.locations else listofpoly_to_listofpts( _farm.locations['greenhouse'        ] )
    natural_area_S       = [] if 'natural_area'       not in _farm.locations else listofpoly_to_listofpts( _farm.locations['natural_area'      ] )
    surface_water_S      = [] if 'surface_water'      not in _farm.locations else listofpoly_to_listofpts( _farm.locations['surface_water'     ] )
    residence_S          = [] if 'residence'          not in _farm.locations else listofpoly_to_listofpts( _farm.locations['residence'         ] )
    ceremonial_area_S    = [] if 'ceremonial_area'    not in _farm.locations else listofpoly_to_listofpts( _farm.locations['ceremonial_area'   ] )
    fence_S              = [] if 'fence'              not in _farm.locations else listofpoly_to_listofpts( _farm.locations['fence'             ] )
    watercourse_S        = [] if 'watercourse'        not in _farm.locations else listofpoly_to_listofpts( _farm.locations['watercourse'       ] )
    buffer_zone_S        = [] if 'buffer_zone'        not in _farm.locations else listofpoly_to_listofpts( _farm.locations['buffer_zone'       ] )
    water_valve_S        = [] if 'water_valve'        not in _farm.locations else listofpoly_to_listofpts( _farm.locations['water_valve'       ] )
    gate_S               = [] if 'gate'               not in _farm.locations else listofpoly_to_listofpts( _farm.locations['gate'              ] )

    CUR.execute("""
                select array_agg(cv.crop_variety_name) as variety,
                    array_agg(c.crop_subgroup) as subgroup,
                    count(c.crop_subgroup) as subgroup_count,
                    cv.farm_id
                from 
                "crop_variety" cv  
                join "crop" c on c.crop_id          = cv.crop_id
                left join "farm" f on c.farm_id     = f.farm_id
                where cv.farm_id = '%s'
                GROUP BY cv.farm_id, f.country_id, f.grid_points"""%farmid)



    resp = CUR.fetchall()
    ( crop_varieties, crop_subgroups, _1 , _2 ) = resp[0] if len(resp) >0  else [[] ,[]  ,0 ,farmid]


    row = [
           farm_id,
           country,
           global_coordinates,
           total_area,
           natural_area,
           industrial_area,
           field_only_area, 

            farm_site_boundary_S ,
            field_S              ,
            garden_S             ,
            barn_S,
            greenhouse_S         ,
            natural_area_S       ,
            surface_water_S      ,
            residence_S          ,
            ceremonial_area_S    ,
            fence_S              ,
            watercourse_S        ,
            buffer_zone_S        ,
            water_valve_S,
            gate_S      ,
            crop_varieties,
            crop_subgroups         
            
            ]

    rows.append(row)
            

df =pd.DataFrame(rows, columns=headers)
df.to_csv('farms_SPG_data.csv')
print(df)










