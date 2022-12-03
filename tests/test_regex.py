import random
from datetime import datetime

import pytest

from haproxy.line import HAPROXY_LINE_REGEX, HTTP_REQUEST_REGEX


def test_default_values(line_factory, default_line_data):
    """Check that the default line with default values is parsed."""
    line = line_factory()
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)
    assert matches.group('http_request') == default_line_data['http_request']


def test_client_ip_and_port(line_factory):
    """Check that the client IP and port are extracted correctly."""
    ip = '192.168.0.250'
    port = '34'
    line = line_factory(client_ip=ip, client_port=port)
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)

    assert matches.group('client_ip') == ip
    assert matches.group('client_port') == port


def test_accept_date(line_factory):
    """Check that the accept date is extracted correctly."""
    accept_date = datetime.now().strftime('%d/%b/%Y:%H:%M:%S.%f')
    line = line_factory(accept_date=accept_date)
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)

    assert matches.group('accept_date') == accept_date


def test_server_names(line_factory):
    """Check that the server names are extracted correctly."""
    frontend_name = 'SomeThing4'
    backend_name = 'Another1'
    server_name = 'Cloud9'
    line = line_factory(
        frontend_name=frontend_name, backend_name=backend_name, server_name=server_name
    )
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)

    assert matches.group('frontend_name') == frontend_name
    assert matches.group('backend_name') == backend_name
    assert matches.group('server_name') == server_name


@pytest.mark.parametrize(
    'tq,tw,tc,tr,tt',
    [
        ('0', '0', '0', '0', '0'),
        ('23', '55', '3', '4', '5'),
        ('-23', '-33', '-3', '-4', '5'),
        ('23', '33', '3', '4', '+5'),
    ],
)
def test_timers(line_factory, tq, tw, tc, tr, tt):
    """Check that the timers are extracted correctly.

    Note that all timers can be negative but `tt`,
    and that `tt` is the only one that can have a positive sign.
    """
    line = line_factory(tq=tq, tw=tw, tc=tc, tr=tr, tt=tt)
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)

    assert matches.group('tq') == tq
    assert matches.group('tw') == tw
    assert matches.group('tc') == tc
    assert matches.group('tr') == tr
    assert matches.group('tt') == tt


@pytest.mark.parametrize(
    'status, bytes_read', [('200', '0'), ('-301', '543'), ('200', '+543')]
)
def test_status_and_bytes(line_factory, status, bytes_read):
    """Check that the status code and bytes are extracted correctly.

    Note that `status` can be negative (for terminated requests),
    and `bytes` can be prefixed with a plus sign.
    """
    line = line_factory(status=status, bytes=bytes_read)
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)

    assert matches.group('status_code') == status
    assert matches.group('bytes_read') == bytes_read


@pytest.mark.parametrize(
    'act,fe,be,srv,retries',
    [
        ('0', '0', '0', '0', '0'),
        ('40', '10', '11', '12', '14'),
        ('40', '10', '11', '12', '+14'),
    ],
)
def test_connections_and_retries(line_factory, act, fe, be, srv, retries):
    """Check that the connections and retries are extracted correctly.

    Note that `retries` might have a plus sign prefixed.
    """
    line = line_factory(act=act, fe=fe, be=be, srv=srv, retries=retries)
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)

    assert matches.group('act') == act
    assert matches.group('fe') == fe
    assert matches.group('be') == be
    assert matches.group('srv') == srv
    assert matches.group('retries') == retries


@pytest.mark.parametrize('server, backend', [('0', '0'), ('200', '200')])
def test_queues(line_factory, server, backend):
    """Check that the server and backend queues are extracted correctly."""
    line = line_factory(queue_server=server, queue_backend=backend)
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)

    assert matches.group('queue_server') == server
    assert matches.group('queue_backend') == backend


@pytest.mark.parametrize(
    'request_header, response_header',
    [
        ('', ''),
        ('something', None),
        ('something here', 'and there'),
        ('multiple | request | headers', 'and | multiple | response ones'),
    ],
)
def test_captured_headers(line_factory, request_header, response_header):
    """Check that captured headers are extracted correctly."""
    if response_header:
        headers = f' {{{request_header}}} {{{response_header}}}'
    else:
        headers = f' {{{request_header}}}'
    line = line_factory(headers=headers)
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)

    if response_header:
        assert matches.group('request_headers') == request_header
        assert matches.group('response_headers') == response_header
    else:
        assert matches.group('headers') == request_header
        assert matches.group('request_headers') is None
        assert matches.group('response_headers') is None


def test_http_request(line_factory):
    """Check that the HTTP request is extracted correctly."""
    http_request = 'something in the air'
    line = line_factory(http_request=http_request)
    matches = HAPROXY_LINE_REGEX.match(line.raw_line)

    assert matches.group('http_request') == http_request


@pytest.mark.parametrize(
    'path',
    [
        '/path/to/image',
        '/path/with/port:80',  # with port
        '/path/with/example.com',  # with domain
        '/path/to/article#section',  # with anchor
        '/article?hello=world&goodbye=lennin',  # with parameters
        '/article-with-dashes_and_underscores',  # dashes and underscores
        '/redirect_to?http://example.com',  # double slashes
        '/@@funny',  # at sign
        '/something%20encoded',  # percent sign
        '/++adding++is+always+fun',  # plus sign
        '/here_or|here',  # vertical bar
        '/here~~~e',  # tilde sign
        '/here_*or',  # asterisk sign
        '/something;or-not',  # colon
        '/something-important!probably',  # exclamation mark
        '/something$important',  # dollar sign
        "/there's-one's-way-or-another's"  # single quote sign
        '/there?la=as,is',  # comma
        '/here_or(here)',  # parenthesis
        '/here_or[here]',  # square brackets
        '/georg}von{grote/\\',  # curly brackets
        '/here_or<',  # less than
        '/here_or>',  # more than
        '/georg-von-grote/\\',  # back slash
        '/georg`von´grote/\\',  # diacritics
        '/georg`von^grote/\\',  # caret
    ],
)
def test_http_request_regex(path):
    """Test that the method/path/protocol are extracted properly from the HTTP request."""
    verbs = ('GET', 'POST', 'DELETE', 'PATCH', 'PUT')
    protocols = (
        'HTTP/1.0',
        'HTTP/1.1',
        'HTTP/2.0',
    )
    method = random.choice(verbs)
    protocol = random.choice(protocols)
    matches = HTTP_REQUEST_REGEX.match(f'{method} {path} {protocol}')
    assert matches.group('method') == method
    assert matches.group('path') == path
    assert matches.group('protocol') == protocol
