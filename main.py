import json

from jinja2 import Environment, PackageLoader, select_autoescape
from jsonpath_ng import parse, ext

import jinja_utils
import properties

import utils
import input_utils

configs = properties.get_properties()


def get_series_attribute(series_id, series, attribute):
    jp_expr = ext.parse(f"$.series[?(@.id=={series_id})].{attribute}")
    attr = jp_expr.find(series)
    return attr[0].value


def get_blocks_values(blocks, attribute):
    jsonpath_get_ints = parse(f"$.blocks[*].{attribute}")
    return [match.value for match in jsonpath_get_ints.find(blocks)]


def main():
    env = Environment(loader=PackageLoader("main"),
                      autoescape=select_autoescape())
    jinja_utils.setup(env)

    file_series = open(configs.get("PATH_SERIES").data)
    series = json.load(file_series)

    series_id = input_utils.get_relevant_series_id(series)
    series_vars = get_series_attribute(series_id, series, "variables")
    series_blocks_path = get_series_attribute(series_id, series, "source_file")

    file_blocks = open(series_blocks_path)
    blocks_json = json.load(file_blocks)

    int_variables = utils.flatten(get_blocks_values(blocks_json, "integer_vars"))
    date_variables = utils.flatten(get_blocks_values(blocks_json, "date_vars"))

    template = env.get_template(configs.get("TEMPLATE").data)
    template_vars = input_utils.get_template_vars(env, series_vars, int_variables, date_variables)

    content = template.render(template_vars)

    with open(configs.get("FILENAME_OUTPUT").data, mode="w", encoding="utf-8") as message:
        message.write(content)


if __name__ == '__main__':
    main()
