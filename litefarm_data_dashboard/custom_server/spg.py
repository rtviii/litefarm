from litefarm import get_cleaned_farms, ALL_ORGANIZATIONS, litefarm
import pandas as pd
from itables.shiny import DT
from .farms import VARIABLES
from .farm_variables import find_variable_in_variable_list
import plotly.graph_objects as go
import plotly.subplots as sp
from pathlib import Path
import sys
import uuid


def organizations_overview(
    year,
    variable_names=[
        "Average farm site area",
        "Average productive area",
        "Average crop diversity",
    ],
    selected_organization=None,
):
    variables = []
    # Get all farms from selected year
    farms_df = filter_spg_farms(year, None)

    # Init the aggregation parameters
    agg_dict = {"farm_id": "count"}
    columns_renaming = {
        "farm_id": "# farms",
    }
    # Fill the aggregation parameters for every variable and calculate it for each farm
    for variable_name in variable_names:
        variable = find_variable_in_variable_list(VARIABLES, variable_name)
        variables.append(variable)
        farms_df = variable.function(farms_df)
        agg_dict[variable.name] = "mean"
        columns_renaming[variable.name] = variable.full_name

    # Aggregate everything in a nice table
    table = (
        farms_df.groupby("organization")
        .agg(agg_dict)
        .rename(columns=columns_renaming)
        .reset_index()
    )
    # Make the row stand out if the organization is selected
    table["Organization"] = table["organization"].apply(
        lambda x: f"<span class='selected'>{x}</span>"
        if str(x) == selected_organization
        else x
    )
    # Filter the output table
    table = table[
        [
            "Organization",
        ]
        + list(columns_renaming.values())
    ]
    # Nice looking na values
    table = table.fillna("-")
    with pd.option_context("display.float_format", "{:,.2f}".format):
        return DT(table)


def filter_spg_farms(year, organization):
    all_farms = litefarm("SELECT * FROM farm")
    spg_farms = pd.read_csv(
        Path(__file__).parent.parent / "data" / "spg_organizations.csv"
    )
    spg_farms["farm_id"] = spg_farms["farm_id"].apply(uuid.UUID)
    farms = pd.merge(all_farms, spg_farms, on="farm_id", how="inner")
    farms = farms[(farms.year == int(year))]
    if organization in ALL_ORGANIZATIONS:
        farms = farms[farms.organization == organization]
    return farms


def spg_hist(year, organization, variable_names=[]):
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
    farms_df = filter_spg_farms(year, organization)
    variables = []
    for name in variable_names:
        variables.append(find_variable_in_variable_list(VARIABLES, name))
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
                name=variable.name,
            ),
            row=i // 2 + 1,
            col=i % 2 + 1,
        )
        fig.update_xaxes(
            title_text=variable.full_name,
            row=i // 2 + 1,
            col=i % 2 + 1,
        )
    fig.update_layout(height=500 * number_of_rows, bargap=0.20)
    return fig
