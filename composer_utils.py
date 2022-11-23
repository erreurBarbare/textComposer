from jsonpath_ng import parse, ext
import json
import configparser

BLOCKS = "blocks"
SAMPLE_CONFIG_PATH = "samples/composer.ini"
config_path = ""
config_info_printed = False


def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def get_attribute_of_single_object(object_name, object_id, json_object, attribute):
    jp_expr = ext.parse(f"$..{object_name}[?(@.id=={object_id})].{attribute}")
    attr = jp_expr.find(json_object)
    return attr[0].value


def get_attribute_of_all_objects(object_name, json_object, attribute):
    jsonpath_get_ints = parse(f"$..{object_name}[*].{attribute}")
    return [match.value for match in jsonpath_get_ints.find(json_object)]


def generate_template(relevant_blocks, blocks_json, template_path):
    with open(template_path, mode='w', encoding='utf-8') as new_template:
        for b in relevant_blocks:
            new_template.write(get_attribute_of_single_object(BLOCKS, b, blocks_json, "value") + "\n\n")


def load_json_from_file(path):
    loaded_file = open(path, 'r', encoding='utf-8')
    loaded_json = json.load(loaded_file)
    loaded_file.close()
    return loaded_json


def get_config(path=None):
    global config_path
    parser = configparser.ConfigParser()
    if path is not None and config_path != "":
        config_path = path
    if config_path != "":
        parser.read(path)
        return parser
    else:
        global config_info_printed
        if not config_info_printed:
            print("No custom config provided. Using sample config.")
            config_info_printed = True
        parser.read(SAMPLE_CONFIG_PATH)
        return parser
