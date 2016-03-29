.. -*- coding: utf-8 -*-

HAProxy log analyzer
====================
This Python package is a `HAProxy`_ log parser.
It analyzes HAProxy log files in multiple ways (see commands section below).

.. note::
   Currently only the `HTTP log format`_ is supported.

Tests and coverage
------------------
No project is trustworthy if does not have tests and a decent coverage!

.. image:: https://travis-ci.org/gforcada/haproxy_log_analysis.svg?branch=master
   :target: https://travis-ci.org/gforcada/haproxy_log_analysis
   :alt: Tests

.. image:: https://coveralls.io/repos/gforcada/haproxy_log_analysis/badge.svg?branch=master
   :target: https://coveralls.io/github/gforcada/haproxy_log_analysis
   :alt: Coverage

.. image:: https://img.shields.io/pypi/dm/haproxy_log_analysis.svg
   :target: https://pypi.python.org/pypi/haproxy_log_analysis/
   :alt: Downloads

.. image:: https://img.shields.io/pypi/v/haproxy_log_analysis.svg
   :target: https://pypi.python.org/pypi/haproxy_log_analysis/
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/haproxy_log_analysis.svg
   :target: https://pypi.python.org/pypi/haproxy_log_analysis/
   :alt: Egg Status

.. image:: https://img.shields.io/pypi/l/haproxy_log_analysis.svg
   :target: https://pypi.python.org/pypi/haproxy_log_analysis/
   :alt: License

Documentation
-------------
See the `documentation and API`_ at ReadTheDocs_.

Command-line interface
----------------------
The current ``--help`` looks like this::

  usage: haproxy_log_analysis [-h] [-l LOG] [-s START] [-d DELTA] [-c COMMAND]
                              [-f FILTER] [-n] [--list-commands]
                              [--list-filters]

  Analyze HAProxy log files and outputs statistics about it

  optional arguments:
    -h, --help            show this help message and exit
    -l LOG, --log LOG     HAProxy log file to analyze
    -s START, --start START
                          Process log entries starting at this time, in HAProxy
                          date format (e.g. 11/Dec/2013 or
                          11/Dec/2013:19:31:41). At least provide the
                          day/month/year. Values not specified will use their
                          base value (e.g. 00 for hour). Use in conjunction with
                          -d to limit the number of entries to process.
    -d DELTA, --delta DELTA
                          Limit the number of entries to process. Express the
                          time delta as a number and a time unit, e.g.: 1s, 10m,
                          3h or 4d (for 1 second, 10 minutes, 3 hours or 4
                          days). Use in conjunction with -s to only analyze
                          certain time delta. If no start time is given, the
                          time on the first line will be used instead.
    -c COMMAND, --command COMMAND
                          List of commands, comma separated, to run on the log
                          file. See -l to get a full list of them.
    -f FILTER, --filter FILTER
                          List of filters to apply on the log file. Passed as
                          comma separated and parameters within square brackets,
                          e.g ip[192.168.1.1],ssl,path[/some/path]. See --list-
                          filters to get a full list of them.
    -n, --negate-filter   Make filters passed with -f work the other way around,
                            i.e. ifthe ``ssl`` filter is passed instead of showing
                          only ssl requests it will show non-ssl traffic. If the
                          ``ip`` filter isused, then all but that ip passed to
                          the filter will be used.
    --list-commands       Lists all commands available.
    --list-filters        Lists all filters available.


Commands
--------

Commands are small purpose specific programs in themselves that report specific statistics about the log file being analyzed.
See the ``--help`` (or the section above) to know how to run them.

``counter``
  Reports how many log lines could be parsed.

``counter_invalid``
  Reports how many log lines could *not* be parsed.

``http_methods``
  Reports a breakdown of how many requests have been made per HTTP method
  (GET, POST...).

``ip_counter``
  Reports a breakdown of how many requests have been made per IP.
  Note that for this to work you need to configure HAProxy to capture the header that has the IP on it
  (usually the X-Forwarded-For header).
  Something like:
  ``capture request header X-Forwarded-For len 20``

