-- select * from "area" where figure_id = 'e0a949f2-3377-11ec-a74c-0242ac130002';
-- SELECT * FROM "point" where figure_id = 'b4f7ba2c-31d4-11ec-8ed0-0242ac130002';
-- select type, location.location_id from "location" join "figure" on location.location_id = figure.location_id where farm_id = '0ad0ce20-3112-11ec-b36e-0242ac130002'


-- select count(mp.management_plan_id) as mp_number from "crop_management_plan" cmp
-- join "management_plan" mp on mp.management_plan_id = cmp.management_plan_id
-- join  "users" u on mp.created_by_user_id = u.user_id
-- where u.user_id = '58ceac20-3809-11ec-b613-0242ac150003'


select 
        array_agg(uf.farm_id) as farmids,
        uf.user_id, 
        u.email,
        rl.role
        from "userFarm" uf 
        join "users" u on uf.user_id = u.user_id 
        join "role" rl on rl.role_id = uf.role_id 
        where u.email ='cayoramonrivas@gmail.com'
        GROUP BY uf.user_id, u.first_name, u.last_name,u.email, rl.role