import datetime
import json

from jinja2 import Environment, PackageLoader, select_autoescape, meta
from jsonpath_ng import parse, ext

# TODO: Create config file
TEMPLATE = "test-template.txt.j2"
FILENAME_OUTPUT = "test_output.txt"
PATH_SERIES = "examples/series.json"
DATE_FORMAT_HUMAN_READABLE = "DD.MM.YYYY"
DATE_FORMAT_MACHINE_READABLE = "%d.%m.%Y"


def change_days(date, num_days):
    return date + datetime.timedelta(days=num_days)


def datetimeformat(value, date_format=DATE_FORMAT_MACHINE_READABLE):
    return value.strftime(date_format)


def get_relevant_series():
    file_series = open(PATH_SERIES)
    series = json.load(file_series)
    jsonpath_get_ids = parse('$.series[*].id')
    ids = [match.value for match in jsonpath_get_ids.find(series)]

    print("The following series are available:")
    for i in ids:
        print("-", i)
    print()
    # TODO: User can select desired series via number or name (bash dialog)
    # TODO: Add error handling
    relevant_id = input("-> Please enter desired series name: ")

    jp_expr = ext.parse(f"$.series[?(@.id=={relevant_id})].variables")
    return jp_expr.find(series)


def setup(env):
    env.filters['change_days'] = change_days
    env.filters['datetimeformat'] = datetimeformat


def get_template_vars(env, series_params):
    template_source = env.loader.get_source(env, TEMPLATE)
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
                print("If you do not want to set the variable, just hit Enter")
                print_info = False
            value = input(f"{v}: ")
            template_vars_dict.update({v: value})

    return template_vars_dict


def main():
    env = Environment(loader=PackageLoader("main"),
                      autoescape=select_autoescape())
    setup(env)

    template = env.get_template(TEMPLATE)

    relevant_series = get_relevant_series()
    series_vars = relevant_series[0].value

    template_vars = get_template_vars(env, series_vars)
    # TODO Parse int and dates correctly
    workshop_date = datetime.datetime(2022, 12, 3)
    template_vars.update({"date": workshop_date})

    content = template.render(template_vars)

    with open(FILENAME_OUTPUT, mode="w", encoding="utf-8") as message:
        message.write(content)


if __name__ == '__main__':
    main()
