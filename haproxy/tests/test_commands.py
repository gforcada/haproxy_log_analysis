from datetime import datetime
from datetime import timedelta
from haproxy import commands
from testfixtures import OutputCapture

import pytest


@pytest.mark.parametrize(
    'klass, expected',
    [
        (commands.StatusCodesCounter, 'status_codes_counter'),
        (commands.AverageResponseTime, 'average_response_time'),
        (commands.Counter, 'counter'),
        (commands.IpCounter, 'ip_counter'),
    ],
)
def test_print_command_name(klass, expected):
    """Check that the command line name of command classes are generated correctly."""
    assert klass.command_line_name() == expected


def test_counter():
    """Test the Counter command.

    It plain and simply counts all the lines passed to it.
    """
    cmd = commands.Counter()
    assert cmd.results() == 0
    for x in range(3):
        cmd(x)

    assert cmd.results() == 3


def test_http_methods(line_factory):
    """Test the HTTPMethods command.

    It creates a breakdown of how many times each HTTP verb has been used.
    """
    cmd = commands.HttpMethods()
    assert cmd.results() == {}
    for verb, count in (('POST', 4), ('GET', 3), ('PUT', 2)):
        line = line_factory(http_request=f'{verb} /path/to/image HTTP/1.1')
        for x in range(count):
            cmd(line)
    results = cmd.results()
    assert len(results) == 3
    assert results['POST'] == 4
    assert results['GET'] == 3
    assert results['PUT'] == 2


def test_ip_counter(line_factory):
    """Test the IpCounter command.

    It creates a breakdown of how many times each IP has been used.
    """
    cmd = commands.IpCounter()
    assert cmd.results() == {}
    for ip, count in (('192.168.0.1', 4), ('172.4.3.2', 3), ('8.7.6.5', 2)):
        line = line_factory(headers=f' {{{ip}}}')
        for x in range(count):
            cmd(line)
    results = cmd.results()
    assert len(results) == 3
    assert results['192.168.0.1'] == 4
    assert results['172.4.3.2'] == 3
    assert results['8.7.6.5'] == 2


def test_top_ips(line_factory):
    """Test the TopIps command.

    It lists the 10 most used IPs, and how much where they used.
    """
    cmd = commands.TopIps()
    assert cmd.results() == []
    for ip, count in ((f'192.168.0.{x}', x) for x in range(11)):
        line = line_factory(headers=f' {{{ip}}}')
        for x in range(count):
            cmd(line)
    results = cmd.results()
    assert len(results) == 10
    assert results[0] == ('192.168.0.10', 10)
    assert results[1] == ('192.168.0.9', 9)
    assert results[2] == ('192.168.0.8', 8)
    assert results[3] == ('192.168.0.7', 7)
    assert results[4] == ('192.168.0.6', 6)
    assert results[5] == ('192.168.0.5', 5)
    assert results[6] == ('192.168.0.4', 4)
    assert results[7] == ('192.168.0.3', 3)
    assert results[8] == ('192.168.0.2', 2)
    assert results[9] == ('192.168.0.1', 1)


def test_status_codes_counter(line_factory):
    """Test the StatusCodesCounter command.

    It creates a breakdown of which status codes have been used and how many each.
    """
    cmd = commands.StatusCodesCounter()
    assert cmd.results() == {}
    for status_code, count in (('200', 4), ('301', 3), ('500', 2)):
        line = line_factory(status=status_code)
        for x in range(count):
            cmd(line)
    results = cmd.results()
    assert len(results) == 3
    assert results['200'] == 4
    assert results['301'] == 3
    assert results['500'] == 2


