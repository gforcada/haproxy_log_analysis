# -*- coding: utf-8 -*-
from haproxy.haproxy_logfile import HaproxyLogFile

import unittest


class HaproxyLogFileTest(unittest.TestCase):

    def test_haproxy_log_file_error_no_file(self):
        """Check that trying to parse a non existing file raises an error"""
        log_file = HaproxyLogFile()
        with self.assertRaises(ValueError):
            log_file.parse_file()

    def test_haproxy_log_file_parsed(self):
        """Check that log files are parsed"""
        log_file = HaproxyLogFile(
            logfile='haproxy/tests/files/dummy_small.log'
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
