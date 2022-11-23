import json

from jinja2 import Environment, PackageLoader, select_autoescape
from jsonpath_ng import parse, ext

import jinja_utils
import properties

import utils
import input_utils

configs = properties.get_properties()
SERIES = "series"
BLOCKS = "blocks"


def get_attribute_of_single_object(object_name, object_id, json_object, attribute):
    jp_expr = ext.parse(f"$..{object_name}[?(@.id=={object_id})].{attribute}")
    attr = jp_expr.find(json_object)
    return attr[0].value


def get_attribute_of_all_objects(object_name, json_object, attribute):
    jsonpath_get_ints = parse(f"$..{object_name}[*].{attribute}")
    return [match.value for match in jsonpath_get_ints.find(json_object)]


def generate_template(relevant_blocks, blocks_json, template_path):
    with open(template_path, mode="w", encoding="utf-8") as new_template:
        for b in relevant_blocks:
            new_template.write(get_attribute_of_single_object(BLOCKS, b, blocks_json, "value") + "\n")


def main():
    env = Environment(loader=PackageLoader("main"),
                      autoescape=select_autoescape())
    jinja_utils.setup(env)

    file_series = open(configs.get("PATH_SERIES").data)
    series_json = json.load(file_series)

    series_id = input_utils.get_relevant_series_id(series_json)
    series_vars = get_attribute_of_single_object(SERIES, series_id, series_json, "variables")
    blocks_path = get_attribute_of_single_object(SERIES, series_id, series_json, "source_file")
    series_relevant_blocks = get_attribute_of_single_object(SERIES, series_id, series_json, "blocks")

    file_blocks = open(blocks_path)
    blocks_json = json.load(file_blocks)

    generate_template(series_relevant_blocks, blocks_json,
                      configs.get("TEMPLATE_FOLDER").data + configs.get("TEMPLATE").data)
    template = env.get_template(configs.get("TEMPLATE").data)

    int_vars = utils.flatten(get_attribute_of_all_objects(BLOCKS, blocks_json, "integer_vars"))
    date_vars = utils.flatten(get_attribute_of_all_objects(BLOCKS, blocks_json, "date_vars"))
    enum_vars = utils.flatten(get_attribute_of_all_objects(BLOCKS, blocks_json, "enum_vars"))
    template_vars = input_utils.get_template_vars(env, series_vars, int_vars, date_vars, enum_vars)

    content = template.render(template_vars)

    with open(configs.get("FOLDER_OUTPUT").data + configs.get("FILENAME_OUTPUT").data, mode="w", encoding="utf-8") as message:
        message.write(content)


if __name__ == '__main__':
    main()
