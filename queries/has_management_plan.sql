-- select cv.crop_variety_name, cv.farm_id  from "crop_variety" cv 
--  join "farm" f on cv.farm_id = f.farm_id where f.farm_id = '56d00778-7abe-11ec-8e4a-0242ac150004';

---------------------------------------------------------------------------------------------------------------

-- select *  from "crop" c;

---------------------------------------------------------------------------------------------------------------
-- select cv.crop_variety_name, cv.crop_id,  c.crop_common_name ,  cv.farm_id  from "crop_variety" cv
-- left outer join "crop" c on c.crop_id = cv.crop_id  where cv.farm_id='f8efc7aa-4bb1-11ec-9a56-0242ac150004';

---------------------------------------------------------------------------------------------------------------
select cv.crop_variety_name,  c.crop_group, c.farm_id   from "crop_variety" cv 
join "crop" c  on c.crop_id = cv.crop_id


-- GROUP BY cv.farm_id;
-- select array_agg(cv.crop_variety_name) , cv.farm_id  from "crop_variety" cv GROUP BY cv.farm_id;


---------------------------------------------------------------------------------------------------------------
-- management_plan vs crop_management_plans
-- select farm_id from "crop_management_plan" cpm join "management_plan" mp on cpm.management_plan_id = mp.management_plan_id;



