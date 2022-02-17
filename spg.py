from concurrent.futures import thread
import sys
import pandas as pd
from farm import *

    # rows to fill:
    # - farmid
    # - usr id
    # - email <<<<<<<<<<<<<<<<<<
    # - role	

    # - user_ids_for_farm
    # - farm_site_boundary_exists
    # - bound_area_ha
    # - has_3_locations
    # - n_locations
    # - n_crop_plans
    # - n_unique_crop_subgroups
    # - n_unique_crop_varieties


def get_users_for_farm(farmid:str):
    CUR.execute("""
    select array_agg(json_build_object(
    'user_id',u.user_id,
    'last_name',u.last_name,
    'first_name',u.first_name)) as all_users_on_this_farm
    from "users" u
    join "userFarm" uf  on uf.user_id = u.user_id
    WHERE uf.farm_id='%s'"""%farmid)
    return CUR.fetchall()[0]


def rectify_via_email(email:str, original_farm=False, original_userid=False):
    """given a user email, fetch the rest"""
    CUR.execute("""select 
        array_agg(uf.farm_id) as farmids,
        uf.user_id, 
        u.email,
        rl.role
        from "userFarm" uf 
        join "users" u on uf.user_id = u.user_id 
        join "role" rl on rl.role_id = uf.role_id 
        where u.email ='%s'
        GROUP BY uf.user_id, u.first_name, u.last_name,u.email, rl.role"""%email)
    
    resp = CUR.fetchall()
    if len( resp ) > 1: print("Multiple users with email {}. Exiting ".format(email)); exit(1)
    [theirfams, userid, email, role] = resp[0]
    reference_farm                   = original_farm if original_farm else theirfams[0]
    user_ids_for_farm                = get_users_for_farm(reference_farm)
    []                = farm_fields(reference_farm)

    



def varieties(farmid:str):
    CUR.execute("""select array_agg(cv.crop_variety_name) as variety,
    array_agg(c.crop_subgroup) as subgroup,
    count(c.crop_subgroup) as subgroup_count,
    cv.farm_id
    from 
    "crop_variety" cv  
    join "crop" c on c.crop_id          = cv.crop_id
    left join "farm" f on c.farm_id     = f.farm_id
    where cv.farm_id = '%s'
    GROUP BY cv.farm_id, f.country_id, f.grid_points"""%farmid)
    i = CUR.fetchall()[0]

def get_mps_for_usr(usrid:str) -> int:
    CUR.execute(
        """
        select count(mp.management_plan_id) as mp_number from "crop_management_plan" cmp
    join "management_plan" mp on mp.management_plan_id = cmp.management_plan_id
    join  "users" u on mp.created_by_user_id = u.user_id
    where u.user_id = '%s'
        """ % usrid
    )
    return CUR.fetchone()[0]

def usr_fields():
    ...

def farm_fields(farmid:str)->bool:
    has_boundary         = 'farm_site_boundary' in Farm(farmid).locations
    has_3_locs           = len(Farm(farmid).all_poly()) >2
    print(Farm(farmid).locations.keys())
    return True



def driver():
    sheetpath = './SPG.xlsx'
    df     = pd.read_excel(sheetpath)
    sheet = df[['Active in Litefarm Spring 2022?','Farm ID', 'User ID', 'Associated Email Address']]

    for row in sheet.iterrows(): 
        index = row[0]
        _                               = row[1].tolist()
        [ active, farmid, usrid,email ] = _
        if type("") not in [type(active),type(farmid),type(usrid), type(email) ]:
            continue# all nan/Empty row



        rectify_via_email(email)

        
        

        if type("_") == type(farmid):
            # case: about to overwrite farmid
            val = input("""Original:\t\033[95m{}\033[0m\nIncoming:\t\033[93m{}\033[0m\n\033[95m[Y] to overwrite\033[0m|\033[93m[N] to overwrite\033[0m"""
                        .format(farmid,"b"))
            if val == "Y":
                print("s")
            else:
                ...
        

        if email == "cayoramonrivas@gmail.com":
            val = input("""Original:\t\033[95m{}\033[0m\nIncoming:\t\033[93m{}\033[0m\n\033[95m[Y] to overwrite\033[0m|\033[93m[N] to overwrite\033[0m""".format("a","b"))
            if val == "Y":
                print("s")
            else:
                ...

            print("IDX:",index)
            df.loc[index, [ "Farm ID","User ID",  ]]  =[ "hi","HELLO" ]


    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('SPG LiteFarm Census Data (in progress).xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Master-SPG-Data-v2')
    writer.save()



    
driver()