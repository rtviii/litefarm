import sys
from xml.etree.ElementInclude import include
import geopandas as gpd
import pandas as pd
from farm import *

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

def rectify_via_email(email:str, original_farm_id=False, original_usr_id=False):
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

    if len( resp ) > 1: print("Multiple users with email {}. Exiting ".format(email)); return ["","","","","","","","",            "","","",""]

    try:
        [theirfams, usr_id, email, role] = resp[0]
        theirfams                        = str(theirfams).strip('{').strip('}').split(',')[0]
    except:
        print("User with email {} not found".format(email))
        return ["","","","","","","","", "","","",""]
        
    #---------------+----------------ᢹ----------------|
    reference_farm_id = original_farm_id if original_farm_id else theirfams
    print("Calculated reference farm id", reference_farm_id)
    reference_usr_id  = original_usr_id if original_usr_id else usr_id
    #---------------+----------------ᢹ----------------|


    [all_users, has_boundary,bound_area_ha, has_3_locs, n_locations] = farm_fields(reference_farm_id)
    n_crop_plans                                                     = get_mps_for_usr(reference_usr_id)
    [ n_unique_crop_varieties, n_unique_crop_subgroups ]             = unique_varieties_and_subgroups(reference_farm_id)

    return [reference_farm_id,
            reference_usr_id,
            email,
            role,
            all_users,
            has_boundary,
            bound_area_ha,
            has_3_locs,
            n_locations,
            n_crop_plans,
            n_unique_crop_subgroups,
            n_unique_crop_varieties]
    
def farm_fields(farmid:str):
    print("---------------------------1Farm fields got" ,farmid)
    F            = Farm(farmid)
    has_boundary = 'farm_site_boundary' in F.locations
    if  has_boundary:
        farmsite_boundary_area = sum(list(gpd.GeoSeries(F.locations['farm_site_boundary']).area))
        bound_area_ha          = float(farmsite_boundary_area)* 0.0001
    else:
        bound_area_ha    = F.total_area * 0.0001
    n_locations  = len(F.all_poly())
    has_3_locs   = n_locations >2
    all_users    = get_users_for_farm(farmid)
    return [all_users, has_boundary,bound_area_ha, has_3_locs, n_locations]

def unique_varieties_and_subgroups(farmid:str):

    CUR.execute("""
    select array_agg(cv.crop_variety_name) as variety,array_agg(c.crop_subgroup) as subgroup,cv.farm_id
    from 
    "crop_variety" cv  
    left join "crop" c on c.crop_id    = cv.crop_id
    left join "farm" f on c.farm_id    = f.farm_id
    where cv.farm_id = '%s'
    GROUP BY cv.farm_id"""%farmid)

    try:
        resp                           = CUR.fetchall()[0]
    except:
        return [-1,-1]
    [varieties, subgroups, farmid] = resp

    return [len(list(set(varieties))), len(list(set(subgroups)))]

def get_mps_for_usr(usrid:str) -> int:
    CUR.execute(
    """select count(cmp.management_plan_id) as cmp_number from "crop_management_plan" cmp
    join "management_plan" mp on mp.management_plan_id = cmp.management_plan_id
    join  "users" u on mp.created_by_user_id = u.user_id
    where u.user_id = '%s'""" % usrid)
    return CUR.fetchone()[0]


