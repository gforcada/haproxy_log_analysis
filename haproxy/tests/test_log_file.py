# -*- coding: utf-8 -*-
from datetime import datetime
from haproxy import filters
from haproxy.logfile import Log
from haproxy.main import main
from time import sleep

import os
import unittest


class LogFileTest(unittest.TestCase):

    def tearDown(self):
        """Be sure to remove all pickle files so to not keep stale files
        around.
        """
        path = 'haproxy/tests/files'
        for filename in os.listdir(path):
            if filename.endswith('.pickle'):
                os.remove('{0}/{1}'.format(path, filename))

    def test_from_main(self):
        log_path = 'haproxy/tests/files/small.log'
        data = {
            'start': None,
            'delta': None,
            'log': log_path,
            'commands': ['counter', ],
            'negate_filter': None,
            'filters': None,
            'list_commands': False,
            'list_filters': False,
        }
        logfile = main(data)

        self.assertEqual(logfile.logfile, log_path)

    def test_parsed(self):
        """Check that log files are parsed."""
        log_file = Log(
            logfile='haproxy/tests/files/small.log'
        )
        self.assertTrue(log_file.cmd_counter() > 0)

    def test_total_lines(self):
        """Check that even if some lines are not valid, 'total_lines' counts
        all of them.
        """
        log_file = Log(
            logfile='haproxy/tests/files/2_ok_1_invalid.log'
        )
        self.assertEqual(log_file.total_lines, 3)

    def test_valid_and_invalid_lines(self):
        """Check that if some log lines can not be parsed both numbers are
        correctly reported.
        """
        log_file = Log(
            logfile='haproxy/tests/files/2_ok_1_invalid.log'
        )
        self.assertEqual(log_file.cmd_counter(), 2)
        self.assertEqual(log_file.cmd_counter_invalid(), 1)

    def test_lines_sorted(self):
        """Check that after parsing a log file, the valid log lines are kept
        sorted to ease further work on them.
        """
        log_file = Log(
            logfile='haproxy/tests/files/small.log',
        )

        previous = log_file._valid_lines[0]
        previous_date = previous.accept_date
        for line in log_file._valid_lines[1:]:
            self.assertTrue(previous_date < line.accept_date)

    def test_cmd_http_methods(self):
        """Check that the http methods command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/small.log',
        )
        http_methods = log_file.cmd_http_methods()

        self.assertEqual(len(http_methods), 3)
        self.assertEqual(http_methods['GET'], 4)
        self.assertEqual(http_methods['POST'], 2)
        self.assertEqual(http_methods['HEAD'], 3)

    def test_cmd_ip_counter(self):
        """Check that the ip counter command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/small.log',
        )
        ip_counter = log_file.cmd_ip_counter()

        self.assertEqual(len(ip_counter), 4)
        self.assertEqual(ip_counter['123.123.123.123'], 4)
        self.assertEqual(ip_counter['123.123.124.124'], 2)
        self.assertEqual(ip_counter['123.123.124.123'], 1)
        self.assertEqual(ip_counter['123.123.123.124'], 1)

    def test_cmd_status_codes(self):
        """Check that the status codes command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/small.log',
        )
        status_codes = log_file.cmd_status_codes_counter()

        self.assertEqual(len(status_codes), 3)
        self.assertEqual(status_codes['404'], 3)
        self.assertEqual(status_codes['200'], 2)
        self.assertEqual(status_codes['300'], 4)

    def test_cmd_request_path_counter(self):
        """Check that the request path counter command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/small.log',
        )
        path_counter = log_file.cmd_request_path_counter()

        self.assertEqual(len(path_counter), 5)
        self.assertEqual(path_counter['/hello'], 3)
        self.assertEqual(path_counter['/world'], 2)
        self.assertEqual(path_counter['/free'], 2)
        self.assertEqual(path_counter['/fra'], 1)
        self.assertEqual(path_counter['/freitag'], 1)

    def test_cmd_slow_requests(self):
        """Check that the slow requests command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/small.log',
        )
        slow_requests = log_file.cmd_slow_requests()

        self.assertEqual(len(slow_requests), 5)
        slow_requests.sort()  # sort them as the log analyzer sorts by dates
        self.assertEqual(slow_requests,
                         [1293, 2936, 2942, 20095, 29408, ])

    def test_cmd_counter_slow_requests(self):
        """Check that the slow requests counter command reports as expected.
        """
        log_file = Log(
            logfile='haproxy/tests/files/small.log',
        )
        slow_requests = log_file.cmd_counter_slow_requests()

        self.assertEqual(slow_requests, 5)

    def test_cmd_server_load(self):
        """Check that the server load counter command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/small.log',
        )
        servers = log_file.cmd_server_load()

        self.assertEqual(len(servers), 3)
        self.assertEqual(servers['instance1'], 4)
        self.assertEqual(servers['instance2'], 3)
        self.assertEqual(servers['instance3'], 2)

    def test_cmd_queue_peaks(self):
        """Check that the queue peaks command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/queue.log',
        )
        peaks = log_file.cmd_queue_peaks()

        self.assertEqual(len(peaks), 4)
        self.assertEqual(peaks[0]['peak'], 4)
        self.assertEqual(peaks[0]['span'], 5)

        self.assertEqual(peaks[1]['peak'], 19)
        self.assertEqual(peaks[1]['span'], 5)

        self.assertEqual(peaks[2]['peak'], 49)
        self.assertEqual(peaks[2]['span'], 3)

        self.assertEqual(peaks[3]['peak'], 3)
        self.assertEqual(peaks[3]['span'], 1)

        self.assertTrue(peaks[0]['first'] < peaks[1]['first'])
        self.assertTrue(peaks[1]['first'] < peaks[2]['first'])
        self.assertTrue(peaks[2]['first'] < peaks[3]['first'])

        self.assertTrue(peaks[0]['last'] < peaks[1]['last'])
        self.assertTrue(peaks[1]['last'] < peaks[2]['last'])
        self.assertTrue(peaks[2]['last'] < peaks[3]['last'])

    def test_cmd_queue_peaks_no_end(self):
        """Check that the queue peaks command reports as expected when the
        last log request did not have any queue.
        """
        log_file = Log(
            logfile='haproxy/tests/files/queue_2.log',
        )
        peaks = log_file.cmd_queue_peaks()

        self.assertEqual(len(peaks), 3)
        self.assertEqual(peaks[0]['peak'], 4)
        self.assertEqual(peaks[0]['span'], 5)

        self.assertEqual(peaks[1]['peak'], 19)
        self.assertEqual(peaks[1]['span'], 5)

        self.assertEqual(peaks[2]['peak'], 49)
        self.assertEqual(peaks[2]['span'], 3)

        self.assertTrue(peaks[0]['first'] < peaks[1]['first'])
        self.assertTrue(peaks[1]['first'] < peaks[2]['first'])

        self.assertTrue(peaks[0]['last'] < peaks[1]['last'])
        self.assertTrue(peaks[1]['last'] < peaks[2]['last'])

    def test_cmd_top_ips(self):
        """Check that the top ips command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/top_ips.log',
        )
        top_ips = log_file.cmd_top_ips()

        self.assertEqual(len(top_ips), 10)
        self.assertEqual(top_ips[0], ('1.1.1.15', 6))
        self.assertEqual(top_ips[1], ('1.1.1.11', 5))

        # as the 3rd and 4th have the same repetitions their order is unknown
        self.assertEqual(top_ips[2][1], 4)
        self.assertEqual(top_ips[3][1], 4)
        self.assertTrue(top_ips[2][0] in ('1.1.1.10', '1.1.1.19'))
        self.assertTrue(top_ips[3][0] in ('1.1.1.10', '1.1.1.19'))

        # the same as above for all the others
        other_ips = [
            '1.1.1.12',
            '1.1.1.13',
            '1.1.1.14',
            '1.1.1.16',
            '1.1.1.17',
            '1.1.1.18',
        ]
        for ip_info in top_ips[4:]:
            self.assertEqual(ip_info[1], 2)
            self.assertTrue(ip_info[0] in other_ips)

            # remove the other_ips to ensure all ips are there
            for position, current in enumerate(other_ips):
                if current == ip_info[0]:
                    del other_ips[position]
                    break

        self.assertEqual(other_ips, [])

    def test_cmd_top_request_paths(self):
        """Check that the top request paths command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/top_paths.log',
        )
        top_paths = log_file.cmd_top_request_paths()

        self.assertEqual(len(top_paths), 10)
        self.assertEqual(top_paths[0], ('/14', 6))
        self.assertEqual(top_paths[1], ('/13', 4))

        # as the 3rd and 4th have the same repetitions their order is unknown
        self.assertEqual(top_paths[2][1], 3)
        self.assertEqual(top_paths[3][1], 3)
        self.assertEqual(top_paths[4][1], 3)
        self.assertTrue(top_paths[2][0] in ('/12', '/15', '/11', ))
        self.assertTrue(top_paths[3][0] in ('/12', '/15', '/11', ))
        self.assertTrue(top_paths[4][0] in ('/12', '/15', '/11', ))

        # the same as above for all the others
        other_paths = [
            '/1',
            '/2',
            '/3',
            '/4',
            '/5',
            '/6',
            '/7',
            '/8',
            '/9',
        ]
        for path_info in top_paths[5:]:
            self.assertEqual(path_info[1], 2)
            self.assertTrue(path_info[0] in other_paths)

            # remove the other_ips to ensure all ips are there
            for position, current in enumerate(other_paths):
                if current == path_info[0]:
                    del other_paths[position]
                    break

        self.assertEqual(len(other_paths), 4)

    def test_cmd_connection_type(self):
        """Check that the connection type command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/connection.log',
        )
        ssl, non_ssl = log_file.cmd_connection_type()

        self.assertEqual(ssl, 7)
        self.assertEqual(non_ssl, 5)

    def test_cmd_requests_per_minute(self):
        """Check that the requests per minute command reports as expected."""
        log_file = Log(
            logfile='haproxy/tests/files/requests_per_minute.log',
        )
        requests = log_file.cmd_requests_per_minute()

        self.assertEqual(len(requests), 5)

        self.assertEqual(
            requests[0],
            (datetime(2013, 12, 11, 11, 2), 8)
        )
        self.assertEqual(
            requests[1],
            (datetime(2013, 12, 11, 11, 3), 3)
        )
        self.assertEqual(
            requests[2],
            (datetime(2013, 12, 11, 11, 13), 5)
        )
        self.assertEqual(
            requests[3],
            (datetime(2013, 12, 11, 11, 52), 7)
        )
        self.assertEqual(
            requests[4],
            (datetime(2013, 12, 11, 12, 2), 9)
        )

    def test_cmd_requests_per_minute_empty(self):
        """Check that the requests per minute command reports nothing if
        there are no valid lines for whichever reason.
        """
        log_file = Log(
            logfile='haproxy/tests/files/empty.log',
        )
        requests = log_file.cmd_requests_per_minute()

        self.assertEqual(None, requests)

    def test_negate_filter(self):
        """Check that reversing a filter output works as expected."""
        filter_func = filters.filter_ssl()
        log_file = Log(
            logfile='haproxy/tests/files/connection.log',
        )

        # total number of log lines
        self.assertEqual(log_file.cmd_counter(), 12)

        # only SSL lines
        only_ssl = log_file.filter(filter_func)
        self.assertEqual(only_ssl.cmd_counter(), 7)

        # non SSL lines
        non_ssl = log_file.filter(filter_func, reverse=True)
        self.assertEqual(non_ssl.cmd_counter(), 5)

        # we did get all lines?
        self.assertEqual(
            log_file.cmd_counter(),
            only_ssl.cmd_counter() + non_ssl.cmd_counter()
        )

    def test_cmd_print_empty(self):
        """Check that the print command prints an empty string if the log file
        is empty.
        """
        log_file = Log(
            logfile='haproxy/tests/files/empty.log',
        )
        data = log_file.cmd_print()
        self.assertEqual('', data)

    def test_cmd_print(self):
        """Check that the print command prints the valid lines."""
        log_file = Log(
            logfile='haproxy/tests/files/2_ok_1_invalid.log',
        )
        data = log_file.cmd_print()
        self.assertNotEqual('', data)

        lines = data.split('\n')
        self.assertEqual(len(lines), 3)

    def test_cmd_average_response_time(self):
        """Check that the average response time returns the expected output."""
        log_file = Log(
            logfile='haproxy/tests/files/average_response.log',
        )
        data = log_file.cmd_average_response_time()
        self.assertEqual(data, 105)

    def test_cmd_average_response_time_aborted(self):
        """Check that the average response time returns the expected output
        when there are aborted connections.
        """
        log_file = Log(
            logfile='haproxy/tests/files/average_response_aborted.log',
        )
        data = log_file.cmd_average_response_time()
        self.assertEqual(data, 110)

    def test_cmd_average_response_time_no_wait(self):
        """Check that the average response time returns the expected output
        when there are connections that did not take any millisecond to reply.
        """
        log_file = Log(
            logfile='haproxy/tests/files/average_response_no_wait.log',
        )
        data = log_file.cmd_average_response_time()
        self.assertEqual(data, 74)

    def test_cmd_average_response_time_empty_log(self):
        """Check that the average response time does not break if no log lines
        are logged.
        """
        log_file = Log(
            logfile='haproxy/tests/files/empty.log',
        )
        data = log_file.cmd_average_response_time()
        self.assertEqual(data, 0)

    def test_cmd_average_waiting_time(self):
        """Check that the average time waiting on queues returns the expected
        output.
        """
        log_file = Log(
            logfile='haproxy/tests/files/average_waiting.log',
        )
        data = log_file.cmd_average_waiting_time()
        self.assertEqual(data, 105)

    def test_cmd_average_waiting_time_empty_log(self):
        """Check that the average time waiting on queues does not break if no
        log lines are logged.
        """
        log_file = Log(
            logfile='haproxy/tests/files/empty.log',
        )
        data = log_file.cmd_average_waiting_time()
        self.assertEqual(data, 0)

    def test_cmd_average_waiting_time_aborted(self):
        """Check that the average time waiting on queues returns the expected
        output when there are aborted connections.
        """
        log_file = Log(
            logfile='haproxy/tests/files/average_waiting_aborted.log',
        )
        data = log_file.cmd_average_waiting_time()
        self.assertEqual(data, 110)

    def test_cmd_average_waiting_time_no_wait(self):
        """Check that the average time waiting on queues returns the expected
        output when there are requests that did not wait at all (i.e.
        time_wait_queues is 0).
        """
        log_file = Log(
            logfile='haproxy/tests/files/average_waiting_no_wait.log',
        )
        data = log_file.cmd_average_waiting_time()
        self.assertEqual(data, 52.5)

    def test_pickle_exists(self):
        """Check that a pickle file is created after the first run."""
        filename = 'haproxy/tests/files/average_waiting_aborted.log'
        pickle_file = '{0}.pickle'.format(filename)

        # pickle files does not exist
        self.assertFalse(os.path.exists(pickle_file))

        Log(logfile=filename)
        # it does exist after parsing the file
        self.assertTrue(os.path.exists(pickle_file))

    def test_pickle_is_recreated(self):
        """Check that a pickle file is recreated if the log file is newer
        than the pickle file."""
        filename = 'haproxy/tests/files/average_waiting_aborted.log'
        pickle_file = '{0}.pickle'.format(filename)

        # create the pickle file and get its modified time
        Log(logfile=filename)
        old_pickle_time = os.path.getmtime(pickle_file)

        # any second or nth run will not change the modified time
        Log(logfile=filename)
        second_old_pickle_time = os.path.getmtime(pickle_file)
        self.assertEqual(old_pickle_time, second_old_pickle_time)

        # 'update' the original log file
        sleep(1)  # os.path.getmtime has a resolution up to seconds
        os.utime(filename, None)

        # the existing pickle file is discarded and a newer one will be created
        Log(logfile=filename)
        new_pickle_time = os.path.getmtime(pickle_file)

        self.assertTrue(new_pickle_time > old_pickle_time)
