import shiny
from shinywidgets import output_widget
from litefarm import ALL_ORGANIZATIONS, spg_available_years
from custom_server import VARIABLES, build_menu_from_farm_variable_list

spg = shiny.ui.nav(
    "SPG reports",
    shiny.ui.layout_sidebar(
        shiny.ui.panel_sidebar(
            shiny.ui.h3("Filters"),
            shiny.ui.h4("Year"),
            shiny.ui.help_text(
                "Only selects farms that were member of the SPG on the selected year"
            ),
            shiny.ui.input_select(
                "spg_year", "", [int(y) for y in spg_available_years()]
            ),
            shiny.ui.h4("Organization"),
            shiny.ui.help_text("Select an organization to filter the data"),
            shiny.ui.input_select(
                "org_name",
                "",
                [
                    "---------",
                ]
                + ALL_ORGANIZATIONS,
            ),
            shiny.ui.h4("Variables"),
            shiny.ui.help_text(
                "Select the variables to display in the table and the plots"
            ),
            shiny.ui.input_selectize(
                "spg_variables",
                "",
                build_menu_from_farm_variable_list(VARIABLES),
                multiple=True,
            ),
            width=3,
        ),
        shiny.ui.panel_main(
            shiny.ui.div(
                shiny.ui.h1("LiteFarm data from SPG farms"),
                shiny.ui.p(
                    """The SPG farms are the farms that are part of the Participatory Guarantee System (Sistema Participativo de Garantía) in the LiteFarm database. We are working with 7 different
                    organizations in Brazil, Mexico, Argentina, Ecuador, El Salvador and Paraguay who work in certifying organic farms. The data from SPG farms
                     was collected and analyzed in the reports available """,
                    shiny.ui.a(
                        "here",
                        href="http://localhost:3838/static/spg_reports/",
                        target="_blank",
                    ),
                ),
                shiny.ui.p(
                    """
                    For more specific visualizations, you can use the filters and select variables on the left panel.
                    """
                ),
                shiny.ui.p(
                    shiny.ui.help_text(
                        "This table represents the current data in the LiteFarm database for each organization"
                    ),
                ),
                shiny.ui.help_text(
                    "All variables other than the farm count are averages."
                ),
                shiny.ui.output_ui("spg_overview_table"),
                shiny.ui.h4("Farm variables distribution", class_="mt-4"),
                shiny.ui.help_text(
                    "Detail of the distribution of the selected variables"
                ),
                output_widget("spg_farm_variables_hist"),
                class_="custom-scroll-main",
            )
        ),
    ),
)
