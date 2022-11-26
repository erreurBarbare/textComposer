from jinja2 import Environment, PackageLoader, select_autoescape

import composer_utils as cu
import input_utils
import jinja_utils

SERIES = "series"
BLOCKS = "blocks"


def main():
    configs = cu.get_config()

    env = Environment(loader=PackageLoader("main"),
                      autoescape=select_autoescape())
    jinja_utils.setup(env)

    # load series
    series_json = cu.load_json_from_file(configs['Files']['PathSeries'])

    # select relevant series
    series_id = input_utils.get_relevant_series_id(series_json)
    series_vars = cu.get_attribute_of_single_object(SERIES, series_id, series_json, "variables")

    # generate template from blocks
    blocks_path = cu.get_attribute_of_single_object(SERIES, series_id, series_json, "source_file")
    series_relevant_blocks = cu.get_attribute_of_single_object(SERIES, series_id, series_json, "blocks")

    blocks_json = cu.load_json_from_file(blocks_path)

    cu.generate_template(series_relevant_blocks, blocks_json,
                         configs['Files']['TemplateFolder'] + configs['Files']['Template'])
    template = env.get_template(configs['Files']['Template'])

    # define the variables values for the final text
    int_vars = cu.flatten(cu.get_attribute_of_all_objects(BLOCKS, blocks_json, "integer_vars"))
    date_vars = cu.flatten(cu.get_attribute_of_all_objects(BLOCKS, blocks_json, "date_vars"))
    time_vars = cu.flatten(cu.get_attribute_of_all_objects(BLOCKS, blocks_json, "time_vars"))
    enum_vars = cu.flatten(cu.get_attribute_of_all_objects(BLOCKS, blocks_json, "enum_vars"))
    optional_vars = cu.flatten(cu.get_attribute_of_all_objects(BLOCKS, blocks_json, "optional_vars"))
    text_variables_values = input_utils.get_template_vars(env, series_vars, int_vars, date_vars, time_vars,
                                                          enum_vars, optional_vars)

    # generate final text
    content = template.render(text_variables_values)

    with open(configs['Files']['FolderOutput'] + configs['Files']['FilenameOutput'], mode='w',
              encoding='utf-8') as message:
        message.write(content)


if __name__ == '__main__':
    main()
