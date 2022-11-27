from jsonpath_ng import parse, ext
import json
import configparser
import datetime

BLOCKS = "blocks"


def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def get_attribute_of_single_object(object_name, object_id, json_object, attribute):
    jp_expr = ext.parse(f"$..{object_name}[?(@.id=={object_id})].{attribute}")
    attr = jp_expr.find(json_object)
    try:
        return attr[0].value
    except IndexError:
        print(f"ERROR: could find no attribute '{attribute}' in object '{object_name}' for id '{object_id}' \n"
              f"json: {json_object}")
        exit(1)


def get_attribute_of_all_objects(object_name, json_object, attribute):
    jsonpath_get_attr_of_all_objs = parse(f"$..{object_name}[*].{attribute}")
    return [match.value for match in jsonpath_get_attr_of_all_objs.find(json_object)]


def generate_template(relevant_blocks, blocks_json, template_path):
    with open(template_path, mode='w', encoding='utf-8') as new_template:
        for b in relevant_blocks:
            new_template.write(get_attribute_of_single_object(BLOCKS, b, blocks_json, "value") + "\n\n")


def load_json_from_file(path):
    loaded_file = open(path, 'r', encoding='utf-8')
    loaded_json = json.load(loaded_file)
    loaded_file.close()
    return loaded_json


def get_config():
    parser = configparser.ConfigParser()
    parser.read("composer.ini")
    return parser


def check_datatype(variable, value, ints, dates, times, enums):
    configs = get_config()
    enum_names = []
    for e in enums:
        enum_names.append(e["name"])

    if variable in ints:
        try:
            return int(value)
        except ValueError:
            print(f"ERROR: '{value}' is not a valid integer")
            exit(1)
    elif variable in dates:
        try:
            return datetime.datetime.strptime(value, configs['Date']['DateFormatMachineReadable'])
        except ValueError:
            print(f"ERROR: '{value}' is not a valid time (supported format: "
                  f"{configs['Date']['DateFormatHumanReadable']}")
            exit(1)
    elif variable in times:
        check_time(value, configs)
    elif variable in enum_names:
        relevant_enum = get_relevant_enum(variable, value, enums)
        if value in relevant_enum["values"]:
            return value
        else:
            print(f"ERROR: '{value}' is not a valid value"
                  f"(allowed values: {relevant_enum['values']})")
            exit(1)
    # treat all other variables as strings
    else:
        return value


def check_time(value, configs):
    if type(value) == datetime.datetime:
        return value
    try:
        return datetime.datetime.strptime(value, configs['Time']['TimeFormatMachineReadable'])
    except ValueError:
        print(f"ERROR: '{value}' is not a valid time (supported format: "
              f"{configs['Time']['TimeFormatHumanReadable']}")
        exit(1)


def get_relevant_enum(variable, value, enums):
    for enum in enums:
        if enum["name"] == variable:
            return enum
    return None