def driver():
    sheetpath = './spg-monday.xlsx'
    df        = pd.read_excel(sheetpath)
    kyc_cols  = ['Farm Name(s)','Farm ID','User ID', 'Associated Email Address']
    sheet     = df[kyc_cols]

    for row in sheet.iterrows(): 
        index                                   = row[0]
        _                                       = row[1].tolist()
        [ xlfarmname, xlfarmid, xlusrid,xlemail ] = _

        print("[{}]:".format(index), [ xlfarmname, xlfarmid, xlusrid,xlemail ])

        # ================================================= CLEANUP
        
        if type("") not in [type(xlfarmid),type(xlusrid), type(xlemail) ]:
            continue # all nan/empty row

        # ----------- fill userid if email is present
        # if str(xlusrid) == 'nan':
        #     if str(xlemail) == 'nan': continue
        #     print("empty usrid. try to get by user email")

        #     # CUR.execute("select user_id from users u where u.email ='%s'" % xlemail)
        #     print(xlemail)
        #     CUR.execute("select user_id from \"users\" u where u.email = '%s'" % xlemail)
            
        #     userid = CUR.fetchall()
        #     print("Got uid", userid)


        # ---------------------------------Fill email if userid is present
        # if str(xlemail) == 'nan':
        #     if str(xlusrid) == 'nan':continue
        #     print("empty email. try to get by user id")
        #     cur.execute("select u.email from users u where u.user_id =  '%s'" % xlusrid)
        #     computed_email = cur.fetchall()
        #     if len(computed_email) > 0:
        #         xlemail = computed_email[0][0]
        #         # df.loc[df.index[index], 'associated email address'] = xlemail
        #     else:
        #         continue

        # ----------- fill farmid if xlusri is present; if multiple farm, choose only those with locations, if more than one: concant via coma
        # if str(xlfarmid) == 'nan':
        #     if str(xlemail) == 'nan': continue
        #     print("empty usrid. try to get by user email")

        #     # CUR.execute("select user_id from users u where u.email ='%s'" % xlemail)
        #     print(xlemail)
        #     CUR.execute("select user_id from \"users\" u where u.email = '%s'" % xlemail)
            
        #     userid = CUR.fetchall()
        #     print("Got uid", userid)
        
        

        # ================================================= Setter


        sought = df.loc[index,["is_boundary_mapped",	
                      "area_within_boundary_ha",
                      "area_all_locations_ha",
                      "has_3_locations",
                      "n_locations",
                      "n_crop_plans",
                      "n_crop_subgroups",
                      "n_unique_crop_varieties" ]]

        # print("Computed rows:")
        # if int(index) > 45:
            # print(get_rows_for_farmid(xlfarmid, xlusrid))

        df.loc[index,[
                    "is_boundary_mapped",	
                    "area_within_boundary_ha",
                    "area_all_locations_ha",
                    "has_3_locations",
                    "n_locations",
                    "n_crop_plans",
                    "n_crop_subgroups",
                    "n_unique_crop_varieties" ]] = get_rows_for_farmid(xlfarmid,xlusrid)
        # ================================================= 


    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('spg-monday.xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Master-SPG-Data-v2')
    writer.save()


def get_rows_for_farmid(farmid:str, usrid:str):
    # try:
    print("Got farmid", str(farmid))
    if str(farmid) == 'nan' or '/' in farmid: return [""]*8
    else:
        f                       = Farm(farmid)
        is_boundary_mapped      = 'farm_site_boundary' in f.locations
        area_within_boundary_ha = unary_union(f.locations['farm_site_boundary']).area / 10**4 if is_boundary_mapped  else 'N/A' 
        area_all_locations_ha   = f.total_area  /10**4
        try:
            has_3_locations         = "True" if len(get_farm_locs(farmid)) > 2 else "False"
        except: 
            has_3_locations = "False"
        try:
            n_locations                                 = len(get_farm_locs(farmid))
        except:
            n_locations = 'N/A'
        n_crop_plans                                = get_mps_for_usr(usrid)
        [ n_crop_subgroups,n_unique_crop_varieties] = unique_varieties_and_subgroups(farmid)

        result = [is_boundary_mapped,	
                    area_within_boundary_ha,
                    area_all_locations_ha,
                    has_3_locations,
                    n_locations,
                    n_crop_plans,
                    n_crop_subgroups,
                    n_unique_crop_varieties ]
        return  result
    # except:
    #     print("Could not initialize farm.")
    #     return [""]*7

    




    
driver()