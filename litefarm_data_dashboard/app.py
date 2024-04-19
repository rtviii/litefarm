from shiny import App, render, ui
from custom_ui import tabs
from custom_server import (
    country_overview,
    new_farms_evolution,
    overview_hist,
    organizations_overview,
    spg_hist,
)
from shinywidgets import render_widget
from custom_server import export
import sys

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet", type="text/css", href="/static/css/litefarm.css"
        ),
        ui.tags.script(src="/static/js/litefarm.js", type="text/javascript"),
    ),
    ui.page_navbar(
        tabs.homepage,
        tabs.overview,
        tabs.spg,
        title=ui.div(
            ui.img(src="/static/img/litefarm-logo.png", class_="logo", height=25),
            "LITEFARM Dashboard",
            class_="title",
        ),
    ),
)


def server(input, output, session):
    # @output
    # @render.text
    # def number_of_farm():
    #     return farm_count()

    # @output
    # @render.text
    # def number_of_countries():
    #     return countries_count()

    @output
    @render.ui
    def countries_overview_table():
        return ui.HTML(
            country_overview(
                year=input.overview_year(),
                countries=input.overview_countries(),
                variable_names=input.overview_variables(),
            )
        )

    @output
    @render_widget
    def country_farm_variables_hist():
        return overview_hist(
            year=input.overview_year(),
            countries=input.overview_countries(),
            variable_names=input.overview_variables(),
        )

    @output
    @render.ui
    def spg_overview_table():
        return ui.HTML(
            organizations_overview(
                input.spg_year(), input.spg_variables(), input.org_name()
            )
        )

    @output
    @render_widget
    def spg_farm_variables_hist():
        return spg_hist(input.spg_year(), input.org_name(), input.spg_variables())


app = App(
    app_ui,
    server,
)
