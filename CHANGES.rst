CHANGES
=======


0.0.1 (unreleased)
------------------

- Create distribution
  [GF]

- Add regular expressions for haproxy log lines (HTTP format) and to
  parse HTTP requests path.
  Both have quite a few tests to ensure they work as expected.
  [GF]

- Add argument parsing and custom validation logic for all arguments.
  [GF]

- Add travis support.
  [GF]

- Add coveralls support.
  [GF]

- Add a requirements.txt file to keep track of dependencies and pin them.
  [GF]

- Run commands passed as arguments (with -c flag).
  [GF]

- Add two commands: counter and counter_invalid.
  [GF]

- Make sure that the, optional with -s and -d, time range is taken into
  account when processing the log file.
  [GF]

- Keep valid log lines sorted so that the exact order of connections is kept.
  [GF]
