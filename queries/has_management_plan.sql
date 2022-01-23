SELECT count(mp.created_by_user_id) as has_mps, u.user_id, u.first_name ,u.last_name 
from "management_plan"  mp join "users" u on mp.created_by_user_id = u.user_id group by  u.user_id ORDER BY has_mps desc;
