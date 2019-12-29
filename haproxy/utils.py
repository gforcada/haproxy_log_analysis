from datetime import timedelta
from datetime import datetime

import re


DELTA_REGEX = re.compile(r'\A(?P<value>\d+)(?P<time_unit>[smhd])\Z')

START_REGEX = re.compile(
    r'(?P<day>\d+)/(?P<month>\w+)/(?P<year>\d+)'
    r'(:(?P<hour>\d+)|)(:(?P<minute>\d+)|)(:(?P<second>\d+)|)'
)

DELTA_KEYS = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days'}


def date_str_to_datetime(date):
    """Convert a string to a datetime object.

    The format is `day/month/year[[[:hour]:minute]:second]` being:
    - day a number
    - month a three letter representation of the month (i.e. Dec, Jan, etc)
    - year as a 4 digits value
    - hour/minute/second as 2 digits value, each of them being optional
    """
    matches = START_REGEX.match(date)
    data = matches.group('day'), matches.group('month'), matches.group('year')
    raw_date_input = f'{data[0]}/{data[1]}/{data[2]}'
    date_format = '%d/%b/%Y'
    for variable, percent in (('hour', ':%H'), ('minute', ':%M'), ('second', ':%S')):
        match = matches.group(variable)
        if match:
            date_format += percent
            raw_date_input = f'{raw_date_input}:{match}'

    return datetime.strptime(raw_date_input, date_format)


def delta_str_to_timedelta(delta):
    """Convert a string to a timedelta representation.

    Format is NUMBER followed by one of the following letters: `s`, `m`, `h`, `d`.
    Each of them meaning, second, minute, hour and day.
    """
    matches = DELTA_REGEX.match(delta)
    value = int(matches.group('value'))
    time_unit = matches.group('time_unit')
    key = DELTA_KEYS[time_unit]
    return timedelta(**{key: value})
