# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta

import pytest


NOW = datetime.now()
TWO_DAYS_AGO = NOW - timedelta(days=2)
IN_TWO_DAYS = NOW + timedelta(days=2)


def test_default_values(line_factory, default_line_data):
    line = line_factory()

    assert line.client_ip == default_line_data['client_ip']
    assert line.client_port == default_line_data['client_port']

    assert line.raw_accept_date in default_line_data['accept_date']

    assert line.frontend_name == default_line_data['frontend_name']
    assert line.backend_name == default_line_data['backend_name']
    assert line.server_name == default_line_data['server_name']

    assert line.time_wait_request == default_line_data['tq']
    assert line.time_wait_queues == default_line_data['tw']
    assert line.time_connect_server == default_line_data['tc']
    assert line.time_wait_response == default_line_data['tr']
    assert line.total_time == default_line_data['tt']

    assert line.status_code == default_line_data['status']
    assert line.bytes_read == default_line_data['bytes']

    assert line.connections_active == default_line_data['act']
    assert line.connections_frontend == default_line_data['fe']
    assert line.connections_backend == default_line_data['be']
    assert line.connections_server == default_line_data['srv']
    assert line.retries == default_line_data['retries']

    assert line.queue_server == default_line_data['queue_server']
    assert line.queue_backend == default_line_data['queue_backend']

    assert line.captured_request_headers == default_line_data['headers'].strip()
    assert line.captured_response_headers is None

    assert line.raw_http_request == default_line_data['http_request']

    assert line.is_valid


def test_unused_values(line_factory):
    line = line_factory()
    assert line.captured_request_cookie is None
    assert line.captured_response_cookie is None
    assert line.termination_state is None


def test_datetime_value(line_factory):
    line = line_factory()
    assert isinstance(line.accept_date, datetime)


def test_http_request_values(line_factory):
    method = 'PUT'
    path = '/path/to/my/image'
    protocol = 'HTTP/2.0'
    line = line_factory(http_request=f'{method} {path} {protocol}')
    assert line.http_request_method == method
    assert line.http_request_path == path
    assert line.http_request_protocol == protocol


def test_invalid_line(line_factory):
    line = line_factory(bytes='wroooong')
    assert not line.is_valid


def test_no_captured_headers(line_factory):
    """A log line without captured headers is still valid."""
    line = line_factory(headers='')
    assert line.is_valid


def test_request_and_response_captured_headers(line_factory):
    """Request and response headers captured are parsed correctly."""
    request_headers = '{something}'
    response_headers = '{something_else}'
    line = line_factory(headers=f' {request_headers} {response_headers}')
    assert line.is_valid
    assert line.captured_request_headers == request_headers
    assert line.captured_response_headers == response_headers


def test_request_is_https_valid(line_factory):
    """Check that if a log line contains the SSL port on it, is reported
    as a https connection.
    """
    line = line_factory(http_request='GET /domain:443/to/image HTTP/1.1')
    assert line.is_https


def test_request_is_https_false(line_factory):
    """Check that if a log line does not contains the SSL port on it, is
    not reported as a https connection.
    """
    line = line_factory(http_request='GET /domain:80/to/image HTTP/1.1')
    assert not line.is_https


def test_request_is_front_page(line_factory):
    """Check that if a request is for the front page the request path is
    correctly stored.
    """
    line = line_factory(http_request='GET / HTTP/1.1')
    assert line.http_request_path == '/'


def test_strip_syslog_valid_hostname_slug(line_factory):
    """Checks that if the hostname added to syslog slug is still valid line"""
    line = line_factory(
        http_request='GET / HTTP/1.1',
        process_name_and_pid='ip-192-168-1-1 haproxy[28029]:',
    )
    assert line.is_valid


def test_unparseable_http_request(line_factory):
    line = line_factory(http_request='something')
    assert line.http_request_method == 'invalid'
    assert line.http_request_path == 'invalid'
    assert line.http_request_protocol == 'invalid'


def test_dot_on_process_name(line_factory):
    """Checks that process names can have a dot on it"""
    line = line_factory(process_name_and_pid='localhost.localdomain haproxy[2345]:')
    assert line.is_valid


def test_nixos_syslog(line_factory):
    """Check that the NixOS timestamp at the beginning can also be parsed"""
    line = line_factory(syslog_date='2017-07-06T14:29:39+02:00')
    assert line.is_valid


def test_ip_from_headers(line_factory):
    """Check that the IP from the captured headers takes precedence."""
    line = line_factory(headers=' {1.2.3.4}')
    assert line.ip == '1.2.3.4'


def test_ip_from_client_ip(line_factory):
    """Check that if there is no IP on the captured headers, the client IP is used."""
    line = line_factory(headers='', client_ip='127.1.2.7')
    assert line.ip == '127.1.2.7'


@pytest.mark.parametrize(
    'start, end, result',
    [
        (None, None, True),
        (TWO_DAYS_AGO, None, True),
        (IN_TWO_DAYS, None, False),
        (TWO_DAYS_AGO, IN_TWO_DAYS, True),
        (TWO_DAYS_AGO, TWO_DAYS_AGO, False),
    ],
)
def test_is_within_timeframe(line_factory, start, end, result):
    """Check that a line is within a given time frame."""
    line = line_factory(accept_date=NOW.strftime('%d/%b/%Y:%H:%M:%S.%f'))
    assert line.is_within_time_frame(start, end) is result
