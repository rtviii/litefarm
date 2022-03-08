-- select count(ul.created_at) as nlogins, u.user_id, u.first_name, u.last_name from "userLog"  ul
-- join users u on u.user_id = ul.user_id group by u.user_id, u.first_name,u.last_name order by nlogins desc

select farm_id from "userFarm" ;