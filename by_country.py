import sys
from matplotlib.pyplot import figure
import pandas as pd
from farm import *
import geopandas as gpd
from shapely.geometry import Point, Polygon

# br, ca, us,uk, mx
COUNTRY  = sys.argv[1]
country = COUNTRY
query   = """select f.farm_name,
                f.farm_id,
                f.grid_points,
                c.country_name 
                from "farm" f  join "countries" c on f.country_id = c.id where c.country_name ='%s';""" % country

CUR.execute(query)

gridpts              = []
farmnames            = []
farmsizes            = []
farms:List[Farm]     = []

all       = CUR.fetchall()
print("ALL FARMSL:", all)
for (farm_name,farmid, grid_points, country) in all:
    gridpts.append(grid_points) 
    farmnames.append(farm_name)
    farmsizes.append(Farm(farmid).total_area)
    farms.append(Farm(farmid))

world      = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
fig, ax    = plt.subplots()
country    = world[world['name'] == COUNTRY]

lat = list(map(lambda _ : _['lat'],gridpts))
lng = list(map(lambda _ : _['lng'],gridpts))
df  = pd.DataFrame({'names': farmnames,
                    'sizes': farmsizes,
                    'lat'  : lat,
                    'lon'  : lng})

geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
gdf      = gpd.GeoDataFrame(df, geometry=geometry)

gdf.set_crs(epsg=4326, inplace=True)
gdf.to_crs (epsg=3395)

country.plot(ax=ax,
             figsize   = (8,8),
             edgecolor = u'gray',
             cmap      = 'Pastel1',
             alpha     = 0.8)

gdf.plot(ax=ax, 
        markersize = gdf['sizes']/np.array(farmsizes).mean()*6,
        alpha      = 0.3,
        edgecolor  = 'black',
        color      = 'blue'
        )

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

for (lat,lon) in zip(gdf['lat'], gdf['lon']):
    plt.annotate("name", xy=(lat,lon), xytext=(20,20), horizontalalignment='center')

plt.ylabel('Latitude', fontsize=16)
plt.xlabel('Longitude', fontsize=16)

props      = dict(boxstyle='square', facecolor='wheat', alpha=0.2)
total_area = 0
for f in farms:
    total_area += f.total_area
annotation = """Country :    {}
# Farms:     {}
# Total Area:  {} sq. km""".format(COUNTRY, len(farms), np.round( total_area/10**6, 3))

ax.text(0.05, 0.95, annotation, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)

plt.title("Farms in {}".format(COUNTRY), fontsize=16)
# pprint(farms)
plt.show()