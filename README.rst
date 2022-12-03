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

.. image:: https://github.com/gforcada/haproxy_log_analysis/actions/workflows/tests.yml/badge.svg?branch=master
   :target: https://github.com/gforcada/haproxy_log_analysis/actions/workflows/tests.yml

.. image:: https://coveralls.io/repos/github/gforcada/haproxy_log_analysis/badge.svg?branch=master
   :target: https://coveralls.io/github/gforcada/haproxy_log_analysis?branch=master


Documentation
-------------
See the `documentation and API`_ at ReadTheDocs_.

Command-line interface
----------------------
The current ``--help`` looks like this::

  usage: haproxy_log_analysis [-h] [-l LOG] [-s START] [-d DELTA] [-c COMMAND]
                              [-f FILTER] [-n] [--list-commands]
                              [--list-filters] [--json]

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
                          file. See --list-commands to get a full list of them.
    -f FILTER, --filter FILTER
                          List of filters to apply on the log file. Passed as
                          comma separated and parameters within square brackets,
                          e.g ip[192.168.1.1],ssl,path[/some/path]. See --list-
                          filters to get a full list of them.
    -n, --negate-filter   Make filters passed with -f work the other way around,
                          i.e. if the ``ssl`` filter is passed instead of
                          showing only ssl requests it will show non-ssl
                          traffic. If the ``ip`` filter is used, then all but
                          that ip passed to the filter will be used.
    --list-commands       Lists all commands available.
    --list-filters        Lists all filters available.
    --json                Output results in json.
    --invalid             Print the lines that could not be parsed. Be aware
                          that mixing it with the print command will mix their
                          output.


Commands
--------

Commands are small purpose specific programs in themselves that report specific statistics about the log file being analyzed.
See them all with ``--list-commands`` or online at https://haproxy-log-analyzer.readthedocs.io/modules.html#module-haproxy.commands.

- ``average_response_time``
- ``average_waiting_time``
- ``connection_type``
- ``counter``
- ``http_methods``
- ``ip_counter``
- ``print``
- ``queue_peaks``
- ``request_path_counter``
- ``requests_per_hour``
- ``requests_per_minute``
- ``server_load``
- ``slow_requests``
- ``slow_requests_counter``
- ``status_codes_counter``
- ``top_ips``
- ``top_request_paths``

Filters
-------
Filters, contrary to commands,
are a way to reduce the amount of log lines to be processed.

.. note::
   The ``-n`` command line argument allows to reverse filters output.

   This helps when looking for specific traces, like a certain IP, a path...

See them all with ``--list-filters`` or online at https://haproxy-log-analyzer.readthedocs.io/modules.html#module-haproxy.filters.

- ``backend``
- ``frontend``
- ``http_method``
- ``ip``
- ``ip_range``
- ``path``
- ``response_size``
- ``server``
- ``slow_requests``
- ``ssl``
- ``status_code``
- ``status_code_family``
- ``wait_on_queues``

Installation
------------
After installation you will have a console script `haproxy_log_analysis`::

    $ pip install haproxy_log_analysis

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
.. _HTTP log format: http://cbonte.github.io/haproxy-dconv/2.2/configuration.html#8.2.3
.. _documentation and API: https://haproxy-log-analyzer.readthedocs.io/
.. _ReadTheDocs: http://readthedocs.org
