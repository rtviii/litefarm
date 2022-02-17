from re import sub
from tkinter import Variable
from xml.dom.expatbuilder import FragmentBuilder
import sys
from matplotlib.lines import Line2D
from matplotlib.pyplot import figure
import pandas as pd
from farm import *
import geopandas as gpd
from shapely.geometry import Point, Polygon
from matplotlib.patches import Patch, Polygon
import matplotlib.pyplot as plt

props = {
        "None"                                   : {"num":197 ,"color":"dimgray"     , "marker":'.' },
        'Mushrooms and truffles'                 : {"num":1   ,"color":"bisque"      , "marker":"," },
        'Rubber'                                 : {"num":1   ,"color":"forestgreen" , "marker":"o" },
        'Lentils'                                : {"num":2   ,"color":"goldenrod"   , "marker":"v" },
        'Melons'                                 : {"num":2   ,"color":"lightsalmon" , "marker":"^" },
        'Other roots and tubers'                 : {"num":4   ,"color":"orangered"   , "marker":"<" },
        'Oilseed crops and oleaginous fruits'    : {"num":12  ,"color":"violet"      , "marker":">" },
        'Flower crops'                           : {"num":15  ,"color":"b"           , "marker":"1" },
        'Fibre crops'                            : {"num":25  ,"color":"g"           , "marker":"2" },
        'Berries'                                : {"num":89  ,"color":"c"           , "marker":"3" },
        'Cereals'                                : {"num":173 ,"color":"m"           , "marker":"+" },
        'Citrus fruits'                          : {"num":121 ,"color":"y"           , "marker":"8" },
        'Fruit-bearing vegetables'               : {"num":399 ,"color":"wheat"       , "marker":"s" },
        'Grapes'                                 : {"num":25  ,"color":"beige"       , "marker":"p" },
        'Grasses and other fodder crops'         : {"num":76  ,"color":"lightskyblue", "marker":"P" },
        'High starch root/tuber crops'           : {"num":114 ,"color":"teal"        , "marker":"*" },
        'Leafy or stem vegetables'               : {"num":483 ,"color":"coral"       , "marker":"*" },
        'Leguminous crops'                       : {"num":155 ,"color":"gold"        , "marker":"H" },
        'Medicinal, pesticidal or similar crops' : {"num":69  ,"color":"brown"       , "marker":'+' },
        'Nuts'                                   : {"num":50  ,"color":"tomato"      , "marker":"x" },
        'Other crops'                            : {"num":212 ,"color":"slateblue"   , "marker":"+" },
        'Other fruits'                           : {"num":18  ,"color":"springgreen" , "marker":"D" },
        'Other temporary oilseed crops'          : {"num":32  ,"color":"navy"        , "marker":"d" },
        'Permanent oilseed crops'                : {"num":16  ,"color":"hotpink"     , "marker":"|" },
        'Pome fruits and stone fruits'           : {"num":114 ,"color":"chocolate"   , "marker":"_" },
        'Root, bulb or tuberous vegetables'      : {"num":296 ,"color":"chartreuse"  , "marker":"+" },
        'Spice and aromatic crops'               : {"num":87  ,"color":"firebrick"   , "marker":"5" },
        'Stimulant crops'                        : {"num":54  ,"color":"lime"        , "marker":"6" },
        'Sugar crops'                            : {"num":24  ,"color":"olivedrab"   , "marker":"7" },
        'Tropical and subtropical fruits'        : {"num":321 ,"color":"tan"         , "marker":"+" }
        }


CUR.execute("""
select array_agg(cv.crop_variety_name) as variety,
    array_agg(c.crop_subgroup) as subgroup,
    array_agg(c.crop_group) as group,
    cv.farm_id,
    f.grid_points
from 
"crop_variety" cv  
join "crop" c on c.crop_id                = cv.crop_id
left OUTER join "farm" f on c.farm_id     = f.farm_id
left OUTER join "countries" ctr on ctr.id = f.country_id
GROUP BY cv.farm_id , f.country_id, f.grid_points""")

_                               = CUR.fetchall()

farms                           = []
subgroups                       = []
farm_v_subgroups                = []
zero_area                       = []
viable                          = []
none_varieties                  = []
datapoints = []

