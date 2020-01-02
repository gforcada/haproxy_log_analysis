from haproxy.main import create_parser
from haproxy.main import main
from haproxy.main import parse_arguments
from haproxy.utils import VALID_COMMANDS
from haproxy.utils import VALID_FILTERS

import pytest


@pytest.mark.parametrize(
    'switch, listing',
    [('list-filters', VALID_FILTERS), ('list-commands', VALID_COMMANDS),],
)
def test_list_filters_and_commands(capsys, switch, listing):
    """Test that one can request the filters/commands to be listed."""
    parser = create_parser()
    data = parse_arguments(parser.parse_args([f'--{switch}',]))
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
    assert 'optional arguments:' in output_text
    assert '--list-filters ' in output_text
    assert '--list-commands ' in output_text


def test_main(capsys):
    log_path = 'haproxy/tests/files/small.log'
    data = {
        'start': None,
        'delta': None,
        'log': log_path,
        'commands': ['counter'],
        'negate_filter': None,
        'filters': None,
        'list_commands': False,
        'list_filters': False,
        'json': False,
    }
    main(data)
    output_text = capsys.readouterr().out
    assert 'COUNTER' in output_text
    assert '=======' in output_text
    assert '9' in output_text


def test_main_with_filter(capsys):
    log_path = 'haproxy/tests/files/small.log'
    data = {
        'start': None,
        'delta': None,
        'log': log_path,
        'commands': ['counter'],
        'negate_filter': None,
        'filters': [('server', 'instance1'),],
        'list_commands': False,
        'list_filters': False,
        'json': False,
    }
    main(data)
    output_text = capsys.readouterr().out
    assert 'COUNTER' in output_text
    assert '=======' in output_text
    assert '4' in output_text


# class ArgumentParsingTest(unittest.TestCase):
#
#    def test_arg_parser_json(self):
#        """Test that we really output json."""
#        arguments = ['-l', 'haproxy/tests/files/small.log', '--json', '-c', 'counter']
#        data = parse_arguments(self.parser.parse_args(arguments))
#        test_output = NamedTemporaryFile(mode='w', delete=False)
#        test_result = True
#
#        with RedirectStdout(stdout=test_output):
#            main(data)
#
#        # Since python 3.5, json.load returns a JSONDecodeError instead of a
#        # ValueError
#        try:
#            json_parse_exception = json.decoder.JSONDecodeError
#        except AttributeError:
#            json_parse_exception = ValueError
#
#        try:
#            with open(test_output.name) as json_file:
#                json.load(json_file)
#        except json_parse_exception:
#            test_result = False
#
#        self.assertTrue(test_result)
#
#    def test_arg_parser_filters(self):
#        """Check that the filter logic on haproxy.main.main works as expected.
#        """
#        arguments = [
#            '-f',
#            'ssl,ip[1.2.3.4]',
#            '-c',
#            'counter',
#            '-l',
#            'haproxy/tests/files/filters.log',
#        ]
#        data = parse_arguments(self.parser.parse_args(arguments))
#        test_output = NamedTemporaryFile(mode='w', delete=False)
#
#        with RedirectStdout(stdout=test_output):
#            main(data)
#
#        with open(test_output.name, 'r') as output_file:
#            output_text = output_file.read()
#
#            self.assertIn('counter', output_text)
#            self.assertIn('2', output_text)
#
#    def test_arg_parser_filters_start(self):
#        """Check that the filter_time is applied on the log file if a start
#        argument is given.
#        """
#        arguments = [
#            '-s',
#            '12/Dec/2015',
#            '-c',
#            'counter',
#            '-l',
#            'haproxy/tests/files/filters.log',
#        ]
#        data = parse_arguments(self.parser.parse_args(arguments))
#        test_output = NamedTemporaryFile(mode='w', delete=False)
#
#        with RedirectStdout(stdout=test_output):
#            main(data)
#
#        with open(test_output.name, 'r') as output_file:
#            output_text = output_file.read()
#
#            self.assertIn('counter', output_text)
#            self.assertIn('4', output_text)
#
#    def test_arg_parser_filters_start_and_delta(self):
#        """Check that the filter_time is applied on the log file if a start
#        and delta arguments are given.
#        """
#        arguments = [
#            '-s',
#            '11/Dec/2015:11',
#            '-d',
#            '3h',
#            '-c',
#            'counter',
#            '-l',
#            'haproxy/tests/files/filters.log',
#        ]
#        data = parse_arguments(self.parser.parse_args(arguments))
#        test_output = NamedTemporaryFile(mode='w', delete=False)
#
#        with RedirectStdout(stdout=test_output):
#            main(data)
#
#        with open(test_output.name, 'r') as output_file:
#            output_text = output_file.read()
#
#            self.assertIn('counter', output_text)
#            self.assertIn('2', output_text)
#
#    def test_arg_parser_negate_filter_output(self):
#        """Check that if the negate filter argument is set, is actually used.
#        """
#        arguments = [
#            '-c',
#            'counter',
#            '-l',
#            'haproxy/tests/files/small.log',
#            '-f',
#            'server[instance3]',
#            '-n',
#        ]
#
#        # with the negate argument set, there should be all but instance3 lines
#        data = parse_arguments(self.parser.parse_args(arguments))
#        test_output = NamedTemporaryFile(mode='w', delete=False)
#
#        with RedirectStdout(stdout=test_output):
#            main(data)
#
#        with open(test_output.name, 'r') as output_file:
#            output_text = output_file.read()
#
#            self.assertIn('counter', output_text)
#            self.assertIn('7', output_text)
#
#        # remove the negate argument, now only 2 lines should match
#        arguments.pop()
#        data = parse_arguments(self.parser.parse_args(arguments))
#        test_output = NamedTemporaryFile(mode='w', delete=False)
#
#        with RedirectStdout(stdout=test_output):
#            main(data)
#
#        with open(test_output.name, 'r') as output_file:
#            output_text = output_file.read()
#
#            self.assertIn('counter', output_text)
#            self.assertIn('2', output_text)
#
#        # finally remove the filter, 9 lines should match
#        arguments.pop()
#        arguments.pop()  # this second pop() is because of the argument
#        data = parse_arguments(self.parser.parse_args(arguments))
#        test_output = NamedTemporaryFile(mode='w', delete=False)
#
#        with RedirectStdout(stdout=test_output):
#            main(data)
#
#        with open(test_output.name, 'r') as output_file:
#            output_text = output_file.read()
#
#            self.assertIn('counter', output_text)
#            self.assertIn('9', output_text)
#
