import datetime

from jinja2 import Environment, PackageLoader, select_autoescape


def change_days(date, num_days):
    return date + datetime.timedelta(days=num_days)


def datetimeformat(value, format='%d.%m.%Y'):
    return value.strftime(format)


def main():
    env = Environment(loader=PackageLoader("main"),
                      autoescape=select_autoescape())
    env.filters['change_days'] = change_days
    env.filters['datetimeformat'] = datetimeformat
    template = env.get_template("am_before_workshop.txt")

    filename = "test_output.txt"

    workshop_date = datetime.datetime(2022, 12, 3)

    content = template.render(
        firstname="Valentina",
        workshop="aare_meter",
        date=workshop_date,
        time="from 9.30am to 4.30pm",
        os="win"
    )

    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)


if __name__ == '__main__':
    main()
