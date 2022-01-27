import os
from pprint import pprint
import sys
from attr import field
import geopandas
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, LineString, Point
import json

plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':100})

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

# farmlocs_path = sys.argv[1]
farmlocs_path= "/home/rxz/dev/litefarm/locations/locations_26608372-54ab-11eb-9564-22000ab2b8c4.json"

with open(farmlocs_path) as infile:
    data = json.load(infile)

farm_objects = {
    'barns' : [],
    'fields': [],
    "other" : []
}
areas = []
for datum in data:
    # print(datum['coords'])
    if location_categories[ datum['type'] ] in  [ 'area', 'line' ] :
        try:
            poly = Polygon([*map(lambda i : (i['lng'],i['lat'] ), datum['coords'])])
            areas.append(poly)
            if datum['type'] == "field":
                farm_objects["fields"].append(poly)
            if datum['type'] == "barn":
                farm_objects["barns"].append(poly)
            else:
                farm_objects['other'].append(poly)
        except Exception:
            print("Not enough points to construct a polygon")
            ...

# other  = geopandas.GeoSeries(farm_objects['other'], )
# barns  = geopandas.GeoSeries(farm_objects['barns'])
fields = geopandas.GeoSeries(farm_objects['fields']).set_crs(epsg=4326)
print(fields)
print(fields.crs)

# fields.to_crs("EPSG:3395")

# pprint(fields)
# pprint(fields.crs)
# pprint(fields.area)

# print("area of fields is", np.round(fields.area, 3))

# fig, ax = plt.subplots()
# ax.set_aspect('equal')
# fields.plot(ax=ax,color=None,edgecolor='green',linewidth = 1, facecolor='green', alpha=0.2);
# barns.plot(ax=ax,color=None,edgecolor='orange',linewidth = 1, facecolor='orange',alpha=0.2);
# other.plot(color=None,ax=ax,edgecolor='k',linewidth = 0.5, facecolor='none');

# # plt.show()
# plt.savefig(f'{os.path.basename(farmlocs_path)[0:-5]}.png', bbox_inches='tight')

#  b4c9ceb6-2e6e-11ea-9a69-22000b628b95 |  330
#  0ad0ce20-3112-11ec-b36e-0242ac130002 |  248
#  353f0b9e-5c6a-11ec-8795-0242ac130002 |  203
#  2d930078-31a7-11ec-b8f3-0242ac130002 |  180
#  094a2776-3109-11ec-ad47-0242ac130002 |  159
#  06f0c1c8-329f-11ec-a4ff-0242ac130002 |  136
#  26608372-54ab-11eb-9564-22000ab2b8c4 |  135
#  ca713386-3050-11ec-b23b-0242ac130002 |  120

# print("AREAS:", areas)


# ---------------------------------- AREA CALCULATIONS as per https://gis.stackexchange.com/a/413350/162472

from shapely.geometry.polygon import orient
def gpd_geographic_area(geodf):
    if not geodf.crs and geodf.crs.is_geographic:
        raise TypeError('geodataframe should have geographic coordinate system')
    geod = geodf.crs.get_geod()
    print("GEOD is ", geod)
    def area_calc(geom):
        if geom.geom_type not in ['MultiPolygon','Polygon']:
            return np.nan
        
        # For MultiPolygon do each separately
        if geom.geom_type=='MultiPolygon':
            return np.sum([area_calc(p) for p in geom.geoms])

        # orient to ensure a counter-clockwise traversal. 
        # See https://pyproj4.github.io/pyproj/stable/api/geod.html
        # geometry_area_perimeter returns (area, perimeter)
        return geod.geometry_area_perimeter(orient(geom, 1))[0]

    return geodf.geometry.apply(area_calc)
    

print("gpd geo area", gpd_geographic_area(fields))

from shapely.geometry import Polygon
def line_integral_polygon_area(geom, radius = 6378137):
    """
    Computes area of spherical polygon, assuming spherical Earth. 
    Returns result in ratio of the sphere's area if the radius is specified.
    Otherwise, in the units of provided radius.
    lats and lons are in degrees.
    
    from https://stackoverflow.com/a/61184491/6615512
    """
    if geom.geom_type not in ['MultiPolygon','Polygon']:
        return np.nan

    # For MultiPolygon do each separately
    if geom.geom_type=='MultiPolygon':
        return np.sum([line_integral_polygon_area(p) for p in geom.geoms])

    # parse out interior rings when present. These are "holes" in polygons.
    if len(geom.interiors)>0:
        interior_area = np.sum([line_integral_polygon_area(Polygon(g)) for g in geom.interiors])
        geom = Polygon(geom.exterior)
    else:
        interior_area = 0
        
    # Convert shapely polygon to a 2 column numpy array of lat/lon coordinates.
    geom = np.array(geom.boundary.coords)

    lats = np.deg2rad(geom[:,1])
    lons = np.deg2rad(geom[:,0])

    # Line integral based on Green's Theorem, assumes spherical Earth

    #close polygon
    if lats[0]!=lats[-1]:
        lats = np.append(lats, lats[0])
        lons = np.append(lons, lons[0])

    #colatitudes relative to (0,0)
    a = np.sin(lats/2)**2 + np.cos(lats)* np.sin(lons/2)**2
    colat = 2*np.arctan2( np.sqrt(a), np.sqrt(1-a) )

    #azimuths relative to (0,0)
    az = np.arctan2(np.cos(lats) * np.sin(lons), np.sin(lats)) % (2*np.pi)

    # Calculate diffs
    # daz = np.diff(az) % (2*pi)
    daz = np.diff(az)
    daz = (daz + np.pi) % (2 * np.pi) - np.pi

    deltas=np.diff(colat)/2
    colat=colat[0:-1]+deltas

    # Perform integral
    integrands = (1-np.cos(colat)) * daz

    # Integrate 
    area = abs(sum(integrands))/(4*np.pi)

    area = min(area,1-area)
    if radius is not None: #return in units of radius
        return (area * 4*np.pi*radius**2) - interior_area
    else: #return in ratio of sphere total area 
        return area - interior_area
        


# a wrapper to apply the method to a geo data.frame
def gpd_geographic_area_line_integral(geodf):
    return geodf.geometry.apply(line_integral_polygon_area)

print("gpd area", gpd_geographic_area_line_integral(fields))