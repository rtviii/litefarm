from litefarm import get_cleaned_farms, litefarm
import pandas as pd
from .farm_variables import FarmVariable


def farm_count():
    return len(get_cleaned_farms().index)


def get_farm_total_area(farm_df):
    locations = litefarm("SELECT * FROM location WHERE NOT deleted")
    figures = litefarm("SELECT * FROM figure")
    areas = litefarm("SELECT * FROM area")

    figures = figures[figures.type == "farm_site_boundary"]

    lfa = pd.merge(
        pd.merge(locations, figures, on="location_id", how="inner"),
        areas,
        on="figure_id",
        how="inner",
    )

    for farm_id in farm_df.farm_id:
        farm_df.loc[farm_df.farm_id == farm_id, "Farm site area"] = (
            lfa[lfa.farm_id == farm_id].total_area.sum() / 10000
        )
    if "Farm site area" not in farm_df.columns:
        farm_df["Farm site area"] = None
    return farm_df


def get_farm_productive_area(farm_df):
    locations = litefarm("SELECT * FROM location WHERE NOT deleted")
    figures = litefarm("SELECT * FROM figure")
    areas = litefarm("SELECT * FROM area")

    figures = figures[figures.type.isin(["field", "greenhouse", "garden"])]

    lfa = pd.merge(
        pd.merge(locations, figures, on="location_id", how="inner"),
        areas,
        on="figure_id",
        how="inner",
    )

    for farm_id in farm_df.farm_id:
        farm_df.loc[farm_df.farm_id == farm_id, "Productive area"] = (
            lfa[lfa.farm_id == farm_id].total_area.sum() / 10000
        )
    if "Productive area" not in farm_df.columns:
        farm_df["Productive area"] = None
    return farm_df


def get_farm_diversity(farm_df):
    crop_variety = litefarm("SELECT * FROM crop_variety WHERE NOT deleted")

    farm__crop_variety = pd.merge(farm_df, crop_variety, on="farm_id", how="left")

    farm_df_copy = farm__crop_variety.groupby("farm_id").agg({"crop_id": "count"})
    farm_df["Crop diversity"] = farm_df_copy["crop_id"].values
    return farm_df


def get_farm_locations(farm_df):
    locations = litefarm("SELECT * FROM location WHERE NOT deleted")
    farm_locations = pd.merge(farm_df, locations, on="farm_id", how="left")
    farm_locations = farm_locations.groupby("farm_id").agg({"location_id": "count"})
    farm_df["Number of location shapes"] = farm_locations["location_id"].values
    return farm_df


def count_farm_boundary_shapes(farm_df):
    locations = litefarm("SELECT * FROM location WHERE NOT deleted")
    farm_site_boundary = litefarm("SELECT location_id from farm_site_boundary")
    locations = locations[locations.location_id.isin(farm_site_boundary.location_id)]
    farm_locations = pd.merge(farm_df, locations, on="farm_id", how="left")
    farm_locations = farm_locations.groupby("farm_id").agg({"location_id": "count"})
    farm_df["Number of boundary shapes"] = farm_locations["location_id"].values
    return farm_df


def count_natural_areas(farm_df):
    locations = litefarm("SELECT * FROM location WHERE NOT deleted")
    natural_areas = litefarm("SELECT * FROM natural_area")
    farm_locations = pd.merge(farm_df, locations, on="farm_id", how="left")
    farm_locations = pd.merge(
        farm_locations, natural_areas, on="location_id", how="left"
    )
    farm_locations = farm_locations.groupby("farm_id").agg({"location_id": "count"})
    farm_df["Number of natural areas"] = farm_locations["location_id"].values
    return farm_df


def get_farm_natural_area(farm_df):
    locations = litefarm("SELECT * FROM location WHERE NOT deleted")
    figures = litefarm("SELECT * FROM figure")
    areas = litefarm("SELECT * FROM area")

    figures = figures[figures.type.isin(["natural_area"])]

    lfa = pd.merge(
        pd.merge(locations, figures, on="location_id", how="inner"),
        areas,
        on="figure_id",
        how="inner",
    )

    for farm_id in farm_df.farm_id:
        farm_df.loc[farm_df.farm_id == farm_id, "Natural area"] = (
            lfa[lfa.farm_id == farm_id].total_area.sum() / 10000
        )
    if "Natural area" not in farm_df.columns:
        farm_df["Natural area"] = None
    return farm_df


def get_farm_crop_management_plans_count(farm_df):
    cmp = litefarm("SELECT * FROM crop_management_plan")
    mp = litefarm("SELECT * FROM management_plan WHERE NOT deleted")
    cv = litefarm("SELECT * FROM crop_variety")

    farm_ids = farm_df.farm_id.unique()
    cv = cv[cv.farm_id.isin(farm_ids)]

    cmp_count = pd.merge(cv, mp, on="crop_variety_id", how="inner")
    cmp_count = pd.merge(cmp_count, cmp, on="management_plan_id", how="inner")
    cmp_count = cmp_count.groupby("farm_id").agg({"management_plan_id": "count"})

    farm_cmp_count = pd.merge(farm_df, cmp_count, on="farm_id", how="left")

    farm_df["Number of crop management plans"] = farm_cmp_count[
        "management_plan_id"
    ].values
    return farm_df


# Keep this at the end of this file and add new variables to the list
VARIABLES = [
    FarmVariable("Farm site area", get_farm_total_area, "ha", "average", "Locations"),
    FarmVariable(
        "Productive area", get_farm_productive_area, "ha", "average", "Locations"
    ),
    FarmVariable("Crop diversity", get_farm_diversity, "", "average", "Crops"),
    FarmVariable("Natural area", get_farm_natural_area, "ha", "average", "Locations"),
    FarmVariable(
        "Number of location shapes", get_farm_locations, "", "average", "Locations"
    ),
    FarmVariable(
        "Number of boundary shapes",
        count_farm_boundary_shapes,
        "",
        "average",
        "Locations",
    ),
    FarmVariable(
        "Number of natural areas", count_natural_areas, "", "average", "Locations"
    ),
    FarmVariable(
        "Number of crop management plans",
        get_farm_crop_management_plans_count,
        "",
        "average",
        "Farm management",
    ),
]
