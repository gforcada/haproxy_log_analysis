# -*- coding: utf-8 -*-
from datetime import datetime
from haproxy import filters
from haproxy.logfile import Log
from haproxy.line import Line
from haproxy.main import main

import pytest


def test_logfile_default_values():
    """Check that the default values are set."""
    log_file = Log('something')
    assert log_file.logfile == 'something'
    assert log_file.invalid_lines == 0
    assert log_file.valid_lines == 0
    assert log_file.total_lines == 0
    assert log_file.start is None
    assert log_file.end is None


@pytest.mark.parametrize(
    'start_str, start_obj, delta, end_obj',
    [
        (None, None, None, None),
        (None, None, '3d', None),
        ('12/Dec/2019', datetime(2019, 12, 12), None, None),
        ('12/Dec/2019', datetime(2019, 12, 12), '3d', datetime(2019, 12, 15)),
    ],
)
def test_start_and_end_attributes(start_str, start_obj, delta, end_obj):
    """Check that the start and end of attributes of Log objects are set as expected."""
    log_file = Log('something', start=start_str, delta=delta)
    assert log_file.logfile == 'something'
    assert log_file.invalid_lines == 0
    assert log_file.start == start_obj
    assert log_file.end == end_obj


@pytest.mark.parametrize(
    'accept_date, start, delta, is_valid',
    [
        # valid line not to be stripped, returned
        ('09/Dec/2013:12:59:46.633', None, None, True),
        # invalid line, not returned
        (None, None, None, False),
        # valid line before time frame, not returned
        ('09/Dec/2013:12:59:46.633', '09/Dec/2014', None, False),
        # valid line after time frame, not returned
        ('09/Dec/2013:12:59:46.633', '08/Dec/2012', '3d', False),
        # valid line within time frame, returned
        ('09/Dec/2013:12:59:46.633', '08/Dec/2013', '3d', True),
    ],
)
def test_parse_lines(haproxy_line_factory, accept_date, start, delta, is_valid):
    """Check that lines are parsed and checked.

    Only if they are valid, they are returned, otherwise, they are counted as invalid.
    """
    log_file = Log('something', start=start, delta=delta)
    assert log_file.invalid_lines == 0
    if accept_date:
        line = haproxy_line_factory(accept_date=accept_date)
    else:
        line = ''
    result = log_file.parse_line(line)
    if is_valid:
        assert result.raw_line == line
        assert log_file.invalid_lines == 0
    else:
        assert result is None
        assert log_file.invalid_lines == 1


def test_total_lines():
    """Check that the total amount of lines are always counted."""
    log_file = Log(logfile='haproxy/tests/files/2_ok_1_invalid.log')
    _ = [x for x in log_file]
    assert log_file.total_lines == 3
    assert log_file.valid_lines == 2
    assert log_file.invalid_lines == 1


#
# def test_negate_filter(self):
#    """Check that reversing a filter output works as expected."""
#    filter_func = filters.filter_ssl()
#    log_file = Log(logfile='files/connection.log')
#
#    # total number of log lines
#    self.assertEqual(log_file.cmd_counter(), 12)
#
#    # only SSL lines
#    only_ssl = log_file.filter(filter_func)
#    self.assertEqual(only_ssl.cmd_counter(), 7)
#
#    # non SSL lines
#    non_ssl = log_file.filter(filter_func, reverse=True)
#    self.assertEqual(non_ssl.cmd_counter(), 5)
#
#    # we did get all lines?
#    self.assertEqual(
#        log_file.cmd_counter(), only_ssl.cmd_counter() + non_ssl.cmd_counter()
#    )
