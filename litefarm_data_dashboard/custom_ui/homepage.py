from shiny import ui

homepage = ui.nav(
    "Home",
    ui.page_fluid(
        ui.row(
            ui.div(
                ui.div(
                    ui.div(
                        ui.div(
                            ui.h1(
                                "Welcome to the LiteFarm Data App!", class_="text-sc"
                            ),
                            ui.p(
                                "LiteFarm Data App is a web application that provides a user-friendly interface to visualize and study data from ",
                                ui.a(
                                    "LiteFarm",
                                    href="https://litefarm.org",
                                    target="_blank",
                                ),
                                ".",
                                class_="lead",
                            ),
                            class_="homepage-lead-text-block",
                        ),
                        class_="homepage-head",
                    ),
                    ui.div(
                        ui.div(
                            ui.h2("What is LiteFarm?", class_="text-sc"),
                            ui.p(
                                """LiteFarm is a free and open source farm management tool built for current and aspiring sustainable farms. It was built by farmers and researchers coordinated by the
                            University of British Columbia to address many challenges in farm management.""",
                                class_="lead",
                            ),
                            class_="homepage-lead-text-block",
                        ),
                        class_="homepage-head",
                    ),
                    ui.div(
                        ui.div(
                            ui.h2("What is the app for?", class_="text-sc"),
                            ui.p(
                                """
                                Our application aims at helping LiteFarm users to get access and visualize the data available in the LiteFarm database, while respecting the core principles of our
                                """,
                                ui.a(
                                    "data sovereignty",
                                    href="https://www.litefarm.org/data-policy",
                                    target="_blank",
                                ),
                                ".",
                                class_="lead",
                            ),
                            ui.p(
                                "To enquire for access to the raw data, please contact our research team (",
                                ui.a(
                                    "Hannah Wittman",
                                    href="mailto:hannah.wittman@ubc.ca",
                                ),
                                " and ",
                                ui.a("Khanh Dao Duc", href="mailto:kdd@math.ubc.ca"),
                                ").",
                                class_="lead",
                            ),
                            class_="homepage-lead-text-block",
                        ),
                        class_="homepage-head",
                    ),
                    ui.div(
                        # ui.a("Pick a data subset", class_="btn btn-primary", href="#"),
                        # ui.a("Action", class_="btn btn-primary", href="#"),
                        class_="homepage-head homepage-actions",
                    ),
                    # ui.hr(),
                    # ui.div(
                    #     ui.div(
                    #         ui.h2("Some key figures about our database:"),
                    #         class_="indicators-title",
                    #     ),
                    #     ui.row(
                    #         ui.column(
                    #             4,
                    #             ui.div(
                    #                 ui.div(
                    #                     "Number of farms", class_="indicator-box-title"
                    #                 ),
                    #                 ui.div(
                    #                     ui.output_text("number_of_farm"),
                    #                     class_="indicator-text",
                    #                 ),
                    #                 class_="indicators-boxes-row",
                    #             ),
                    #         ),
                    #         ui.column(
                    #             4,
                    #             ui.div(
                    #                 ui.div(
                    #                     "Number of countries",
                    #                     class_="indicator-box-title",
                    #                 ),
                    #                 ui.div(
                    #                     ui.output_text("number_of_countries"),
                    #                     class_="indicator-text",
                    #                 ),
                    #                 class_="indicators-boxes-row",
                    #             ),
                    #         ),
                    #         class_="indicator-boxes",
                    #     ),
                    #     class_="indicator-section",
                    # ),
                    ui.div(
                        ui.hr(),
                        ui.div(
                            ui.div(
                                ui.h2("Acknowledgements"),
                                ui.div(
                                    ui.div(
                                        ui.img(
                                            src="/static/img/shiny.png",
                                            alt="Shiny",
                                            height=50,
                                        ),
                                        ui.p("Built with Shiny"),
                                        class_="ackn-elt",
                                    ),
                                    ui.div(
                                        ui.img(
                                            src="/static/img/ubc.png",
                                            alt="UBC",
                                            height=50,
                                        ),
                                        ui.p(
                                            "Developed by ",
                                            ui.a(
                                                "Khanh Dao Duc",
                                                href="https://kdaoduc.com/",
                                                target="_blank",
                                            ),
                                            " and ",
                                            ui.a(
                                                "Hannah Wittman",
                                                href="https://www.landfood.ubc.ca/hannah-wittman/",
                                                target="_blank",
                                            ),
                                            "'s research groups at the University of British Columbia.",
                                        ),
                                        class_="ackn-elt",
                                    ),
                                    class_="homepage-acknowledgements",
                                ),
                            ),
                            class_="homepage-head homepage-acknowledgements",
                        ),
                        class_="bottom",
                    ),
                    class_="homepage-content homepage-background cover light",
                ),
            )
        ),
    ),
)
