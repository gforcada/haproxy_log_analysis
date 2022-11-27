import re
from datetime import datetime, timedelta

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


def validate_arg_date(start):
    """Check that date argument is valid."""
    try:
        date_str_to_datetime(start)
    except (AttributeError, ValueError):
        raise ValueError('--start argument is not valid')


def validate_arg_delta(delta):
    """Check that the delta argument is valid."""
    try:
        delta_str_to_timedelta(delta)
    except (AttributeError, ValueError):
        raise ValueError('--delta argument is not valid')


def list_filters():
    """Return the information of existing filters.

    Data returned:
    - their names as the user is expected to use them from the command line
    - the object itself
    - its description
    """
    from haproxy import filters

    data = {}
    for full_name in dir(filters):
        if not full_name.startswith('filter_'):
            continue
        name = full_name[7:]
        obj = getattr(filters, full_name)

        description = obj.__doc__
        if description:
            description = re.sub(r'\n\s+', ' ', description)
            description.strip()

        data[name] = {'obj': obj, 'description': f'{name}: {description}\n'}
    return data


def list_commands():
    """Return the information of existing commands.

    Data returned:
    - their names as the user is expected to use them from the command line
    - the object itself
    - its description
    """
    from haproxy import commands

    data = {}
    for cmd in dir(commands):
        if cmd.endswith('Mixin'):
            continue
        klass = getattr(commands, cmd)
        try:
            name = klass.command_line_name()
        except AttributeError:
            continue

        description = klass.__doc__
        if description:
            description = re.sub(r'\n\s+', ' ', description)
            description.strip()

        data[name] = {'klass': klass, 'description': f'{name}: {description}\n'}
    return data


VALID_COMMANDS = list_commands()
VALID_FILTERS = list_filters()
