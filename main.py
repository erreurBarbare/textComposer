import datetime
import json

from jinja2 import Environment, PackageLoader, select_autoescape
from jsonpath_ng import parse, ext

# TODO: Create config file
FILENAME_OUTPUT = "test_output.txt"
PATH_SERIES = "examples/series.json"


def change_days(date, num_days):
    return date + datetime.timedelta(days=num_days)


def datetimeformat(value, date_format='%d.%m.%Y'):
    return value.strftime(date_format)


def get_relevant_series(json_series):
    jsonpath_get_ids = parse('$.series[*].id')
    ids = [match.value for match in jsonpath_get_ids.find(json_series)]

    print("The following series are available:")
    for i in ids:
        print("-", i)
    print()
    # TODO: User selects desired series -> via number or name (bash dialog)
    # TODO: Add error handling
    relevant_id = input("-> Please enter desired series name: ")

    jp_expr = ext.parse(f"$.series[?(@.id=={relevant_id})].variables")
    return jp_expr.find(json_series)


def main():
    env = Environment(loader=PackageLoader("main"),
                      autoescape=select_autoescape())
    env.filters['change_days'] = change_days
    env.filters['datetimeformat'] = datetimeformat
    template = env.get_template("test-template.txt.j2")

    file_series = open(PATH_SERIES)
    series = json.load(file_series)

    relevant_series = get_relevant_series(series)
    params = relevant_series[0].value

    workshop_date = datetime.datetime(2022, 12, 3)

    content = template.render(
        firstname="Valentina",
        os="win",
        date=workshop_date,
        workshop=params.get("workshop"),
        time=params.get("time"),
        price=params.get("price") or "Free entry, collection"
    )

    with open(FILENAME_OUTPUT, mode="w", encoding="utf-8") as message:
        message.write(content)


if __name__ == '__main__':
    main()
