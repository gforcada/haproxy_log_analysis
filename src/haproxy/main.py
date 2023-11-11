import argparse
import os

from haproxy.logfile import Log
from haproxy.utils import (
    VALID_COMMANDS,
    VALID_FILTERS,
    validate_arg_date,
    validate_arg_delta,
)


def create_parser():
    desc = 'Analyze HAProxy log files and outputs statistics about it'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-l', '--log', help='HAProxy log file to analyze')

    parser.add_argument(
        '-s',
        '--start',
        help='Process log entries starting at this time, in HAProxy date '
        'format (e.g. 11/Dec/2013 or 11/Dec/2013:19:31:41). '
        'At least provide the day/month/year. Values not specified will '
        'use their base value (e.g. 00 for hour). Use in conjunction '
        'with -d to limit the number of entries to process.',
    )

    parser.add_argument(
        '-d',
        '--delta',
        help='Limit the number of entries to process. Express the time delta '
        'as a number and a time unit, e.g.: 1s, 10m, 3h or 4d (for 1 '
        'second, 10 minutes, 3 hours or 4 days). Use in conjunction with '
        '-s to only analyze certain time delta. If no start time is '
        'given, the time on the first line will be used instead.',
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
        '--list-commands', action='store_true', help='Lists all commands available.'
    )

    parser.add_argument(
        '--list-filters', action='store_true', help='Lists all filters available.'
    )

    parser.add_argument('--json', action='store_true', help='Output results in json.')
    parser.add_argument(
        '--invalid',
        action='store_false',
        help='Print the lines that could not be parsed. '
        'Be aware that mixing it with the print command will mix their output.',
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
        'json': None,
        'invalid_lines': None,
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
        validate_arg_date(args.start)
        data['start'] = args.start

    if args.delta is not None:
        validate_arg_delta(args.delta)
        data['delta'] = args.delta

    if args.command is not None:
        data['commands'] = parse_arg_commands(args.command)

    if args.filter is not None:
        data['filters'] = parse_arg_filters(args.filter)

    if args.log is not None:
        _validate_arg_logfile(args.log)
        data['log'] = args.log

    if args.json is not None:
        data['json'] = args.json

    if args.invalid:
        data['invalid_lines'] = args.json

    return data


def parse_arg_commands(commands_list):
    input_commands = commands_list.split(',')
    for cmd in input_commands:
        if cmd not in VALID_COMMANDS:
            raise ValueError(
                f'command "{cmd}" is not available. '
                'Use --list-commands to get a list of all available commands.'
            )
    return input_commands


def parse_arg_filters(filters_arg):
    input_filters = filters_arg.split(',')

    return_data = []
    for filter_expression in input_filters:
        filter_name = filter_expression
        filter_arg = None

        if filter_expression.endswith(']'):
            if '[' not in filter_expression:
                raise ValueError(
                    f'Error on filter "{filter_expression}". '
                    f'It is missing an opening square bracket.'
                )
            filter_name, filter_arg = filter_expression.split('[')
            filter_arg = filter_arg[:-1]  # remove the closing square bracket

        if filter_name not in VALID_FILTERS:
            raise ValueError(
                f'filter "{filter_name}" is not available. Use --list-filters to get a list of all available filters.'
            )

        return_data.append((filter_name, filter_arg))

    return return_data


def _validate_arg_logfile(filename):
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.exists(filepath):
        raise ValueError(f'filename {filepath} does not exist')


def print_commands():
    """Prints all commands available with their description."""
    for command_name in sorted(VALID_COMMANDS.keys()):
        print(VALID_COMMANDS[command_name]['description'])


def print_filters():
    """Prints all filters available with their description."""
    for filter_name in sorted(VALID_FILTERS.keys()):
        print(VALID_FILTERS[filter_name]['description'])


def show_help(data):
    # make sure that if no arguments are passed the help is shown
    show = True
    ignore_keys = ('log', 'json', 'negate_filter', 'invalid_lines')
    for key in data:
        if data[key] is not None and key not in ignore_keys:
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

    # initialize the log file
    log_file = Log(
        logfile=args['log'],
        start=args['start'],
        delta=args['delta'],
        show_invalid=args['invalid_lines'],
    )

    # get the commands and filters to use
    filters_to_use = requested_filters(args)
    cmds_to_use = requested_commands(args)

    # double negation: when a user wants to negate the filters,
    # the argument parsing sets `negate_filter` to True,
    # but the filtering logic (the `all()`) returns True if the line meets all filters
    # so reversing whatever `negate_filter` has is what the user wants :)
    expected_filtering = True
    if args['negate_filter']:
        expected_filtering = False
    # process all log lines
    for line in log_file:
        if all(f(line) for f in filters_to_use) is expected_filtering:
            for cmd in cmds_to_use:
                cmd(line)

    # print the results
    print('\nRESULTS\n')
    output = None
    if args['json']:
        output = 'json'
    for cmd in cmds_to_use:
        cmd.results(output=output)


def requested_filters(args):
    filters_list = []
    if args['filters']:
        for filter_name, arg in args['filters']:
            filter_func = VALID_FILTERS[filter_name]['obj']
            filters_list.append(filter_func(arg))
    return filters_list


def requested_commands(args):
    cmds_list = []
    for command in args['commands']:
        cmd_klass = VALID_COMMANDS[command]['klass']
        cmds_list.append(cmd_klass())
    return cmds_list


def console_script():  # pragma: no cover
    parser = create_parser()
    arguments = parse_arguments(parser.parse_args())
    main(arguments)
