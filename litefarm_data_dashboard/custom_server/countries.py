from litefarm import get_cleaned_farms, litefarm, get_active_farms, ALL_COUNTRIES
import pandas as pd
from itables.shiny import DT
from .farms import (
    get_farm_total_area,
    get_farm_productive_area,
    get_farm_diversity,
    VARIABLES,
)
import plotly.graph_objects as go
import plotly.subplots as sp
from datetime import datetime, date
from .farm_variables import find_variable_in_variable_list
import sys


def country_overview(year, countries, variable_names, minimum=10):
    """
    Returns a pandas dataframe (wrapped in a DT object) with countries, the number of farms, and all variables that are given as input.

    It drops countries with less than minimum farms.
    """
    # If no countries are given, all countries are returned.
    if len(countries) == 0:
        countries = ALL_COUNTRIES

    # We get the data from LF db
    farms_df = get_cleaned_farms()
    countries_df = litefarm("SELECT * FROM countries")

    # Filters
    countries_df = countries_df[countries_df.country_name.isin(countries)]
    farms_df = farms_df[farms_df.created_at.dt.year >= int(year)]

    # Merge
    farms_df = pd.merge(
        farms_df, countries_df, left_on="country_id", right_on="id", how="inner"
    )[["farm_id", "country_name"]]

    # Get all variables and relevant info on how to format the table
    variables = []
    agg_dict = {
        "farm_id": "count",
    }
    rename_dict = {
        "country_name": "Country",
        "farm_id": "# farms",
    }

    for variable_name in variable_names:
        variable = find_variable_in_variable_list(VARIABLES, variable_name)
        variables.append(variable)
        farms_df = variable.function(farms_df)
        agg_dict[variable.name] = "mean"
        rename_dict[variable.name] = variable.full_name

    # Now we aggregate everything in a nice table
    table = (
        farms_df.groupby("country_name")
        .agg(agg_dict)
        .reset_index()
        .rename(columns=rename_dict)
        .sort_values(by="# farms", ascending=False)
    )

    # Remove countries with less than minimum farms
    table = table[table["# farms"] >= minimum]
    table = table[list(rename_dict.values())].reset_index(drop=True)

    table = table.fillna("-")  # Nice looking na values
    with pd.option_context("display.float_format", "{:,.2f}".format):
        return DT(table)


def overview_hist(year, countries, variable_names):
    """
    Returns a plotly figure with histograms of the given variables for the given countries.
    """
    number_of_rows = len(variable_names) // 2 + len(variable_names) % 2
    if number_of_rows == 0:
        fig = go.Figure()
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            text="You can select variables to plot on the left panel",
            showarrow=False,
            font=dict(size=28),
            bgcolor="rgba(255, 255, 255, 0.5)",
            bordercolor="rgba(255, 255, 255, 0.5)",
            borderwidth=1500,
        )
        return fig
    if len(countries) == 0:
        countries = ALL_COUNTRIES
    farms_df = get_cleaned_farms()
    countries_df = litefarm("SELECT * FROM countries")
    countries_df = countries_df[countries_df.country_name.isin(countries)]
    farms_df = farms_df[farms_df.created_at.dt.year >= int(year)]
    farms_df = pd.merge(
        farms_df, countries_df, left_on="country_id", right_on="id", how="inner"
    )[["farm_id", "country_name"]]

    variables = []

    for variable_name in variable_names:
        variables.append(find_variable_in_variable_list(VARIABLES, variable_name))
    fig = sp.make_subplots(
        rows=number_of_rows,
        cols=2,
        subplot_titles=[variable.full_name for variable in variables],
        shared_yaxes=True,
    )
    for i, variable in enumerate(variables):
        data = variable.function(farms_df)
        fig.add_trace(
            go.Histogram(
                x=data[variable.name],
                nbinsx=20,
                name=variable.full_name,
            ),
            row=i // 2 + 1,
            col=i % 2 + 1,
        )
        fig.update_layout(height=number_of_rows * 500, bargap=0.20)
    return fig


def new_farms_evolution(
    years,
    countries,
):
    """
    Returns a plotly figure with the evolution of the number of new farms per month.

    Not used at the moment, but stays here for maybe later
    """
    MIN_DATE = datetime(2021, 1, 31, 0, 0, 0)
    if len(countries) == 0:
        countries = ALL_COUNTRIES

    date_range = date(int(min(years)), 1, 1), date(int(max(years)), 12, 31)

    farms_df = get_cleaned_farms()
    countries_df = litefarm("SELECT * FROM countries")
    countries_df = countries_df[countries_df.country_name.isin(countries)]
    farms_df = pd.merge(
        farms_df, countries_df, left_on="country_id", right_on="id", how="inner"
    )

    farms_df["registration_date"] = farms_df.created_at.apply(
        lambda x: datetime.fromtimestamp(x)
        if datetime.fromtimestamp(x) >= MIN_DATE
        else MIN_DATE
    )
    data = (
        farms_df.groupby("registration_date")
        .agg({"farm_id": "count"})
        .cumsum()
        .reset_index()
        .rename(
            columns={"farm_id": "Total number of farms", "registration_date": "Date"}
        )
    )
    data = data[
        (data.Date >= pd.to_datetime(date_range[0]))
        & (data.Date <= pd.to_datetime(date_range[1]))
    ]
    fig = go.Figure(
        go.Scatter(
            x=data.Date,
            y=data["Total number of farms"],
            mode="lines",
            fill="tozeroy",
            name="Cumulative number of farm registrations",
        )
    )

    fig.update_xaxes(tickangle=-45)
    fig.update_yaxes(rangemode="tozero")
    fig.update_layout(height=500)
    # Add annotation if not enough data
    if len(data.index) < 2:
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            text="Not enough data to plot",
            showarrow=False,
            font=dict(size=28),
            bgcolor="rgba(255, 255, 255, 0.5)",
            bordercolor="rgba(255, 255, 255, 0.5)",
            borderwidth=1500,
        )
    return fig
