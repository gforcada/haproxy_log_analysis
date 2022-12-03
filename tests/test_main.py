import sys

import pytest

from haproxy.main import create_parser, main, parse_arguments
from haproxy.utils import VALID_COMMANDS, VALID_FILTERS

PY310_OR_HIGHER = sys.version_info[1] > 9


@pytest.fixture
def default_arguments():
    """Return all the expected arguments the main function expects."""
    return {
        'start': None,
        'delta': None,
        'log': 'tests/files/small.log',
        'commands': ['counter'],
        'negate_filter': None,
        'filters': None,
        'list_commands': False,
        'list_filters': False,
        'json': False,
        'invalid_lines': False,
    }


@pytest.mark.parametrize(
    'switch, listing',
    [('list-filters', VALID_FILTERS), ('list-commands', VALID_COMMANDS)],
)
def test_list_filters_and_commands(capsys, switch, listing):
    """Test that one can request the filters/commands to be listed."""
    parser = create_parser()
    data = parse_arguments(parser.parse_args([f'--{switch}']))
    argument = switch.replace('-', '_')
    for key in data:
        expected = None
        if key == argument:
            expected = True
        assert data[key] is expected
    main(data)
    output_text = capsys.readouterr().out
    for name in listing:
        assert f'{name}: ' in output_text


def test_show_help(capsys):
    """Check that the help is shown if no arguments are given."""
    parser = create_parser()
    data = parse_arguments(parser.parse_args([]))
    main(data)
    output_text = capsys.readouterr().out
    if PY310_OR_HIGHER:
        assert 'options:' in output_text
    else:
        assert 'optional arguments:' in output_text
    assert '--list-filters ' in output_text
    assert '--list-commands ' in output_text


def test_main(capsys, default_arguments):
    """Check that the main function works as expected with default arguments."""
    main(default_arguments)
    output_text = capsys.readouterr().out
    assert 'COUNTER\n=======\n9' in output_text


def test_main_with_filter(capsys, default_arguments):
    """Check that the filters are applied as expected."""
    default_arguments['filters'] = [
        ('server', 'instance1'),
    ]
    main(default_arguments)
    output_text = capsys.readouterr().out
    assert 'COUNTER\n=======\n4' in output_text


def test_main_negate_filter(capsys, default_arguments):
    """Check that filters can be reversed."""
    default_arguments['filters'] = [
        ('server', 'instance1'),
    ]
    default_arguments['negate_filter'] = True
    main(default_arguments)
    output_text = capsys.readouterr().out
    assert 'COUNTER\n=======\n5' in output_text


def test_print_no_output(capsys, default_arguments):
    """Check that the print header is not shown."""
    default_arguments['commands'] = ['print']
    main(default_arguments)
    output_text = capsys.readouterr().out
    assert 'PRINT\n=====' not in output_text


def test_json_output(capsys, default_arguments):
    """Check that the JSON switch is used and JSON output is printed."""
    default_arguments['json'] = True
    main(default_arguments)
    output_text = capsys.readouterr().out
    assert 'COUNTER\n=======\n9' not in output_text
    assert '{"COUNTER": 9}' in output_text
