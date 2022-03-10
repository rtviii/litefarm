-- select * from farm f where f.farm_id = '3f13e920-89a9-11ec-84b5-0242ac150004'
-- select * from users u WHERE u.email = 'sitioflorbela@gmail.com'
-- [ "0f893636-3d8e-11ec-935a-0242ac150003", "1bdf2b9c-202b-11eb-bdb3-22000obb9251f" ]

-- select count(r.role) from "userFarm" u join "role" r on u.role_id = r.role_id where role ='Owner'
-- select u.email from users u where u.user_id =  '5fce83c1748ff50068e28fdd'

-- select farm_id from "farm" f where f.country_id = 211

-- select user_id from "users" u where u.email = 'maramoster@gmail.com'
-- select user_id from "users" u where u.email = 'maramoster@gmail.com'
	




select * from farm f 
join users u
on f.updated_by_user_id = u.user_id
where u.email = 'carlosarzamendaapro@gmail.com'






-- 28 Brazil
-- 37 Canada
-- 211 United Kingdom
-- 212 United States
-- 128 Mexico

-- select array_agg(uf.farm_id) as farmids,
--         uf.user_id, 
--         u.email,
--         rl.role
--         from "userFarm" uf 
--         join  "users" u on uf.user_id = u.user_id
--         join  "role" rl on rl.role_id = uf.role_id
--         where u.email                 = 'alfonso8munoshuerta@gmail.com'
        -- GROUP BY uf.user_id, u.first_name, u.last_name,u.email, rl.role