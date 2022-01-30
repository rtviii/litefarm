
-- By farm-id
SELECT ufarm.farm_id, COUNT(distinct loc.location_id) AS nloc
FROM "userFarm" ufarm 
JOIN "location" loc ON ufarm.farm_id=loc.farm_id 
GROUP BY ufarm.farm_id ORDER BY nloc DESC

-- By user
-- SELECT   u.last_name , fnloc.nloc FROM "users" u join 
--     (SELECT ufarm.farm_id, ufarm.user_id, COUNT(loc.created_at) AS nloc
--     FROM "userFarm" ufarm JOIN "location" loc ON ufarm.farm_id=loc.farm_id 
--     GROUP BY  ufarm.user_id, ufarm.farm_id ORDER BY nloc DESC) as fnloc 
-- on fnloc.user_id = u.user_id GROUP BY  u.last_name, fnloc.nloc ORDER BY fnloc.nloc desc

-- Locations in a given farm

-- SELECT 
-- fig.type,area.grid_points, ln.line_points , pt.point
-- FROM "userFarm" ufarm 
-- JOIN  "location" loc ON ufarm.farm_id    = loc.farm_id
-- JOIN  "figure" fig ON  fig.location_id   = loc.location_id
-- FULL  JOIN "area" area on area.figure_id = fig.figure_id
-- FULL  JOIN "line" ln  on ln.figure_id    = fig.figure_id
-- FULL  JOIN "point" pt  on pt.figure_id   = fig.figure_id
-- where ufarm.farm_id = 'ca713386-3050-11ec-b23b-0242ac130002'

-- [744bd3ec-1e2e-11eb-ae60-22000bb9251f]
-- [1c0480ec-3054-11ec-be02-0242ac130002]
-- [b5ebef20-3035-11ec-93d7-0242ac130002]
-- [46959140-faba-11eb-be62-0242ac120002]
-- [1fa9ded2-25f4-11ec-8078-0242ac130003]
-- [3b3b07b6-2621-11ec-b499-0242ac130003]
-- [6d921860-31b8-11ec-adce-0242ac130002]
-- [71d84984-88cc-11eb-84e5-0a7facd3678d]
-- [39bf12e0-de89-11eb-bcd8-0242ac120002]
-- [348443ec-5f20-11eb-bd86-22000ab2b8c4]
-- [9386af92-304e-11ec-b382-0242ac130002]