``top_ips``
  Reports the 10 IPs with most requests (and the amount of requests).

``status_codes_counter``
  Reports a breakdown of how many requests per HTTP status code
  (404, 500, 200, 301..) are on the log file.

``request_path_counter``
  Reports a breakdown of how many requests per path (/rss, /, /another/path).

``top_request_paths``
  Reports the 10 paths with most requests.

``slow_requests``
  Reports a list of requests that downstream servers took more than 1 second to response.

``counter_slow_requests``
  Reports the amount of requests that downstream servers took more than 1 second to response.

``average_response_time``
  Reports the average time (in milliseconds) servers spend to answer requests.
  .. note:: Aborted requests are not considered.

``average_waiting_time``
  Reports the average time (in milliseconds) requests spend waiting on the various HAProxy queues.

``server_load``
  Reports a breakdown of how many requests were processed by each downstream server.
  Note that currently it does not take into account the backend the server is configured on.

``queue_peaks``
  Reports a list of queue peaks.
  A queue peak is defined by the biggest value on the backend queue on a series of log lines that are between log lines without being queued.

``connection_type``
  Reports on how many requests were made on SSL and how many on plain HTTP.
  This command only works if the default port for SSL (443) appears on the path.

``requests_per_minute``
  Reports on how many requests were made per minute.
  It works best when used with ``-s`` and ``-d`` command line arguments,
  as the output can be huge.

``print``
  Prints the raw lines.
  This can be useful to trim down a file (with ``-s`` and ``-d`` for example) so that later runs are faster.

Filters
-------
Filters, contrary to commands,
are a way to reduce the amount of log lines to be processed.

.. note::
   The ``-n`` command line argument allows to reverse filters output.

   This helps when looking for specific traces, like a certain IP, a path...

``ip``
  Filters log lines by the given IP.

``ip_range``
  Filters log lines by the given IP range
  (all IPs that begin with the same prefix).

``path``
  Filters log lines by the given string.

``ssl``
  Filters log lines that are from SSL connections.
  See :method::`.HaproxyLogLine.is_https` for its limitations.

``slow_requests``
  Filters log lines that take at least the given time to get answered
  (in milliseconds).

``time_frame``
  This is an implicit filter that is used when ``--start``, and optionally, ``--delta`` are used.
  Do not use this filter on the command line, use ``--start`` and ``--delta`` instead.

``status_code``
  Filters log lines that match the given HTTP status code (i.e. 404, 200...).

``status_code_family``
  Filters log lines that match the given HTTP status code family
  (i.e. 4 for all 4xx status codes, 5 for 5xx status codes...).

``http_method``
  Filters log lines by the HTTP method used (GET, POST...).

``backend``
  Filters log lines by the HAProxy backend the connection was handled with.

``frontend``
  Filters log lines by the HAProxy frontend the connection arrived from.

``server``
  Filters log lines by the downstream server that handled the connection.

``response_size``
  Filters log lines by the response size (in bytes).
  Specially useful when looking for big file downloads.

``wait_on_queues``
  Filters log lines by the amount of time the request had to wait on HAProxy queues.
  If a request waited less than the given amount of time is accepted.

Installation
------------
After installation you will have a console script `haproxy_log_analysis`::

    $ python setup.py install

TODO
----
- add more commands: *(help appreciated)*

  - reports on servers connection time
  - reports on termination state
  - reports around connections (active, frontend, backend, server)
  - *your ideas here*

- think of a way to show the commands output in a meaningful way

- be able to specify an output format. For any command that makes sense (slow
  requests for example) output the given fields for each log line (i.e.
  acceptance date, path, downstream server, load at that time...)

- *your ideas*

.. _HAProxy: http://haproxy.1wt.eu/
.. _HTTP log format: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#8.2.3
.. _documentation and API: http://haproxy-log-analyzer.readthedocs.org/en/latest/
.. _ReadTheDocs: http://readthedocs.org
