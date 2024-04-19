class FarmVariable:
    def __init__(self, name, function, unit="", concat=None, title=None):
        self.name = name
        self.function = function
        self.unit = unit
        self.concat = concat
        self.title = title

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        return (
            f"{self.name.lower().capitalize()} {f' ({self.unit})' if self.unit else ''}"
        )


def build_menu_from_farm_variable_list(farm_variables):
    farm_variables = sorted(farm_variables, key=lambda x: x.name)
    menu = {}
    for variable in farm_variables:
        if variable.title is None:
            variable.title = "Other"
        if variable.title not in menu:
            menu[variable.title] = {}
        menu[variable.title][variable.name] = variable.name
    return menu


def find_variable_in_variable_list(farm_variables, variable_name):
    for variable in farm_variables:
        if variable.name == variable_name:
            return variable
    return None
