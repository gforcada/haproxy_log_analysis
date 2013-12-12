# -*- encoding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from haproxy.haproxy_logfile import HaproxyLogFile

import argparse
import os
import re


def create_parser():
    desc = 'Analyze Haproxy log files and outputs statistics about it'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('filename', help='Haproxy log file to analyze')
    parser.add_argument(
        '-s',
        '--start',
        help='Process log entries starting at this time, in haproxy date '
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
        help='List of commands, comma separated, to run on the log file. '
             'Commands available: '
             'counter (count how many entries are on the log file)',
        required=True,
    )

    return parser


def parse_arguments(args):
    start = getattr(args, 'start', None)
    delta = getattr(args, 'delta', None)
    commands = getattr(args, 'command', None)
    filename = getattr(args, 'filename', None)

    if start is not None:
        start = _parse_arg_date(start)

    if delta is not None:
        delta = _parse_arg_delta(delta)

    if commands is not None:
        commands = _parse_arg_commands(commands)

    if filename is not None:
        _parse_arg_filename(filename)

    data = {
        'start': start,
        'delta': delta,
        'commands': commands,
        'filename': filename,
    }
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
            msg = 'command "{0}" is not available. List of available ' \
                  'commands: {1}'
            raise ValueError(msg.format(cmd, available_commands))
    return input_commands


def _parse_arg_filename(filename):
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.exists(filepath):
        raise ValueError('filename {0} does not exist'.format(filepath))


if __name__ == '__main__':
    parser = create_parser()
    arguments = parse_arguments(parser.parse_args())
    log_file = HaproxyLogFile(arguments)
