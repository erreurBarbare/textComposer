import properties
import datetime

from jinja2 import meta

configs = properties.get_properties()


def change_days(date, num_days):
    return date + datetime.timedelta(days=num_days)


def datetimeformat(value, date_format=configs.get("DATE_FORMAT_MACHINE_READABLE").data):
    return value.strftime(date_format)


def setup(env):
    env.filters['change_days'] = change_days
    env.filters['datetimeformat'] = datetimeformat


def get_undeclared_vars(env):
    template_source = env.loader.get_source(env, configs.get("TEMPLATE").data)
    parsed_content = env.parse(template_source[0])
    return meta.find_undeclared_variables(parsed_content)