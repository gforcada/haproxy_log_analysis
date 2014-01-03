CHANGES
=======


0.0.1 (unreleased)
------------------

- Generate an api doc for ``HaproxyLogLine`` and ``HaproxyLogFile``.
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
