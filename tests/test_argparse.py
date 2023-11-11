from haproxy.main import create_parser
from haproxy.main import parse_arg_filters
from haproxy.main import parse_arguments

import pytest


def test_parser_arguments_defaults():
    """Test that the argument parsing defaults works."""
    parser = create_parser()
    data = parse_arguments(parser.parse_args([]))
    assert data == {
        'start': None,
        'delta': None,
        'commands': None,
        'filters': None,
        'negate_filter': None,
        'log': None,
        'list_commands': None,
        'list_filters': None,
        'json': False,
        'invalid_lines': False,
    }


@pytest.mark.parametrize(
    ('argument', 'option'),
    [
        ('--list-commands', 'list_commands'),
        ('--list-filters', 'list_filters'),
        ('--negate-filter', 'negate_filter'),
        ('-n', 'negate_filter'),
        ('--json', 'json'),
    ],
)
def test_parser_boolean_arguments(argument, option):
    """Test that the argument parsing defaults works."""
    parser = create_parser()
    data = parse_arguments(parser.parse_args([argument]))
    assert data[option] is True


@pytest.mark.parametrize(
    ('start', 'delta'), [('30/Dec/2019', '3d'), ('20/Jun/2015', '2h')]
)
def test_arguments_dates(start, delta):
    """Check that properly formatted start and delta arguments are processed fine.

    Thus they are extracted and stored for later use.
    """
    parser = create_parser()
    data = parse_arguments(parser.parse_args(['-s', start, '-d', delta]))
    assert data['start'] == start
    assert data['delta'] == delta


@pytest.mark.parametrize('start', ['33/Dec/2019', '5/Hallo/2019'])
def test_arguments_date_invalid(start):
    """Incorrectly formatted start argument raises an exception."""
    parser = create_parser()
    with pytest.raises(ValueError, match='--start argument is not valid'):
        parse_arguments(parser.parse_args(['-s', start]))


@pytest.mark.parametrize('delta', ['3P', '2323MM'])
def test_arguments_delta_invalid(delta):
    """Incorrectly formatted delta argument raises an exception."""
    parser = create_parser()
    with pytest.raises(ValueError, match='--delta argument is not valid'):
        parse_arguments(parser.parse_args(['-d', delta]))


@pytest.mark.parametrize(
    ('cmds', 'is_valid'),
    [
        ('counter', True),
        ('counter,ip_counter', True),
        ('ip_counter,count_data', False),
        ('count_data', False),
    ],
)
def test_commands_arguments(cmds, is_valid):
    """Test that the commands are parsed, and an exception raised otherwise."""
    parser = create_parser()
    if not is_valid:
        with pytest.raises(ValueError, match='is not available. Use --list-commands'):
            parse_arguments(parser.parse_args(['-c', cmds]))
    else:
        data = parse_arguments(parser.parse_args(['-c', cmds]))
        assert data['commands'] == cmds.split(',')


@pytest.mark.parametrize(
    ('filters_list', 'is_valid'),
    [
        ('ip_range', True),
        ('slow_requests,backend', True),
        ('tomatoes', False),
        ('slow_requests,potatoes', False),
    ],
)
def test_filters_arguments(filters_list, is_valid):
    """Test that the filters are parsed, and an exception raised otherwise."""
    parser = create_parser()
    if not is_valid:
        with pytest.raises(ValueError, match='is not available. Use --list-filters'):
            parse_arguments(parser.parse_args(['-f', filters_list]))
    else:
        data = parse_arguments(parser.parse_args(['-f', filters_list]))
        assert data['filters'] == [(x, None) for x in filters_list.split(',')]


@pytest.mark.parametrize(
    ('filter_expression', 'expected'),
    [
        ('ip_range', [('ip_range', None)]),
        ('ip_rangelala]', None),
        ('ip_range[lala]', [('ip_range', 'lala')]),
    ],
)
def test_filters_with_arguments(filter_expression, expected):
    """Check that the arguments given to the filters are parsed properly.

    Or raise and exception otherwise.
    """
    if expected is None:
        with pytest.raises(ValueError, match='It is missing an opening square bracket'):
            parse_arg_filters(filter_expression)
    else:
        data = parse_arg_filters(filter_expression)
        assert data == expected


@pytest.mark.parametrize(
    ('filename', 'is_valid'),
    [
        ('tests/conftest.py', True),
        ('tests/non-existing-file.py', False),
    ],
)
def test_log_argument(filename, is_valid):
    """Check that the argument parsing validates that the file exists."""
    parser = create_parser()
    if is_valid:
        data = parse_arguments(parser.parse_args(['-l', filename]))
        assert data['log'] == filename
    else:
        with pytest.raises(ValueError, match=f'{filename} does not exist'):
            parse_arguments(parser.parse_args(['-l', filename]))
