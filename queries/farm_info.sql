select 
u.user_id    as uid   ,
u.first_name as name  ,
u.last_name as lastname ,
u.email      as email ,
u.birth_year as bday  

from "userFarm" uf
join "users"    u

on    uf.user_id = u.user_id
where uf.farm_id = 'ffe46f9e-c96a-11eb-8768-0242ac120002'
