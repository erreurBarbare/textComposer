import datetime

from jsonpath_ng import parse

import composer_utils as cu
import jinja_utils

configs = cu.get_config()


def get_relevant_series_id(series_json):
    jsonpath_get_ids = parse('$.series[*].id')
    ids = [match.value for match in jsonpath_get_ids.find(series_json)]
    counter = 1
    series = {}

    print("The following series are available:")
    for i in ids:
        print(f"({counter}) {i}")
        series.update({str(counter): i})
        counter += 1
    print()
    input_message = "-> Please enter desired series name or number: "
    while True:
        user_input = input(input_message)
        if user_input in series.keys():
            return series.get(user_input)
        elif user_input in ids:
            return user_input
        else:
            input_message = "Invalid input. Please enter a existing series name or number: "


def get_template_vars(env, series_params, ints, dates, times, enums, optionals):
    template_vars = jinja_utils.get_undeclared_vars(env)
    template_vars_dict = {}

    print_info = True
    for v in template_vars:
        series_var = series_params.get(v)
        if series_var is not None:
            cu.check_datatype(v, series_var, ints, dates, times, enums)
            template_vars_dict.update({v: series_var})
        else:
            if print_info:
                print("Please enter the desired values for the following variable(s) used in the text.")
                print(f"For dates, use the format {configs['Date']['DateFormatHumanReadable']}")
                print(f"For time, use the format {configs['Time']['TimeFormatHumanReadable']}")
                print("If you do NOT want to set the variable, just hit Enter")
                print_info = False
            value = input(f"{v}: ")
            valid_value = check_data_type(v, value, ints, dates, times, enums, optionals)
            template_vars_dict.update({v: valid_value})

    return template_vars_dict


def check_data_type(variable, value, ints, dates, times, enums, optionals):
    enum_names = []
    for e in enums:
        enum_names.append(e["name"])

    while True:
        if value is None or value == '':
            if variable in optionals:
                return None
            else:
                value = input(f"{variable} can not be empty. Please enter a value for {variable}: ")
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
                              f"(date having the format {configs['Date']['DateFormatHumanReadable']}): ")
        elif variable in times:
            try:
                return datetime.datetime.strptime(value, configs['Time']['TimeFormatMachineReadable'])
            except ValueError:
                value = input(f"please enter a valid value for {variable} "
                              f"(time having the format {configs['Time']['TimeFormatHumanReadable']}): ")
        elif variable in enum_names:
            relevant_enum = cu.get_relevant_enum(variable, value, enums)
            if value in relevant_enum["values"]:
                return value
            else:
                value = input(f"please enter a valid value for {variable} "
                              f"(allowed values: {relevant_enum['values']}): ")
        # treat all other variables as strings
        else:
            return value


def calculate_discount(price):
    if price == 0:
        return price
    discount = input("For normal price, hit enter. For a discount, enter absolute value (20) or a percentage (10%): ")
    while True:
        try:
            if discount is None or discount == '' or int(discount) < 0:
                return price
            if 0 < int(discount) < price:
                return price - int(discount)
        except ValueError:
            if discount[-1:] == '%':
                try:
                    percentage = int(discount[0:-1])
                    if 0 < percentage <= 100:
                        return int(price * (100 - percentage)/100)
                except ValueError:
                    pass
        discount = input("please enter a valid value for discount: ")

