HAProxy log analyzer
====================

This Python package is a `HAProxy`_ log parser that allows you to analyze
your HAProxy log files in multiple ways (see commands section below).

.. note::
   Currently only the `HTTP log format`_ is supported.


Tests and coverage
------------------

No project is trustworthy if does not have tests and a decent coverage!

.. image:: https://travis-ci.org/gforcada/haproxy_log_analysis.png?branch=master
    :target: https://travis-ci.org/gforcada/haproxy_log_analysis

.. image:: https://coveralls.io/repos/gforcada/haproxy_log_analysis/badge.png?branch=master
    :target: https://coveralls.io/r/gforcada/haproxy_log_analysis


Command-line interface
----------------------

The current ``--help`` looks like this::

  usage: main.py [-h] [-s START] [-d DELTA] -c COMMAND filename

  Analyze HAProxy log files and outputs statistics about it

  positional arguments:
    filename              Haproxy log file to analyze

  optional arguments:
    -h, --help            show this help message and exit
    -s START, --start START
                          Process log entries starting at this time, in haproxy
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
                          file. Commands available: counter (count how many
                          entries are on the log file)


Commands
--------

The idea here is that you can issue any number of these commands (see the
command-line interface section above) to the haproxy log file being analyzed.

``counter``
  Reports who many log lines could be parsed.

``counter_invalid``
  Reports who many log lines could *not* be parsed.

``http_methods``
  Reports a breakdown of how many requests have been made per HTTP method
  (GET, POST...)

``ip_counter``
  Reports a breakdown of how many requests have been made per IP. Note that
  for this to work you need to configure HAProxy to capture the header that
  has the ip on it (usually the X-Forwarded-For header). Something like:
  ``capture request header X-Forwarded-For len 20``

``top_ips``
  Reports the 10 IPs with most requests (and the amount of requests).

``status_codes_counter``
  Reports a breakdown of how many requests per HTTP status code (404, 500,
  200, 301..) are on the log file.

``request_path_counter``
  Reports a breakdown of how many requests per path (/rss, /, /another/path).

``top_request_paths``
  Reports the 10 paths with most requests.

``slow_requests``
  Reports a list of requests that downstream servers took more than 1 second
  to response.

``server_load``
  Reports a breakdown of how many requests were processed by each downstream
  server. Note that currently it does not take into account the backend the
  server is configured on.

``queue_peaks``
  Reports a list of queue peaks. A queue peak is defined by the biggest
  value on the backend queue on a series of log lines that are between log
  lines without being queued.

``connection_type``
  Reports on how many requests were made on SSL and how many on plain HTTP.
  This command only works if the default port for SSL (443) appears on the
  path.

``requests_per_minute``
  Reports on how many requests were made per minute. It works best when used
  with ``-s``and ``-d`` command line arguments, as the output can be huge.


TODO
----

- add more commands: *(help appreciated)*

  - reports on slow connections
  - reports on servers connection time
  - reports on termination state
  - reports around connections (active, frontend, backend, server)
  - *your ideas here*

- add a way to chain commands (paths of slow requests, status codes and IPs,
  ...)

- think of a way to show the commands output in a meaningful way

- be able to specify an output format. For any command that makes sense (slow
  requests for example) output the given fields for each log line (i.e.
  acceptance date, path, downstream server, load at that time...)

- generate an api doc for ``HaproxyLogFile``

- create a ``console_script`` for ease of use, see `Setuptools console script`_

- *your ideas*


.. _HAProxy: http://haproxy.1wt.eu/
.. _HTTP log format: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#8.2.3
.. _Setuptools console script: http://pythonhosted.org/setuptools/setuptools.html
