import shiny
from datetime import date
from shinywidgets import output_widget
from litefarm import ALL_COUNTRIES
from custom_server import build_menu_from_farm_variable_list, VARIABLES

overview = shiny.ui.nav(
    "Overview",
    shiny.ui.layout_sidebar(
        shiny.ui.panel_sidebar(
            shiny.ui.h3("Filters"),
            shiny.ui.h4("Country"),
            shiny.ui.help_text("Select countries to filter the data"),
            shiny.ui.input_selectize(
                "overview_countries",
                "",
                choices=ALL_COUNTRIES,
                multiple=True,
            ),
            shiny.ui.h4("Variables"),
            shiny.ui.help_text(
                "Select the variables to display in the table and the plots"
            ),
            shiny.ui.input_selectize(
                "overview_variables",
                "",
                build_menu_from_farm_variable_list(VARIABLES),
                multiple=True,
            ),
            shiny.ui.h4("Year"),
            shiny.ui.help_text("Only selects farms created on or after this year"),
            shiny.ui.input_selectize(
                "overview_year",
                "",
                choices={
                    str(year): year for year in range(2021, date.today().year + 1)
                },
                multiple=False,
                selected=None,
            ),
            width=3,
        ),
        shiny.ui.panel_main(
            shiny.ui.div(
                shiny.ui.h1("LiteFarm data by country"),
                shiny.ui.help_text(
                    "This table represents the current data in the LiteFarm database for each country"
                ),
                shiny.ui.p(
                    shiny.ui.help_text(
                        "All variables other than the farm count are averages."
                    )
                ),
                shiny.ui.output_ui("countries_overview_table"),
                # shiny.ui.h4("User evolution"),
                # shiny.ui.help_text("Evolution of the number of farms"),
                # output_widget("country_farm_evolution"),
                shiny.ui.h4("Farm variables distribution"),
                shiny.ui.help_text(
                    "Detail of the distribution of the selected variables"
                ),
                output_widget("country_farm_variables_hist"),
                class_="custom-scroll-main",
            )
        ),
    ),
)
