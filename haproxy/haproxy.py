# -*- encoding: utf-8 -*-
import re


# Example log line, to understand the regex below (truncated to fit into
# 80 chars):
#
# Dec  9 13:01:26 localhost haproxy[28029]: 127.0.0.1:39759
# [09/Dec/2013:12:59:46.633] loadbalancer default/instance8
# 0/51536/1/48082/99627 200 83285 - - ---- 87/87/87/1/0 0/67
# {77.24.148.74} "GET /path/to/image HTTP/1.1"
HAPROXY_LINE_REGEX = re.compile(
    # Dec  9 13:01:26
    r'\A\w+\s+\d+\s+\d+:\d+:\d+\s+'  # syslog date, ignored
    # localhost haproxy[28029]:
    r'\w+\s+\w+\[\d+\]:\s+'  # haproxy process name and pid, ignored
    # 127.0.0.1:39759
    r'(?P<client_ip>(\d+\.){3}\d+):(?P<client_port>\d+)\s+'
    # [09/Dec/2013:12:59:46.633]
    r'\[(?P<accept_date>.*)\..*\]\s+'
    # loadbalancer default/instance8
    r'(?P<frontend_name>.*)\s+(?P<backend_name>.*)/(?P<server_name>.*)\s+'
    # 0/51536/1/48082/99627
    r'(?P<tq>-?\d+)/(?P<tw>-?\d+)/(?P<tc>-?\d+)/'
    r'(?P<tr>-?\d+)/(?P<tt>\+?\d+)\s+'
    # 200 83285
    r'(?P<status_code>\d+)\s+(?P<bytes_read>\+?\d+)\s+'
    # - - ----
    r'.*\s+'  # ignored by now, should capture cookies and termination state
    # 87/87/87/1/0
    r'(?P<act>\d+)/(?P<fe>\d+)/(?P<be>\d+)/'
    r'(?P<srv>\d+)/(?P<retries>\+?\d+)\s+'
    # 0/67
    r'(?P<queue_server>\d+)/(?P<queue_backend>\d+)\s+'
    # {77.24.148.74}
    r'((?P<request_headers>{.*})\s+(?P<response_headers>{.*})|'
    r'(?P<headers>{.*})|)\s+'
    # "GET /path/to/image HTTP/1.1"
    r'"(?P<http_request>.*)"'
    r'\Z'  # end of line
)