def test_request_path_counter(line_factory):
    """Test the RequestPathCounter command.

    It creates a breakdown of how many times each URL path has been used.
    """
    cmd = commands.RequestPathCounter()
    assert cmd.results() == {}
    for path, count in (('/image/one', 4), ('/video/two', 3), ('/article/three', 2)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for x in range(count):
            cmd(line)
    results = cmd.results()
    assert len(results) == 3
    assert results['/image/one'] == 4
    assert results['/video/two'] == 3
    assert results['/article/three'] == 2


def test_top_request_paths(line_factory):
    """Test the TopRequestPaths command.

    It lists the 10 most used URL paths, and how much where they used.
    """
    cmd = commands.TopRequestPaths()
    assert cmd.results() == []
    for path, count in ((f'/file/{x}', x) for x in range(11)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for x in range(count):
            cmd(line)
    results = cmd.results()
    assert len(results) == 10
    assert results[0] == ('/file/10', 10)
    assert results[1] == ('/file/9', 9)
    assert results[2] == ('/file/8', 8)
    assert results[3] == ('/file/7', 7)
    assert results[4] == ('/file/6', 6)
    assert results[5] == ('/file/5', 5)
    assert results[6] == ('/file/4', 4)
    assert results[7] == ('/file/3', 3)
    assert results[8] == ('/file/2', 2)
    assert results[9] == ('/file/1', 1)


def test_slow_requests(line_factory):
    """Test the SlowRequests command.

    It lists all requests that took more than 1000 milliseconds to respond.
    """
    cmd = commands.SlowRequests()
    assert cmd.results() == []
    for total_time in (1003, 987, 456, 2013, 45000, 1000, 3200, 999):
        cmd(line_factory(tr=total_time))
    results = cmd.results()
    assert results == [1000, 1003, 2013, 3200, 45000]


def test_slow_requests_counter(line_factory):
    """Test the SlowRequestsCounter command.

    It counts how many requests took more than 1000 milliseconds to complete.
    """
    cmd = commands.SlowRequestsCounter()
    assert cmd.results() == 0
    for total_time in (1003, 987, 456, 2013, 45000, 1000, 3200, 999):
        cmd(line_factory(tr=total_time))
    results = cmd.results()
    assert results == 5


@pytest.mark.parametrize(
    'series, average',
    [
        ((1003, 987, 456, 2013, 1000, 3200, 999), 1379.71),
        ((110, -1, 110), 110),  # aborted connections are ignored
        ((45, 30, 0,), 25),  # responses that take 0 milliseconds are still counted
    ],
)
def test_average_response_time(line_factory, series, average):
    """Test the AverageResponseTime command.

    Returns the average response time of all valid requests.
    """
    cmd = commands.AverageResponseTime()
    assert cmd.results() == 0.0
    for total_time in series:
        cmd(line_factory(tr=total_time))
    results = cmd.results()
    assert results == average


@pytest.mark.parametrize(
    'series, average',
    [
        ((1003, 987, 456, 2013, 1000, 3200, 999), 1379.71),
        ((110, -1, 110), 110),  # aborted connections are ignored
        ((45, 30, 0,), 25),  # requests that do not wait at all are still counted
    ],
)
def test_average_waiting_time(line_factory, series, average):
    """Test the AverageWaitingTime command.

    Returns the average time requests had to wait to get processed.
    """
    cmd = commands.AverageWaitingTime()
    assert cmd.results() == 0.0
    for wait_time in series:
        cmd(line_factory(tw=wait_time))
    results = cmd.results()
    assert results == average


def test_server_load(line_factory):
    """Test the ServerLoad command.

    It creates a breakdown of how many requests each server processed.
    """
    cmd = commands.ServerLoad()
    assert cmd.results() == {}
    for name, count in (('server4', 4), ('server3', 3), ('server5', 5)):
        line = line_factory(server_name=name)
        for x in range(count):
            cmd(line)
    results = cmd.results()
    assert len(results) == 3
    assert results['server5'] == 5
    assert results['server4'] == 4
    assert results['server3'] == 3


def test_queue_peaks_no_lines(line_factory):
    """Test the QueuePeaks command.

    If there are no log lines processed, nothing should be returned.
    """
    cmd = commands.QueuePeaks()
    assert cmd.results() == []


def test_queue_peaks_no_queues(line_factory):
    """Test the QueuePeaks command.

    If there are no log lines processed, nothing should be returned.
    """
    cmd = commands.QueuePeaks()
    now = datetime.now()
    for second in range(4):
        accept_date = now.replace(second=second).strftime('%d/%b/%Y:%H:%M:%S.%f')
        cmd(line_factory(queue_backend=0, accept_date=accept_date))
    assert len(cmd.requests) == 4
    assert cmd.results() == []


@pytest.mark.parametrize(
    'date,expected_key',
    [
        ('10/Dec/2019:15:40:12.12345', 1575988812.12345),
        ('15/Jan/2017:05:23:05.456', 1484454185.456),
        ('15/Jan/2017:05:23:05.0', 1484454185.0),
    ],
)
def test_queue_peaks_generated_keys(line_factory, date, expected_key):
    """Test the QueuePeaks command.

    Check how the keys for the requests dictionary are generated.
    """
    cmd = commands.QueuePeaks()
    cmd(line_factory(queue_backend=0, accept_date=date))
    keys = list(cmd.requests.keys())
    assert keys[0] == expected_key


def test_queue_peaks_details(line_factory):
    """Test the QueuePeaks command.

    Check the information returned for each peak.
    """
    cmd = commands.QueuePeaks()
    for microseconds, queue in enumerate([0, 4, 7, 8, 19, 4, 0]):
        line = line_factory(
            queue_backend=queue, accept_date=f'15/Jan/2017:05:23:05.{microseconds}'
        )
        cmd(line)
    day = datetime(year=2017, month=1, day=15, hour=5, minute=23, second=5)
    results = cmd.results()
    assert len(results) == 1
    peak_info = results[0]
    assert peak_info['peak'] == 19
    assert peak_info['span'] == 5
    assert peak_info['first'] == day.replace(microsecond=100000)
    assert peak_info['last'] == day.replace(microsecond=600000)


def test_queue_peaks_multiple_sorted(line_factory):
    """Test the QueuePeaks command.

    Peaks information are returned sorted by date.
    """
    cmd = commands.QueuePeaks()
    for microseconds, queue in enumerate([0, 4, 0, 0, 19, 4, 0]):
        line = line_factory(
            queue_backend=queue, accept_date=f'15/Jan/2017:05:23:05.{microseconds}'
        )
        cmd(line)
    day = datetime(year=2017, month=1, day=15, hour=5, minute=23, second=5)
    results = cmd.results()
    assert len(results) == 2
    assert results[0]['peak'] == 4
    assert results[0]['first'] == day.replace(microsecond=100000)
    assert results[1]['peak'] == 19
    assert results[1]['first'] == day.replace(microsecond=400000)


def test_queue_peaks_already_started(line_factory):
    """Test the QueuePeaks command.

    Check that QueuePeaks handles the corner case of a peak that has already started.
    """
    cmd = commands.QueuePeaks()
    for microseconds, queue in enumerate([4, 19, 0]):
        line = line_factory(
            queue_backend=queue, accept_date=f'15/Jan/2017:05:23:05.{microseconds}'
        )
        cmd(line)
    day = datetime(year=2017, month=1, day=15, hour=5, minute=23, second=5)
    results = cmd.results()
    assert len(results) == 1
    peak_info = results[0]
    assert peak_info['peak'] == 19
    assert peak_info['span'] == 2
    assert peak_info['first'] == day
    assert peak_info['last'] == day.replace(microsecond=200000)


def test_queue_peaks_did_not_finish(line_factory):
    """Test the QueuePeaks command.

    Check that QueuePeaks handles the corner case of a peak that does not finish.
    """
    cmd = commands.QueuePeaks()
    for microseconds, queue in enumerate([4, 19, 12]):
        line = line_factory(
            queue_backend=queue, accept_date=f'15/Jan/2017:05:23:05.{microseconds}'
        )
        cmd(line)
    day = datetime(year=2017, month=1, day=15, hour=5, minute=23, second=5)
    results = cmd.results()
    assert len(results) == 1
    peak_info = results[0]
    assert peak_info['peak'] == 19
    assert peak_info['span'] == 3
    assert peak_info['first'] == day
    assert peak_info['last'] == day.replace(microsecond=200000)


def test_connection_type(line_factory):
    """Test the ConnectionType command.

    It counts how many requests have been made by SSL, and which ones not.
    """
    cmd = commands.ConnectionType()
    assert cmd.results() == (0, 0)
    for path, count in (('/Virtual:443/something', 4), ('/something', 2)):
        line = line_factory(http_request=f'GET {path} HTTP/1.1')
        for x in range(count):
            cmd(line)
    assert cmd.results() == (4, 2)


def test_requests_per_minute(line_factory):
    """Test the RequestsPerMinute command.

    It counts how many requests have been made per minute.
    """
    cmd = commands.RequestsPerMinute()
    assert cmd.results() == []
    now = datetime.now()
    # to avoid leaping into the next/previous minute with the timedeltas below
    now = now.replace(second=30)
    microseconds = timedelta(microseconds=200)
    seconds = timedelta(seconds=5)
    minutes = timedelta(minutes=5)
    hours = timedelta(hours=2)
    dates = [
        now,
        now + microseconds,
        now - microseconds,
        now + seconds,
        now - seconds,
        now + minutes,
        now - minutes,
        now + hours,
        now - hours,
    ]
    for time in dates:
        cmd(line_factory(accept_date=f'{time:%d/%b/%Y:%H:%M:%S.%f}'))
    results = cmd.results()
    assert len(results) == 5
    assert results[0][1] == 1
    assert results[1][1] == 1
    assert results[2][1] == 5  # now and the +- microseconds and +- seconds
    assert results[3][1] == 1
    assert results[4][1] == 1


def test_print(line_factory):
    """Test the Print command.

    It simply prints the verbatim line.
    """
    cmd = commands.Print()
    assert cmd.results() is None
    with OutputCapture() as output:
        for path in ('/first-thing-to-do', '/second/thing/to-do'):
            cmd(line_factory(http_request=f'GET {path} HTTP/1.1'))
    assert cmd.results() is None
    lines = output.captured.split('\n')
    assert len(lines) == 3
    assert '/first-thing-to-do' in lines[0]
    assert '/second/thing/to-do' in lines[1]
    assert lines[2] == ''
