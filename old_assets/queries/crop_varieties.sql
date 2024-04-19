-- select array_agg(cv.crop_variety_name) as variety,
--     array_agg(c.crop_subgroup) as subgroup,
--     array_agg(c.crop_group) as group,
--     cv.farm_id
-- from 
-- "crop_variety" cv  
-- join "crop" c on c.crop_id                = cv.crop_id
-- left join "farm" f on c.farm_id     = f.farm_id
-- GROUP BY cv.farm_id , f.country_id, f.grid_points

-- --------------------------------------------------------------------------------------
select array_agg(cv.crop_variety_name) as variety,
    array_agg(c.crop_subgroup) as subgroup,
    count(c.crop_subgroup) as subgroup_count,
    cv.farm_id
from 
"crop_variety" cv  
join "crop" c on c.crop_id          = cv.crop_id
left join "farm" f on c.farm_id     = f.farm_id
where cv.farm_id = '0093cc60-39b8-11ec-88c0-0242ac150003'
GROUP BY cv.farm_id, f.country_id, f.grid_points
