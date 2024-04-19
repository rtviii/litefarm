from .spg import filter_spg_farms
from .farm_variables import find_variable_in_variable_list
from .farms import VARIABLES
import io


def spg(year, organization_name, variable_names):
    farms_df = filter_spg_farms(year, organization_name)
    variables = []
    for variable_name in variable_names:
        variable = find_variable_in_variable_list(VARIABLES, variable_name)
        variables.append(variable)
        farms_df = variable.function(farms_df)
    with io.StringIO() as buffer:
        farms_df[
            ["farm_id", "organization"] + [variable.name for variable in variables]
        ].to_csv(buffer, index=False)
        yield buffer.getvalue()
