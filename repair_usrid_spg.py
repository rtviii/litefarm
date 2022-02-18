import sys
from xml.etree.ElementInclude import include
import geopandas as gpd
import pandas as pd
from farm import *
    



def driver():
    sheetpath = './SPG.xlsx'
    df     = pd.read_excel(sheetpath)
    sheet = df[['Active in Litefarm Spring 2022?','Farm ID', 'User ID', 'Associated Email Address']]

    for row in sheet.iterrows(): 
        index = row[0]
        _                               = row[1].tolist()
        [ xlactive, xlfarmid, xlusrid,xlemail ] = _
        print("[{}]:".format(index), [ xlactive, xlfarmid, xlusrid,xlemail ])
        if type("") not in [type(xlfarmid),type(xlusrid), type(xlemail) ]:
            continue # all nan/empty row
        if str(xlemail).strip(" ") != 'nan':
                CUR.execute("""select 
            array_agg(uf.farm_id) as farmids,
            uf.user_id, 
            u.email
            from "userFarm" uf 
            join "users" u on uf.user_id = u.user_id 
            join "role" rl on rl.role_id = uf.role_id 
            where u.email ='%s'
            GROUP BY uf.user_id, u.first_name, u.last_name,u.email, rl.role"""%str(xlemail).strip(" "))
    
        resp = CUR.fetchall()

        if len( resp ) > 1: print("Multiple users with email {}. Exiting ".format(xlemail))
        try:
            [theirfarms, usr_id, email ]                   = resp[0]
            if type(xlfarmid) in [float]:
                df.loc[index,"Farm ID"] = str( theirfarms ).strip("{").strip("}").split(",")[0]
            if type(xlusrid) in [float]:
                df.loc[index,"User ID"] = usr_id
        except:
            ...

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
            else: 
                ...
                
                
        if type(xlusrid)  == float: xlusrid  = False
        if type(xlfarmid) == float: xlfarmid  = False

            # elif str(xlfarmid) != 'nan':
            #     str(xlfarmid).strip(" ")





    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('spg-filled.xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Master-SPG-Data-v2')
    writer.save()



    
driver()