import functools
import os
import reverse_geocoder as rg
import pycountry
import psycopg2

#-⋯⋯⋅⋱⋰⋆⋅⋅⋄⋅⋅∶⋅⋅⋄▫▪▭┈┅✕⋅⋅⋄⋅[environment]⋯⋯⋯⋯⋅⋱⋰⋆⋅⋅⋄⋅⋅∶⋅⋅⋄▫▪▭┈
connection = psycopg2.connect(
    dbname   = os.environ.get("litefarm_prod_db"),
    user     = os.environ.get("litefarm_prod_usr"),
    host     = os.environ.get("litefarm_prod_host"),
    port     = os.environ.get("litefarm_prod_port"),
    password = os.environ.get("litefarm_prod_pwd"))
CUR     = connection.cursor()
#-⋯⋯⋅⋱⋰⋆⋅⋅⋄⋅⋅∶⋅⋅⋄▫▪▭┈┅✕⋅⋅⋄⋅⋅✕∶⋅⋅⋄⋱⋰⋯⋯⋯⋯⋅⋱⋰⋆⋅⋅⋄⋅⋅∶⋅⋅⋄▫▪▭┈





# Grab country names and ids,their standard codes into dict
CUR.execute("""select array_agg(json_build_object(country_name,id)) from countries;"""); 
ISO3166_1 = {};
for i in CUR.fetchone()[0]:
    try:
        litefarm_name, litefarm_cc = list(i.items())[0]
        C_obj = pycountry.countries.search_fuzzy(litefarm_name)[0]
        ISO3166_1.update({
        C_obj.alpha_2: {
            "name": litefarm_name,
            "cc"  : litefarm_cc
        }
        })
    except:
        print("Could not locate 2-letter code for ", i)
        ...


# country id fix
def fix_c_id_huh(farm_id:str, grid_pts:dict, country_id)->None:
    if grid_pts == None :
        return

    if country_id == None:
        lat = grid_pts['lat']
        lng = grid_pts['lng']
        matches   = rg.search((lat,lng))
        alpha2ccs = [match['cc'] for match in matches]
        alpha2ccs
        if len(alpha2ccs) > 0:
            sought_cc = ISO3166_1[alpha2ccs[0]]['cc']
            print("Update {}'s country_id to {} ".format(farm_id,sought_cc))
            # CUR.execute("UPDATE farm SET country_id=%s  WHERE farm_id=%s;"%(sought_cc, farm_id))
    return

# Grab farms. for those that do not have country_id but do have grid points, issue update
CUR.execute("""select farm_id, grid_points,country_id from "farm";""")
farms = CUR.fetchall()
[fix_c_id_huh(fid,grid_pts,cid) for (fid, grid_pts, cid) in farms]



