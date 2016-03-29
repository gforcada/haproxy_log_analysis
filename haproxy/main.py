# -*- encoding: utf-8 -*-
from haproxy import DELTA_REGEX
from haproxy import filters
from haproxy import START_REGEX
from haproxy.logfile import Log

import argparse
import os
import re


VALID_FILTERS = [
    f[7:]
    for f in dir(filters)
    if f.startswith('filter_') and not f.endswith('time_frame')
]


def create_parser():
    desc = 'Analyze HAProxy log files and outputs statistics about it'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument(
        '-l',
        '--log',
        help='HAProxy log file to analyze',
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
        help='List of commands, comma separated, to run on the log file. See '
             '--list-commands to get a full list of them.',
    )

    parser.add_argument(
        '-f',
        '--filter',
        help='List of filters to apply on the log file. Passed as comma '
             'separated and parameters within square brackets, e.g '
             'ip[192.168.1.1],ssl,path[/some/path]. See '
             '--list-filters to get a full list of them.',
    )

    parser.add_argument(
        '-n',
        '--negate-filter',
        help='Make filters passed with -f work the other way around, i.e. if '
             'the ``ssl`` filter is passed instead of showing only ssl '
             'requests it will show non-ssl traffic. If the ``ip`` filter is '
             'used, then all but that ip passed to the filter will be used.',
        action='store_true',
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
        'filters': None,
        'negate_filter': None,
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

    if args.negate_filter:
        data['negate_filter'] = True

    if args.start is not None:
        _validate_arg_date(args.start)
        data['start'] = args.start

    if args.delta is not None:
        _validate_arg_delta(args.delta)
        data['delta'] = args.delta

    if args.command is not None:
        data['commands'] = _parse_arg_commands(args.command)

    if args.filter is not None:
        data['filters'] = _parse_arg_filters(args.filter)

    if args.log is not None:
        _validate_arg_logfile(args.log)
        data['log'] = args.log

    return data


def _validate_arg_date(start):
    matches = START_REGEX.match(start)
    if not matches:
        raise ValueError('--start argument is not valid')


def _validate_arg_delta(delta):
    matches = DELTA_REGEX.match(delta)
    if not matches:
        raise ValueError('--delta argument is not valid')


def _parse_arg_commands(commands):
    input_commands = commands.split(',')
    available_commands = Log.commands()
    for cmd in input_commands:
        if cmd not in available_commands:
            msg = 'command "{0}" is not available. Use --list-commands to ' \
                  'get a list of all available commands.'
            raise ValueError(msg.format(cmd))
    return input_commands


def _parse_arg_filters(filters_arg):
    input_filters = filters_arg.split(',')

    return_data = []
    for filter_expression in input_filters:
        filter_name = filter_expression
        filter_arg = None

        if filter_expression.endswith(']'):
            if '[' not in filter_expression:
                msg = 'Error on filter "{0}". It is missing an opening ' \
                      'square bracket.'
                raise ValueError(msg.format(filter_expression))
            filter_name, filter_arg = filter_expression.split('[')
            filter_arg = filter_arg[:-1]  # remove the closing square bracket

        if filter_name not in VALID_FILTERS:
            msg = 'filter "{0}" is not available. Use --list-filters to ' \
                  'get a list of all available filters.'
            raise ValueError(msg.format(filter_name))

        return_data.append((filter_name, filter_arg))

    return return_data


def _validate_arg_logfile(filename):
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.exists(filepath):
        raise ValueError('filename {0} does not exist'.format(filepath))


def print_commands():
    """Prints all commands available from Log with their
    description.
    """
    dummy_log_file = Log()
    commands = Log.commands()
    commands.sort()

    for cmd in commands:
        cmd = getattr(dummy_log_file, 'cmd_{0}'.format(cmd))
        description = cmd.__doc__
        if description:
            description = re.sub(r'\n\s+', ' ', description)
            description = description.strip()

        print('{0}: {1}\n'.format(cmd, description))


def print_filters():
    """Prints all filters available with their description."""
    for filter_name in VALID_FILTERS:
        filter_func = getattr(filters, 'filter_{0}'.format(filter_name))
        description = filter_func.__doc__
        if description:
            description = re.sub(r'\n\s+', ' ', description)
            description.strip()

        print('{0}: {1}\n'.format(filter_name, description))


def show_help(data):
    # make sure that if no arguments are passed the help is shown
    show = True
    for key in data:
        if data[key] is not None and key != 'log':
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

    # create a Log instance and parse the log file
    log_file = Log(
        logfile=args['log'],
    )

    # apply the time frame filter
    if args['start'] or args['delta']:
        start = args['start'] or ''
        delta = args['delta'] or ''
        filter_func = filters.filter_time_frame(start, delta)

        log_file = log_file.filter(filter_func)

    # apply all other filters given
    if args['filters']:
        for filter_data in args['filters']:
            arg = filter_data[1] or ''
            filter_func = getattr(filters, 'filter_{0}'.format(filter_data[0]))
            log_file = log_file.filter(filter_func(arg),
                                       reverse=args['negate_filter'])

    # run all commands
    for command in args['commands']:
        string = 'command: {0}'.format(command)
        print(string)
        print('=' * len(string))

        cmd = getattr(log_file, 'cmd_{0}'.format(command))
        result = cmd()
        print(result)

    return log_file  # return the log_file object so that tests can inspect it


def console_script():
    parser = create_parser()
    arguments = parse_arguments(parser.parse_args())
    main(arguments)
