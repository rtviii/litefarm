from farm import *
import scripts.farm_plot_locs as farmlocs



# -------------- A row is something like this:
#
#
# Farm ID
# Country
# Coordinates
# FarmArea
# Natural Area
# Industrial Area
# Field Area
# Resource Spatial Boundaries
# spatial boundaries for fields
# number of unique subgroups
# number of unique varieties
# crop list
# variety list (we can discuss the terminology and the format for these)

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
pprint(allfarms)
