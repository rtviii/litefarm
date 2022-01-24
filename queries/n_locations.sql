
-- By farm-id
SELECT ufarm.farm_id, COUNT(loc.created_at) AS nloc
FROM "userFarm" ufarm JOIN "location" loc ON ufarm.farm_id=loc.farm_id 
GROUP BY   ufarm.farm_id ORDER BY nloc DESC

-- By user
-- SELECT   u.last_name , fnloc.nloc FROM "users" u join 
--     (SELECT ufarm.farm_id, ufarm.user_id, COUNT(loc.created_at) AS nloc
--     FROM "userFarm" ufarm JOIN "location" loc ON ufarm.farm_id=loc.farm_id 
--     GROUP BY  ufarm.user_id, ufarm.farm_id ORDER BY nloc DESC) as fnloc 
-- on fnloc.user_id = u.user_id GROUP BY  u.last_name, fnloc.nloc ORDER BY fnloc.nloc desc