for (varieties, subgroups, groups, farmid, grid_points) in _:
    f = Farm( farmid )

    if f.total_area < 1:
        ...
    elif len(set(subgroups)) and list(set(subgroups))[0] == None:
        ...
    else:

        for s in subgroups:
            datapoints.append({
            "marker": props[str(s)]['marker'],
            "label" : str(s),
            "color" : props[str(s)]['color'],
            "x"     : f.total_area,
            'y'     : f.total_area/( len(subgroups) *  props[str(s)]['num'])
            })

        viable.append({
            "total_area": f.total_area,
            "subgroups" : subgroups,
            "farmid"    : farmid
        })

# CROPTYPE= 'Leafy or stem vegetables'
CROPTYPE= 'Tropical and subtropical fruits'
fig,ax = plt.subplots()
datapoints.sort(key=lambda x: x['x'])
datapoints = datapoints[:-50] 
datapoints = list(filter(lambda x: x['label'] == CROPTYPE,datapoints))

pprint(datapoints)
# # ----------------------------------------------------------------------------- Single group-----------------------------------------

# pprint(datapoints)
# df = pd. DataFrame({
#     'x'    : list(map(lambda _: _['x'], datapoints)),
#     'y'    : list(map(lambda _: _['y'], datapoints)),
#     'm'    : list(map(lambda _: _['marker'], datapoints)),
#     'color': list(map(lambda _: _['color' ], datapoints)),
#     'label': list(map(lambda _: _['label' ], datapoints)),
# })

# sns.scatterplot(data=df, x='x', y='y', style='m', hue='color', legend=False)
# plt.xlabel("Total area, sq. km"    , fontsize=16)

# plt.ylabel("Crop frequency v area", fontsize=16)

# legendPatches=[]
# legendPatches.append(Line2D([0], [0], marker=props[CROPTYPE]['marker'], color='blue', label='{}: {}'.format(CROPTYPE, props[CROPTYPE]['num'])))

# handles, _          = ax.get_legend_handles_labels()
# plt.legend(handles  = [*handles,*legendPatches], loc='best')
# plt.show()


# # -----------------------------------------------------------------------------------------------------------------------------------
# --------------- by croptype | subgroup_v_area_over_popularity
# pprint(subgroup_v_area_over_popularity)
# df = pd. DataFrame({
#     'x'     : list(map(lambda _: _['x'     ], subgroup_v_area_over_popularity)),
#     'y'     : list(map(lambda _: _['y'     ], subgroup_v_area_over_popularity)),
#     'm'     : list(map(lambda _: _['marker'], subgroup_v_area_over_popularity)),
#     'color' : list(map(lambda _: _['color' ], subgroup_v_area_over_popularity)),
#     'label' : list(map(lambda _: _['label' ], subgroup_v_area_over_popularity)),
# })

# sns.scatterplot(data=df, x='x', y='y', style='m', hue='color', legend=False)
# plt.xlabel("Total area, sq. km"    , fontsize=16)

# plt.ylabel("Crop frequency v area", fontsize=16)

# legendPatches=[]
# for kvp in props.items():
#     try:
#         legendPatches.append(
#             Line2D([0], [0], marker=kvp[1]['marker'], color=kvp[1]['color'], label='{}: {}'.format(kvp[0], props[kvp[0]]['num'])),
#             )
#     except:
#         ...

# handles, _          = ax.get_legend_handles_labels()
# plt.legend(handles  = [*handles,*legendPatches], loc='best')
# plt.show()

# ---------------simple scatter

datapoints.sort(key=lambda x: x['x'])
datapoints = datapoints[:-50] 
ax.scatter(
    list(map(lambda x: x['total_area'], viable)),
    list(map(lambda x: len(x['subgroups']), viable)),
    s     = 7,
    alpha = 0.5,
    color = 'blue',
    )

plt.xlabel("Total area, sq. m", fontsize=16)
plt.ylabel("Number of crops grown", fontsize=16)
plt.show()
# ----------------

# {'.': 'point',
#  ',': 'pixel',
#  'o': 'circle',
#  'v': 'triangle_down',
#  '^': 'triangle_up',
#  '<': 'triangle_left',
#  '>': 'triangle_right',
#  '1': 'tri_down',
#  '2': 'tri_up',
#  '3': 'tri_left',
#  '4': 'tri_right',
#  '8': 'octagon',
#  's': 'square',
#  'p': 'pentagon',
#  '*': 'star',
#  'h': 'hexagon1',
#  'H': 'hexagon2',
#  '+': 'plus',
#  'x': 'x',
#  'D': 'diamond',
#  'd': 'thin_diamond',
#  '|': 'vline',
#  '_': 'hline',
#  'P': 'plus_filled', 
#  'X': 'x_filled'}
