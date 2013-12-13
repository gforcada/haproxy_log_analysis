# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from haproxy.haproxy_logfile import HaproxyLogFile
from haproxy.main import main

import unittest


class HaproxyLogFileTest(unittest.TestCase):

    def test_haproxy_log_file_from_main(self):
        start = datetime.now()
        delta = timedelta(1)
        filename = 'haproxy/tests/files/dummy_unsorted.log'
        data = {
            'start': start,
            'delta': delta,
            'filename': filename,
            'commands': ['counter', ],
        }
        logfile = main(data)

        self.assertEqual(logfile.start_time, start)
        self.assertEqual(logfile.delta, delta)
        self.assertEqual(logfile.end_time, start + delta)
        self.assertEqual(logfile.logfile, filename)

    def test_haproxy_log_file_error_no_file(self):
        """Check that trying to parse a non existing file raises an error"""
        log_file = HaproxyLogFile()
        with self.assertRaises(ValueError):
            log_file.parse_file()

    def test_haproxy_log_file_parsed(self):
        """Check that log files are parsed"""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_unsorted.log'
        )
        self.assertEqual(log_file.cmd_counter(), 0)
        log_file.parse_file()
        self.assertTrue(log_file.cmd_counter() > 0)

    def test_haproxy_log_file_total_lines(self):
        """Check that even if some lines are not valid, 'total_lines' counts
        all of them.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_2_ok_1_invalid.log'
        )
        log_file.parse_file()
        self.assertEqual(log_file.total_lines, 3)

    def test_haproxy_log_file_valid_and_invalid_lines(self):
        """Check that if some log lines can not be parsed both numbers are
        correctly reported.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_2_ok_1_invalid.log'
        )
        log_file.parse_file()
        self.assertEqual(log_file.cmd_counter(), 2)
        self.assertEqual(log_file.cmd_counter_invalid(), 1)

    def test_haproxy_log_file_attributes_start_and_end_time(self):
        """Check that both 'start_time' and 'end_time' are correct"""
        now = datetime.now()
        one_day = timedelta(days=1)
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_2_ok_1_invalid.log',
            start=now,
            delta=one_day,
        )
        self.assertEqual(log_file.start_time, now)
        self.assertEqual(log_file.end_time, now + one_day)

    def test_haproxy_log_file_attributes_start_and_end_time_no_value(self):
        """Check that both 'start_time' and 'end_time' are None if no value
        is passed on HaproxyLogFile __init__ method.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_2_ok_1_invalid.log'
        )
        self.assertEqual(log_file.start_time, None)
        self.assertEqual(log_file.end_time, None)

    def test_haproxy_log_file_attributes_start_time_no_delta(self):
        """Check how 'start_time', 'delta' and 'end_time' attributes are
        set as they should if only start time is given.
        """
        now = datetime.now()
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_2_ok_1_invalid.log',
            start=now,
        )
        self.assertEqual(log_file.start_time, now)
        self.assertEqual(log_file.delta, None)
        self.assertEqual(log_file.end_time, None)

    def test_haproxy_log_file_start_time_no_results(self):
        """Check that if the start time is after all log entries, no log
        entries are considered.
        """
        after_log_entries = datetime(year=2013, month=12, day=13)
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_test_times.log',
            start=after_log_entries,
        )
        self.assertEqual(log_file.start_time, after_log_entries)
        self.assertEqual(log_file.delta, None)
        self.assertEqual(log_file.end_time, None)

        log_file.parse_file()
        self.assertEqual(log_file.total_lines, 9)
        self.assertEqual(log_file.cmd_counter(), 0)
        self.assertEqual(log_file.cmd_counter_invalid(), 0)

    def test_haproxy_log_file_start_time_some_results(self):
        """Check that if the start time is between some log entries, the log
        entries are considered.
        """
        between_log_entries = datetime(year=2013, month=12, day=10)
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_test_times.log',
            start=between_log_entries,
        )
        self.assertEqual(log_file.start_time, between_log_entries)
        self.assertEqual(log_file.delta, None)
        self.assertEqual(log_file.end_time, None)

        log_file.parse_file()
        self.assertEqual(log_file.total_lines, 9)
        self.assertEqual(log_file.cmd_counter(), 6)
        self.assertEqual(log_file.cmd_counter_invalid(), 0)

    def test_haproxy_log_file_start_time_and_end_time_some_results(self):
        """Check that if the start time is between some log entries and there
        is a end_time, the entries that fit in are counted.
        """
        between_log_entries = datetime(year=2013, month=12, day=9, hour=11)
        one_day = timedelta(days=1)
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_test_times.log',
            start=between_log_entries,
            delta=one_day,
        )
        self.assertEqual(log_file.start_time, between_log_entries)
        self.assertEqual(log_file.delta, one_day)
        self.assertEqual(log_file.end_time, between_log_entries + one_day)

        log_file.parse_file()
        self.assertEqual(log_file.total_lines, 9)
        self.assertEqual(log_file.cmd_counter(), 3)
        self.assertEqual(log_file.cmd_counter_invalid(), 0)

    def test_haproxy_log_file_lines_sorted(self):
        """Check that after parsing a log file, the valid log lines are kept
        sorted to ease further work on them.
        """
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_unsorted.log',
        )
        log_file.parse_file()

        previous = log_file._valid_lines[0]
        previous_date = previous.accept_date
        for line in log_file._valid_lines[1:]:
            self.assertTrue(previous_date < line.accept_date)
