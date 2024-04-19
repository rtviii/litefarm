from .get_data import DataGetter, expand_grid_points_coordinates
import os

_required_config = [
    "LITEFARM_DB_HOST",
    "LITEFARM_DB_USER",
    "LITEFARM_DB_PASSWORD",
    "LITEFARM_DB_NAME",
    "LITEFARM_DB_SSH_KEY",
]

_config = {key: os.environ[key] for key in _required_config}

DG                             = DataGetter(config=_config)
get_cleaned_farms              = DG.get_cleaned_farms
litefarm                       = DG.litefarm
expand_grid_points_coordinates = expand_grid_points_coordinates
get_active_farms               = DG.get_active_farms

# might be an issue where this is not updated after the app is started
ALL_COUNTRIES       = DG.all_countries()
ALL_ORGANIZATIONS   = DG.all_organizations()  # same here
spg_available_years = DG.spg_available_years
