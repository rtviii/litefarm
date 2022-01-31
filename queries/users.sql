select uf.user_id, u.first_name, u.last_name,
array_agg(uf.farm_id) as farmids,
count(distinct( uf.farm_id )) as nfarms
from "userFarm" uf 
join "users" u on uf.user_id = u.user_id
GROUP BY uf.user_id, u.first_name, u.last_name
ORDER BY nfarms DESC