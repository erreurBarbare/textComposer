import datetime
import json

from jinja2 import Environment, PackageLoader, select_autoescape, meta
from jsonpath_ng import parse, ext

import jinja_utils
import properties

configs = properties.get_properties()


def get_relevant_series_id(series_json):
    jsonpath_get_ids = parse('$.series[*].id')
    ids = [match.value for match in jsonpath_get_ids.find(series_json)]

    print("The following series are available:")
    for i in ids:
        print("-", i)
    print()
    # TODO: User can select desired series via number or name (bash dialog)
    # TODO: Add error handling
    return input("-> Please enter desired series name: ")


def get_template_vars(env, series_params, ints, dates):
    template_source = env.loader.get_source(env, configs.get("TEMPLATE").data)
    parsed_content = env.parse(template_source[0])
    template_vars = meta.find_undeclared_variables(parsed_content)

    template_vars_dict = {}

    print_info = True
    for v in template_vars:
        if series_params.get(v) is not None:
            template_vars_dict.update({v: series_params.get(v)})
        else:
            if print_info:
                print("Please enter the desired values for the following variable(s) used in the text.")
                print(f"For dates, use the format {configs.get('DATE_FORMAT_HUMAN_READABLE').data}")
                print("If you do not want to set the variable, just hit Enter")
                print_info = False
            value = input(f"{v}: ")
            valid_value = check_data_type(v, value, ints, dates)
            template_vars_dict.update({v: valid_value})

    return template_vars_dict


def check_data_type(variable, value, ints, dates):
    if value is None or value == '':
        return None

    valid = False
    while not valid:
        if variable in ints:
            try:
                return int(value)
            except ValueError:
                value = input(f"please enter a valid value for {variable} (Integer): ")
        elif variable in dates:
            try:
                return datetime.datetime.strptime(value, configs.get("DATE_FORMAT_MACHINE_READABLE").data)
            except ValueError:
                value = input(f"please enter a valid value for {variable} "
                              f"(datetime having the format {configs.get('DATE_FORMAT_HUMAN_READABLE').data}): ")
        # TODO: add enums support
        # treat all other variables as strings
        else:
            return value


def get_series_attribute(series_id, series, attribute):
    jp_expr = ext.parse(f"$.series[?(@.id=={series_id})].{attribute}")
    attr = jp_expr.find(series)
    return attr[0].value


def get_blocks_values_flat_list(blocks, attribute):
    jsonpath_get_ints = parse(f"$.blocks[*].{attribute}")
    lists = [match.value for match in jsonpath_get_ints.find(blocks)]
    return [item for sublist in lists for item in sublist]


def main():
    env = Environment(loader=PackageLoader("main"),
                      autoescape=select_autoescape())
    jinja_utils.setup(env)

    file_series = open(configs.get("PATH_SERIES").data)
    series = json.load(file_series)

    series_id = get_relevant_series_id(series)
    series_vars = get_series_attribute(series_id, series, "variables")
    # TODO: Support multiple blocks files
    series_blocks_path = get_series_attribute(series_id, series, "source_file")

    file_blocks = open(series_blocks_path)
    blocks_json = json.load(file_blocks)

    # TODO: Handle mandatory fields (add section optional_vars in blocks.json)

    int_variables = get_blocks_values_flat_list(blocks_json, "integer_vars")
    date_variables = get_blocks_values_flat_list(blocks_json, "date_vars")

    template = env.get_template(configs.get("TEMPLATE").data)
    template_vars = get_template_vars(env, series_vars, int_variables, date_variables)

    content = template.render(template_vars)

    with open(configs.get("FILENAME_OUTPUT").data, mode="w", encoding="utf-8") as message:
        message.write(content)


if __name__ == '__main__':
    main()
