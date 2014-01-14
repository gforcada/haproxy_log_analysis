# -*- encoding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from haproxy.haproxy_logfile import HaproxyLogFile
from haproxy import filters

import argparse
import os
import re


VALID_FILTERS = [f[7:] for f in dir(filters) if f.startswith('filter_')]


def create_parser():
    desc = 'Analyze HAProxy log files and outputs statistics about it'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument(
        '-l',
        '--log',
        help='Haproxy log file to analyze',
    )

    parser.add_argument(
        '-s',
        '--start',
        help='Process log entries starting at this time, in HAProxy date '
             'format (e.g. 11/Dec/2013 or 11/Dec/2013:19:31:41). '
             'At least provide the day/month/year. Values not specified will '
             'use their base value (e.g. 00 for hour). Use in conjunction '
             'with -d to limit the number of entries to process.'
    )

    parser.add_argument(
        '-d',
        '--delta',
        help='Limit the number of entries to process. Express the time delta '
             'as a number and a time unit, e.g.: 1s, 10m, 3h or 4d (for 1 '
             'second, 10 minutes, 3 hours or 4 days). Use in conjunction with '
             '-s to only analyze certain time delta. If no start time is '
             'given, the time on the first line will be used instead.'
    )

    parser.add_argument(
        '-c',
        '--command',
        help='List of commands, comma separated, to run on the log file. See'
             '-l to get a full list of them.',
    )

    parser.add_argument(
        '--list-commands',
        action='store_true',
        help='Lists all commands available.',
    )

    parser.add_argument(
        '--list-filters',
        action='store_true',
        help='Lists all filters available.',
    )

    return parser


def parse_arguments(args):
    data = {
        'start': None,
        'delta': None,
        'commands': None,
        'log': None,
        'list_commands': None,
        'list_filters': None,
    }

    if args.list_commands:
        data['list_commands'] = True
        # no need to further process any other input parameter
        return data

    if args.list_filters:
        data['list_filters'] = True
        # no need to further process any other input parameter
        return data

    if args.start is not None:
        data['start'] = _parse_arg_date(args.start)

    if args.delta is not None:
        data['delta'] = _parse_arg_delta(args.delta)

    if args.command is not None:
        data['commands'] = _parse_arg_commands(args.command)

    if args.log is not None:
        _parse_arg_logfile(args.log)
        data['log'] = args.log

    return data


def _parse_arg_date(start):
    start_regex = re.compile(
        r'(?P<day>\d+)/(?P<month>\w+)/(?P<year>\d+)'
        r'(:(?P<hour>\d+)|)(:(?P<minute>\d+)|)(:(?P<second>\d+)|)'
    )
    matches = start_regex.match(start)
    if not matches:
        raise ValueError('--start argument is not valid')

    raw_date_input = '{0}/{1}/{2}'.format(
        matches.group('day'),
        matches.group('month'),
        matches.group('year')
    )
    date_format = '%d/%b/%Y'
    if matches.group('hour'):
        date_format += ':%H'
        raw_date_input += ':{0}'.format(matches.group('hour'))
    if matches.group('minute'):
        date_format += ':%M'
        raw_date_input += ':{0}'.format(matches.group('minute'))
    if matches.group('second'):
        date_format += ':%S'
        raw_date_input += ':{0}'.format(matches.group('second'))

    return datetime.strptime(raw_date_input, date_format)


def _parse_arg_delta(delta):
    delta_regex = re.compile(r'\A(?P<value>\d+)(?P<time_unit>[smhd])\Z')
    matches = delta_regex.match(delta)
    if not matches:
        raise ValueError('--delta argument is not valid')

    value = int(matches.group('value'))
    time_unit = matches.group('time_unit')

    if time_unit == 's':
        return timedelta(seconds=value)
    elif time_unit == 'm':
        return timedelta(minutes=value)
    elif time_unit == 'h':
        return timedelta(hours=value)
    if time_unit == 'd':
        return timedelta(days=value)


def _parse_arg_commands(commands):
    input_commands = commands.split(',')
    available_commands = HaproxyLogFile.commands()
    for cmd in input_commands:
        if cmd not in available_commands:
            msg = 'command "{0}" is not available. Use -l to get a list of ' \
                  'all available commands.'
            raise ValueError(msg.format(cmd))
    return input_commands


def _parse_arg_logfile(filename):
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.exists(filepath):
        raise ValueError('filename {0} does not exist'.format(filepath))


def print_commands():
    """Prints all commands available from HaproxyLogFile with their
    description.
    """
    dummy_log_file = HaproxyLogFile()
    commands = HaproxyLogFile.commands()
    commands.sort()

    for cmd in commands:
        description = eval('dummy_log_file.cmd_{0}.__doc__'.format(cmd))
        if description:
            description = re.sub(r'\n\s+', ' ', description)
            description = description.strip()

        print('{0}: {1}\n'.format(cmd, description))


def print_filters():
    """Prints all filters available with their description."""
    for filter_name in VALID_FILTERS:
        description = eval('filters.filter_{0}.__doc__'.format(filter_name))
        if description:
            description = re.sub(r'\n\s+', ' ', description)
            description.strip()

        print('{0}: {1}\n'.format(filter_name, description))


def show_help(data):
    # make sure that if no arguments are passed the help is shown
    show = True
    for key in data:
        if data[key] is not None and key != 'filename':
            show = False
            break

    if show:
        parser = create_parser()
        parser.print_help()
        return True
    return False


def main(args):
    if show_help(args):
        return

    # show the command list
    if args['list_commands']:
        print_commands()
        # no need to process further
        return

    # show the filter list
    if args['list_filters']:
        print_filters()
        # no need to process further
        return

    log_file = HaproxyLogFile(
        logfile=args['log'],
        start=args['start'],
        delta=args['delta'],
    )
    log_file.parse_file()
    command_string = 'log_file.cmd_{0}()'
    for command in args['commands']:
        string = 'command: {0}'.format(command)
        print(string)
        print('=' * len(string))

        result = eval(command_string.format(command))
        print(result)

    return log_file  # return the log_file object so that tests can inspect it


def console_script():
    parser = create_parser()
    arguments = parse_arguments(parser.parse_args())
    main(arguments)
