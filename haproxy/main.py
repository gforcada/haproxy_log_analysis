# -*- encoding: utf-8 -*-
from haproxy.haproxy_logfile import HaproxyLogFile
from haproxy import DELTA_REGEX
from haproxy import START_REGEX
from haproxy import filters

import argparse
import os
import re


VALID_FILTERS = [
    f[7:] for f in dir(filters) if f.startswith('filter_')
    and not f.endswith('time_frame')]


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
             '-l to get a full list of them.',
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
    available_commands = HaproxyLogFile.commands()
    for cmd in input_commands:
        if cmd not in available_commands:
            msg = 'command "{0}" is not available. Use -l to get a list of ' \
                  'all available commands.'
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

    # create a HaproxyLogFile instance and parse the log file
    log_file = HaproxyLogFile(
        logfile=args['log'],
    )
    log_file.parse_file()

    # apply the time frame filter
    if args['start'] is not None or args['delta'] is not None:
        start = args['start'] or ''
        delta = args['delta'] or ''
        filter_string = 'filters.filter_time_frame("{0}", "{1}")'
        filter_func = eval(filter_string.format(start, delta))

        log_file = log_file.filter(filter_func)

    # apply all other filters given
    if args['filters'] is not None:
        filter_string = 'filters.filter_{0}({1})'
        for filter_data in args['filters']:
            arg = ''
            if filter_data[1] is not None:
                arg = filter_data[1]
                arg = "'{0}'".format(arg)

            filter_func = eval(filter_string.format(filter_data[0], arg))

            log_file = log_file.filter(filter_func)

    # run all commands
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
