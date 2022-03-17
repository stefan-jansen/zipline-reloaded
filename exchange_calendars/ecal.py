from __future__ import print_function

import sys

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def error(msg):
    print(msg, file=sys.stderr)
    exit(-1)


def _render_month(calendar, year, month, print_year):
    import pandas as pd

    if sys.version_info[0] == 2:
        import StringIO

        out = StringIO.StringIO()
    else:
        import io

        out = io.StringIO()

    start = "{year}-{month}".format(year=year, month=month)
    if month == 12:
        end = "{year}-{month}".format(year=year + 1, month=1)
    else:
        end = "{year}-{month}".format(year=year, month=month + 1)

    days = pd.date_range(start, end, closed="left", tz="UTC")

    title = months[month - 1]
    if print_year:
        title += " {year}".format(year=year)

    print("{title:^28}".format(title=title).rstrip(), file=out)
    print(" Su  Mo  Tu  We  Th  Fr  Sa", file=out)
    print(
        " " * (4 * ((days[0].weekday() + 1) % 7)),
        end="",
        file=out,
    )

    for d in days:
        if d.weekday() == 6:
            print("", file=out)

        if calendar.is_session(d):
            a = b = " "
        else:
            a = "["
            b = "]"

        print(
            "{a}{d.day:>2}{b}".format(a=a, d=d, b=b),
            end="",
            file=out,
        )

    print("", file=out)
    return out.getvalue()


def _concat_lines(strings, width):
    as_lines = [string.splitlines() for string in strings]
    max_lines = max(len(lines) for lines in as_lines)
    for lines in as_lines:
        missing_lines = max_lines - len(lines)
        if missing_lines:
            lines.extend([" " * width] * missing_lines)

    rows = []
    for row_parts in zip(*as_lines):
        row_parts = list(row_parts)
        for n, row_part in enumerate(row_parts):
            missing_space = width - len(row_part)
            if missing_space:
                row_parts[n] = row_part + " " * missing_space

        rows.append("   ".join(row_parts))

    return "\n".join(row.rstrip() for row in rows)


def _int_arg(v, name):
    try:
        return int(v)
    except ValueError:
        error("%s must be an integer, got: %r" % (name, v))


def parse_args(argv):
    usage = "usage: %s CALENDAR [[[DAY] MONTH] YEAR]" % argv[0]

    if len(argv) == 1 or "--help" in argv or "-h" in argv:
        error(usage)

    if len(argv) > 1:
        from exchange_calendars import get_calendar

        try:
            calendar = get_calendar(argv[1])
        except Exception as e:
            error(str(e))

    if len(argv) == 2:
        import datetime

        now = datetime.datetime.now()
        year = now.year
        month = now.month
    elif len(argv) == 3:
        year = _int_arg(argv[2], "YEAR")
        month = None
    elif len(argv) == 4:
        month = _int_arg(argv[2], "MONTH")
        year = _int_arg(argv[3], "YEAR")
    else:
        error(usage)

    return calendar, year, month


def main(argv=None):
    """Print a unix-cal like calendar but indicate which days are trading
    sessions.
    """
    if argv is None:
        argv = sys.argv
    calendar, year, month = parse_args(argv)

    if month is not None:
        print(_render_month(calendar, year, month, print_year=True))
    else:
        month_strings = [
            [
                _render_month(
                    calendar,
                    year,
                    row * 3 + column + 1,
                    print_year=False,
                )
                for column in range(3)
            ]
            for row in range(4)
        ]
        print("{year:^88}\n".format(year=year).rstrip())
        print("\n\n".join(_concat_lines(cs, 28) for cs in month_strings))


if __name__ == "__main__":
    main()
