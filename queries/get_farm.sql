select 
    f.farm_id,
    (select c.country_name from "countries" c where c.id = f.country_id),
    f.grid_points,
    array_agg(cv.crop_variety_name) as variety,
    array_agg(c.crop_subgroup) as subgroup
from "farm" f 
left join "crop_variety" cv  on cv.farm_id = f.farm_id
left join "crop" c on c.crop_id = cv.crop_id
GROUP BY f.farm_id
