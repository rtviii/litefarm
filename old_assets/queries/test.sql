select * from farm f where f.farm_id = '3f13e920-89a9-11ec-84b5-0242ac150004'
[ "0f893636-3d8e-11ec-935a-0242ac150003", "1bdf2b9c-202b-11eb-bdb3-22000obb9251f" ]

select count(r.role) from "userFarm" u join "role" r on u.role_id = r.role_id where role ='Owner'
select u.email from users u where u.user_id =  '5fce83c1748ff50068e28fdd'

select farm_id from "farm" f where f.country_id = 211


select * from farm f 
join users u
on f.updated_by_user_id = u.user_id
where u.email = ''


select * from "location" where farm_id ='d68bad7a-6ff5-11eb-a53d-22000a6ddaf5'
select count(*) from "location" where farm_id ='d68bad7a-6ff5-11eb-a53d-22000a6ddaf5' and deleted = 'false'

select * from "location" where farm_id='d68bad7a-6ff5-11eb-a53d-22000a6ddaf5'



SELECT fig.type, area.grid_points, ln.line_points , pt.point
FROM "farm" ufarm
JOIN  "location" loc ON ufarm.farm_id    = loc.farm_id
JOIN  "figure" fig ON  fig.location_id   = loc.location_id
FULL JOIN "area" area on area.figure_id = fig.figure_id 
FULL JOIN "line" ln  on ln.figure_id    = fig.figure_id
FULL JOIN "point" pt  on pt.figure_id   = fig.figure_id
where ufarm.farm_id = 'd68bad7a-6ff5-11eb-a53d-22000a6ddaf5' and loc.deleted = 'false'

select f.farm_id from farm f 

-- SELECT location_id FROM "farm" ufarm
-- FULL JOIN  "location" loc ON ufarm.farm_id = loc.farm_id
-- where ufarm.farm_id = 'd68bad7a-6ff5-11eb-a53d-22000a6ddaf5'

-- SELeCT * from "userFarm" uf where uf.farm_id ='d68bad7a-6ff5-11eb-a53d-22000a6ddaf5'

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