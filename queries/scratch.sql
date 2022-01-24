-- select * from "area" where figure_id = 'e0a949f2-3377-11ec-a74c-0242ac130002';
-- SELECT * FROM "point" where figure_id = 'b4f7ba2c-31d4-11ec-8ed0-0242ac130002';
select type, location.location_id from "location" join "figure" on location.location_id = figure.location_id where farm_id = '0ad0ce20-3112-11ec-b36e-0242ac130002'