-- select uf.user_id, u.first_name, u.last_name,
-- array_agg(uf.farm_id) as farmids,
-- count(distinct( uf.farm_id )) as nfarms
-- from "userFarm" uf 
-- join "users" u on uf.user_id = u.user_id
-- GROUP BY uf.user_id, u.first_name, u.last_name
-- ORDER BY nfarms DESC

-- select uf.user_id, u.first_name, u.last_name, array_agg(uf.farm_id) as farmids, count(distinct( uf.farm_id )) as nfarms
-- from "userFarm" uf 
-- join "users" u on uf.user_id = u.user_id
-- GROUP BY uf.user_id, u.first_name, u.last_name
-- ORDER BY nfarms DESC


-- User with role
select 
    uf.user_id, 
    rl.role, 
    u.first_name, 
    u.last_name, 
    u.email,
    array_agg(uf.farm_id) as farmids, 
    count(distinct( uf.farm_id )) as nfarms
from "userFarm" uf 
join "users" u on uf.user_id = u.user_id 
join "role" rl on rl.role_id = uf.role_id 
where u.email ='Stroher.ivete@gmail.com'
GROUP BY uf.user_id, u.first_name, u.last_name,u.email, rl.role



-- 
-- select array_agg(json_build_object(
--     'user_id',u.user_id,
--     'last_name',u.last_name,
--     'first_name',u.first_name)) as all_users_on_this_farm
-- from "users" u
-- join "userFarm" uf  on uf.user_id = u.user_id
-- WHERE uf.farm_id='5118f598-8815-11eb-88f9-0a7facd3678d'


-- select email from "users" u where u.user_id =  '5fd2672b8734ba0068f0444d'
-- select * from "users" u WHERE u.email = 'wagroeco16@gmail.com'


