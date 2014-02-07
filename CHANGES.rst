CHANGES
=======


0.0.1 (unreleased)
------------------

- Pickle :class:`.HaproxyLogFile` data for faster performance.
  [GF]

- Add a way to negate the filters, so that instead of being able to filter by
  IP, it can output all but that IP information.
  [GF]

- Add lots of filters: ip, path, ssl, backend, frontend, server, status_code
  and so on. See ``--list-filters`` for a complete list of them.
  [GF]

- Add :meth:`.HaproxyLogFile.parse_data` method to get data from data stream.
  It allows you use it as a library.
  [bogdangi]

- Add ``--list-filters`` argument on the command line interface.
  [GF]

- Add ``--filter`` argument on the command line interface, inspired by
  Bogdan's early design.
  [bogdangi] [GF]

- Create a new module :mod:`haproxy.filters` that holds all available filters.
  [GF]

- Improve :meth:`.HaproxyLogFile.cmd_queue_peaks` output to not only show
  peaks but also when requests started to queue and when they finsihed and
  the amount of requests that had been queued.
  [GF]

- Show help when no argument is given.
  [GF]

- Polish documentation and docstrings here and there.
  [GF]

- Add a ``--list-commands`` argument on the command line interface.
  [GF]

- Generate an API doc for ``HaproxyLogLine`` and ``HaproxyLogFile``.
  [bogdangi]

- Create a ``console_script`` `haproxy_log_analysis` for ease of use.
  [bogdangi]

- Add Sphinx documentation system, still empty.
  [GF]

- Keep valid log lines sorted so that the exact order of connections is kept.
  [GF]

- Add quite a few commands, see `README.rst`_ for a complete list of them.
  [GF]

- Run commands passed as arguments (with -c flag).
  [GF]

- Add a requirements.txt file to keep track of dependencies and pin them.
  [GF]

- Add travis_ and coveralls_ support. See its badges on `README.rst`_.
  [GF]

- Add argument parsing and custom validation logic for all arguments.
  [GF]

- Add regular expressions for haproxy log lines (HTTP format) and to
  parse HTTP requests path.
  Added tests to ensure they work as expected.
  [GF]

- Create distribution.
  [GF]

.. _travis: https://travis-ci.org/
.. _coveralls: https://coveralls.io/
.. _README.rst: http://github.com/gforcada/haproxy_log_analysis
