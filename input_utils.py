import datetime

from jsonpath_ng import parse

import jinja_utils
import composer_utils as cu

configs = cu.get_config()


def get_relevant_series_id(series_json):
    jsonpath_get_ids = parse('$.series[*].id')
    ids = [match.value for match in jsonpath_get_ids.find(series_json)]

    print("The following series are available:")
    for i in ids:
        print("-", i)
    print()
    input_message = "-> Please enter desired series name: "
    while True:
        user_input = input(input_message)
        if user_input in ids:
            return user_input
        else:
            input_message = "Invalid input. Please enter a existing series name: "


def get_template_vars(env, series_params, ints, dates, enums):
    template_vars = jinja_utils.get_undeclared_vars(env)
    template_vars_dict = {}

    print_info = True
    for v in template_vars:
        if series_params.get(v) is not None:
            template_vars_dict.update({v: series_params.get(v)})
        else:
            if print_info:
                print("Please enter the desired values for the following variable(s) used in the text.")
                print(f"For dates, use the format {configs['Date']['DateFormatHumanReadable']}")
                print("If you do NOT want to set the variable, just hit Enter")
                print_info = False
            value = input(f"{v}: ")
            valid_value = check_data_type(v, value, ints, dates, enums)
            template_vars_dict.update({v: valid_value})

    return template_vars_dict


def check_data_type(variable, value, ints, dates, enums):
    if value is None or value == '':
        return None

    enum_names = []
    for e in enums:
        enum_names.append(e["name"])

    while True:
        if variable in ints:
            try:
                return int(value)
            except ValueError:
                value = input(f"please enter a valid value for {variable} (Integer): ")
        elif variable in dates:
            try:
                return datetime.datetime.strptime(value, configs['Date']['DateFormatMachineReadable'])
            except ValueError:
                value = input(f"please enter a valid value for {variable} "
                              f"(datetime having the format {configs['Date']['DateFormatHumanReadable']}): ")
        elif variable in enum_names:
            relevant_entry = None
            for entry in enums:
                if entry["name"] == variable:
                    relevant_entry = entry
            if value in relevant_entry["values"]:
                return value
            else:
                value = input(f"please enter a valid value for {variable} "
                              f"(allowed values: {relevant_entry['values']}): ")
        # treat all other variables as strings
        else:
            return value
