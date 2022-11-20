import properties
import datetime

configs = properties.get_properties()


def change_days(date, num_days):
    return date + datetime.timedelta(days=num_days)


def datetimeformat(value, date_format=configs.get("DATE_FORMAT_MACHINE_READABLE").data):
    return value.strftime(date_format)


def setup(env):
    env.filters['change_days'] = change_days
    env.filters['datetimeformat'] = datetimeformat
