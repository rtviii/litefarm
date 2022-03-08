-- select * from farm f where f.farm_id = '3f13e920-89a9-11ec-84b5-0242ac150004'
-- select * from users u WHERE u.email = 'sitioflorbela@gmail.com'
-- [ "0f893636-3d8e-11ec-935a-0242ac150003", "1bdf2b9c-202b-11eb-bdb3-22000obb9251f" ]

select count(r.role) from "userFarm" u join "role" r on u.role_id = r.role_id where role ='Owner'