select  json_build_object(
    'id'         , u       .user_id    ,
    'first_name' , u       .first_name ,
    'last_name'  , u       .last_name  ,
    'email'      , u       .email      ,
    'bday'       , u       .birth_year ,
    'logincount', count(ul.user_log_id),
    'nfarms', userfarms.nfarms,
    'farmids', userfarms.farmids
)
from "userFarm" uf
join "users"    u  on uf.user_id = u.user_id
join "userLog"  ul on  u.user_id = ul.user_id
join (
    select uf.user_id,
    array_agg(uf.farm_id) as farmids,
    count(distinct( uf.farm_id )) as nfarms
    from "userFarm" uf 
    GROUP BY uf.user_id ) userfarms
on uf.user_id = userfarms.user_id
-- where uf.farm_id = '39bf12e0-de89-11eb-bcd8-0242ac120002'
GROUP BY u.user_id,u.first_name,u.last_name, u.email,u.birth_year, 
userfarms.nfarms, userfarms.farmids

-- userid "fbb9c928-c96a-11eb-8768-0242ac120002", "
-- userid "5fb715f39e9aad00761e4a49",  19 farms