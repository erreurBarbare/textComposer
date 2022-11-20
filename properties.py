from jproperties import Properties

configs = Properties()


def get_properties():
    with open('text_composer.properties', 'rb') as config_file:
        configs.load(config_file)
    return configs
