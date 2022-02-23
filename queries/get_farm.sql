select 
    f.farm_id,
    (select c.country_name from "countries" c where c.id = f.country_id),
    f.grid_points,
    array_agg(cv.crop_variety_name) as variety  ,
    array_agg(c .crop_subgroup    ) as subgroup 

from "farm" f
left join "crop_variety" cv  on cv.farm_id = f.farm_id
left join "crop" c on c.crop_id            = cv.crop_id
GROUP BY f.farm_id

            -- json_build_object(
            -- 'loctype', fig.type,
            -- 'loc_id' , loc.location_id
            -- 'area_pts', area.grid_points,
            -- 'line_pts', line.line_points,
            -- 'point_pts', point.point
            -- )

            -- left  join "area"   area  on area.figure_id  = fig.figure_id
            -- left  join "line"   line  on line.figure_id  = fig.figure_id
            -- left  join "point"  point on point.figure_id = fig.figure_id
            -- where location.farm_id                       = f.farm_id