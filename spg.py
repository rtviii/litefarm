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
        [theirfams, usr_id, email, role]                   = resp[0]
        theirfams = str(theirfams).strip('{').strip('}').split(',')[0]
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
    sheetpath = './SPG-post-friday.xlsx'
    df        = pd.read_excel(sheetpath)
    kyc_cols  = ['Farm Name(s)','Farm ID','User ID', 'Associated Email Address']

    sheet     = df[kyc_cols]

    for row in sheet.iterrows(): 

        index                                   = row[0]
        _                                       = row[1].tolist()

        [ xlactive, xlfarmid, xlusrid,xlemail ] = _
        print("[{}]:".format(index), [ xlactive, xlfarmid, xlusrid,xlemail ])
        if type("") not in [type(xlfarmid),type(xlusrid), type(xlemail) ]:
            continue # all nan/empty row
    
        if str(xlemail) == 'nan':
            if type(xlusrid) != float and str(xlusrid) != 'nan':
                CUR.execute("""select email from "users" u where u.user_id =  '%s'"""%xlusrid)
                xlemail = CUR.fetchone()[0]
                df.loc[index,"Associated Email Address"] = xlemail

            elif type(xlfarmid) != float and str(xlfarmid) != 'nan' :
                CUR.execute("""
                select u.email from  "farm" f  join "users" u
                    on f.created_by_user_id = u.user_id
                    where f.farm_id = '%s'
                            """%xlfarmid)
                resp = CUR.fetchall()[0]
                print("GOT EMAILS fo rthis farm : ",resp)
            else: 
                ...
                
                
        if type(xlusrid) == float: xlusrid  = False
        if type(xlfarmid) == float: xlfarmid  = False

            # elif str(xlfarmid) != 'nan':
            #     str(xlfarmid).strip(" ")



        
              

        [reference_farm_id,
        reference_usr_id,
        email,
        role,
        user_ids_for_farm,
        farm_site_boundary_exists,
        bound_area_ha,
        has_3_locations,
        n_locations,
        n_crop_plans,
        n_unique_crop_subgroups,
        n_unique_crop_varieties] = rectify_via_email(str(xlemail).strip(" "), 
                                                     original_farm_id = xlfarmid if str(xlfarmid)!='nan' and not ( '/'  in str( xlfarmid ) )else False,
                                                     original_usr_id  = xlusrid  if str(xlusrid) !='nan' else False)

        # if type("_") == type(xlfarmid) and xlfarmid != reference_farm_id:
        #     # case: about to overwrite farmid
        #     val = input("""FARM Original:\t\033[95m{}\033[0m\nIncoming:\t\033[93m{}\033[0m\n\033[95m[Y] to overwrite\033[0m|\033[93m[N] to overwrite\033[0m"""
        #                 .format(xlfarmid,reference_farm_id))
        #     if val == "Y":
        #         df.loc[index,  "Farm ID"  ] = reference_farm_id
        #     else:
        #         ...
        # if type("_") == type(xlusrid) and xlusrid != reference_usr_id:
        #     # case: about to overwrite farmid
        #     val = input("""USER Original:\t\033[95m{}\033[0m\nIncoming:\t\033[93m{}\033[0m\n\033[95m[Y] to overwrite\033[0m|\033[93m[N] to overwrite\033[0m"""
        #                 .format(xlfarmid,reference_farm_id))
        #     if val == "Y":
        #         df.loc[index,  "User ID"  ] = reference_usr_id
        #     else:
                # ...

        # print("")
        # print("Attempting to set: ")
        # print("role:\t", role,)
        # print("user_ids_for_farm:\t", user_ids_for_farm,)
        # print("farm_site_boundary_exists:\t", farm_site_boundary_exists,)
        # print("bound_area_ha:\t", bound_area_ha,)
        # print("has_3_locations:\t", has_3_locations,)
        # print("n_locations:\t", n_locations,)
        # print("n_crop_plans:\t", n_crop_plans,)
        # print("n_unique_crop_subgroups:\t", n_unique_crop_subgroups,)
        # print("n_unique_crop_varieties:\t", n_unique_crop_varieties)
        # print("")

        
        # ================================================= Setter

        df.loc[index,["role", 
                      "user_ids_for_farm",
                      "farm_site_boundary_exists",
                      "bound_area_ha",
                      "has_3_locations",
                      "n_locations",
                      "n_crop_plans",
                      "n_unique_crop_subgroups",
                      "n_unique_crop_varieties"]] = \
        np.array([role,
        user_ids_for_farm,
        farm_site_boundary_exists,
        bound_area_ha,
        has_3_locations,
        n_locations,
        n_crop_plans,
        n_unique_crop_subgroups,
        n_unique_crop_varieties], dtype=object)
        # ================================================= 


    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('spg-filled1.xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Master-SPG-Data-v2')
    writer.save()



    
driver()