# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from haproxy import filters
from haproxy.main import create_parser
from haproxy.main import main
from haproxy.main import parse_arguments
from haproxy.haproxy_logfile import HaproxyLogFile
from tempfile import NamedTemporaryFile

import sys
import unittest


class RedirectStdout(object):
    """Context manager class that redirects standard output to a file.

    This helps analyzing standard output (print() function output) on tests
    without having to do any change on the code, just on tests.
    """

    def __init__(self, stdout=None):
        self._stdout = stdout or sys.stdout
        self.old_stdout = None

    def __enter__(self):
        self.old_stdout = sys.stdout
        self.old_stdout.flush()
        sys.stdout = self._stdout

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush()
        sys.stdout = self.old_stdout


class ArgumentParsingTest(unittest.TestCase):

    def setUp(self):
        self.parser = create_parser()
        self.default_arguments = [
            '-c', 'counter', '-l', 'haproxy/tests/files/huge.log',
        ]

    def test_arg_parser_start_invalid(self):
        """Check that if a 'start' argument is not valid an exception is
        raised.
        """
        arguments = ['-s', '/Dec/2013:14:15:16', ] + self.default_arguments
        with self.assertRaises(ValueError):
            parse_arguments(self.parser.parse_args(arguments))

    def test_arg_parser_start_valid(self):
        """Check that if a 'start' argument is valid is stored."""
        start = '12/Dec/2013:14:15:16'
        arguments = ['-s', start, ] + self.default_arguments
        data = parse_arguments(self.parser.parse_args(arguments))
        self.assertTrue(start, data['start'])

    def test_arg_parser_delta_invalid(self):
        """Check that if an invalid delta argument is passed an exception is
        raised.
        """
        arguments = ['-d', 'invalid', ] + self.default_arguments
        with self.assertRaises(ValueError):
            parse_arguments(self.parser.parse_args(arguments))

    def test_arg_parser_delta_valid(self):
        """Check that if a 'delta' argument is valid is stored."""
        delta = '4d'
        arguments = ['-d', delta, ] + self.default_arguments
        data = parse_arguments(self.parser.parse_args(arguments))
        self.assertTrue(delta, data['delta'])

    def test_arg_parser_log_file_valid(self):
        """Check that any log file passed does exist before handling it
        further.
        """
        arguments = ['-c', 'counter',
                     '-l', 'haproxy/tests/test_argparse.py', ]
        data = parse_arguments(self.parser.parse_args(arguments))
        self.assertEqual('haproxy/tests/test_argparse.py', data['log'])

    def test_arg_parser_log_file_invalid(self):
        """Check that if the log file passed does not exist an exception is
        raised.
        """
        arguments = ['-c', 'counter',
                     '-l', 'non_existing.log', ]
        with self.assertRaises(ValueError):
            parse_arguments(self.parser.parse_args(arguments))

    def test_arg_parser_commands_valid(self):
        """Test that valid commands are correctly parsed."""
        arguments = ['-c', 'http_methods',
                     '-l', 'haproxy/tests/files/huge.log', ]
        data = parse_arguments(self.parser.parse_args(arguments))
        self.assertEqual(['http_methods', ], data['commands'])

    def test_arg_parser_commands_invalid(self):
        """Test that trying to input non existing commands raises an
        exception.
        """
        with self.assertRaises(ValueError):
            arguments = ['-c', 'non_existing_method',
                         '-l', 'haproxy/tests/files/huge.log', ]
            parse_arguments(self.parser.parse_args(arguments))

    def test_arg_parser_filters_valid(self):
        """Test that valid filters are correctly parsed."""
        arguments = ['-f', 'ssl',
                     '-l', 'haproxy/tests/files/huge.log', ]
        data = parse_arguments(self.parser.parse_args(arguments))
        self.assertEqual([('ssl', None)], data['filters'])

    def test_arg_parser_filters_valid_with_argument(self):
        """Test that valid filters with arguments are correctly parsed."""
        arguments = ['-f', 'ip[something],ssl',
                     '-l', 'haproxy/tests/files/huge.log', ]
        data = parse_arguments(self.parser.parse_args(arguments))
        self.assertEqual([('ip', 'something'), ('ssl', None)],
                         data['filters'])

    def test_arg_parser_filters_invalid(self):
        """Test that trying to input non existing filters raises an
        exception.
        """
        with self.assertRaises(ValueError):
            arguments = ['--filter', 'non_existing_filter',
                         '-l', 'haproxy/tests/files/huge.log', ]
            parse_arguments(self.parser.parse_args(arguments))

    def test_arg_parser_filters_invalid_argument(self):
        """Test that trying to input an invalid filter expression fails."""
        with self.assertRaises(ValueError):
            arguments = ['--filter', 'ip_with_error],ssl',
                         '-l', 'haproxy/tests/files/huge.log', ]
            parse_arguments(self.parser.parse_args(arguments))

    def test_arg_parser_filters_without_closing_bracket(self):
        """Test that trying to input an invalid filter expression fails."""
        with self.assertRaises(ValueError):
            arguments = ['--filter', 'ip],ssl',
                         '-l', 'haproxy/tests/files/huge.log', ]
            parse_arguments(self.parser.parse_args(arguments))

    def test_arg_parser_list_commands(self):
        """Test that list commands argument is parsed."""
        arguments = ['--list-commands', ]
        data = parse_arguments(self.parser.parse_args(arguments))

        for arg in data:
            if arg == 'list_commands':
                self.assertTrue(data['list_commands'])
            else:
                self.assertEqual(data[arg], None)

    def test_arg_parser_list_commands_output(self):
        """Test that list commands argument outputs what's expected."""
        arguments = ['--list-commands', ]
        data = parse_arguments(self.parser.parse_args(arguments))
        test_output = NamedTemporaryFile(mode='w', delete=False)

        with RedirectStdout(stdout=test_output):
            main(data)

        with open(test_output.name, 'r') as output_file:
            output_text = output_file.read()

            for cmd in HaproxyLogFile.commands():
                self.assertIn(cmd, output_text)

    def test_arg_parser_help_output(self):
        """Test that when no arguments are given the help is shown."""
        data = parse_arguments(self.parser.parse_args([]))
        test_output = NamedTemporaryFile(mode='w', delete=False)

        with RedirectStdout(stdout=test_output):
            main(data)

        with open(test_output.name, 'r') as output_file:
            output_text = output_file.read()

            for keyword in ('LOG', 'START', 'DELTA', 'COMMAND'):
                self.assertIn(keyword, output_text)

    def test_arg_parser_help_output_only_log_file(self):
        """Test that when no arguments are given the help is shown."""
        arguments = ['-l', 'haproxy/tests/files/queue.log', ]
        data = parse_arguments(self.parser.parse_args(arguments))
        test_output = NamedTemporaryFile(mode='w', delete=False)

        with RedirectStdout(stdout=test_output):
            main(data)

        with open(test_output.name, 'r') as output_file:
            output_text = output_file.read()

            for keyword in ('LOG', 'START', 'DELTA', 'COMMAND'):
                self.assertIn(keyword, output_text)

    def test_arg_parser_list_filters_output(self):
        """Test that list filters argument outputs what's expected."""
        arguments = ['--list-filters', ]
        data = parse_arguments(self.parser.parse_args(arguments))
        test_output = NamedTemporaryFile(mode='w', delete=False)

        with RedirectStdout(stdout=test_output):
            main(data)

        with open(test_output.name, 'r') as output_file:
            output_text = output_file.read()

            filters_list = [f for f in dir(filters) if f.startswith('filter_')]

            for filter_name in filters_list:
                self.assertIn(filter_name[7:], output_text)

    def test_arg_parser_filters(self):
        """Check that the filter logic on haproxy.main.main works as expected.
        """
        arguments = ['-f', 'ssl,ip[1.2.3.4]',
                     '-c', 'counter',
                     '-l', 'haproxy/tests/files/filters.log', ]
        data = parse_arguments(self.parser.parse_args(arguments))
        test_output = NamedTemporaryFile(mode='w', delete=False)

        with RedirectStdout(stdout=test_output):
            main(data)

        with open(test_output.name, 'r') as output_file:
            output_text = output_file.read()

            self.assertIn('counter', output_text)
            self.assertIn('2', output_text)
