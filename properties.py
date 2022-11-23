from jproperties import Properties

configs = Properties()


def get_properties():
    with open('samples/text_composer.conf', 'rb') as config_file:
        configs.load(config_file)
    return configs
