======================================
 Regular Expression Crossword checker
======================================

This is a regular expression crossword checker for crosswords like the
one at
http://boingboing.net/2013/02/11/regular-expressions-crossword.html.
It includes a sample ruleset (in ``rules.json``) for that crossword.
(A sample solution is left as an exercise for the reader.)  It reports
the number of errors and highlights the rows where errors occurred, so
can be used as a helper when solving such a crossword.

Usage is pretty simple::

    regex_crossword_checker.py [<ruleset>]

The user will be prompted to enter their solution for the crossword,
one line at a time.

If no ruleset is given, it will read rules from ``rules.json`` in the
current directory.  (See `Rulesets`_ for details.)

In theory, arbitrarily large (or small) crosswords are handled.  Only
hexagonal crosswords like the one linked to are supported.

This should run on Python 2.5+ (including Py3k), although I've only
really tested it much on Python 2.7.

Rulesets
========

A ruleset is described in JSON according to the following principles:

* The ruleset is a dict that must contain either three or four keys.
  The three required keys are ``Left to right``, ``Bottom-right to
  top-left``, and ``Top-right to bottom-left``.  (There is a fair
  amount of leeway in how you choose to punctuate and capitalize those
  keys, but all the words need to be there.)  You may optionally
  include a ``Comment`` key.
* Each key must contain a list of rules for that dimension.  Every
  rule list must be the same length.
* Each regular expression is automatically anchored at the start and
  end.  You should not include ``^`` or ``$``.
* JSON treats ``\`` as an escape, so if you wish to include a
  backslash in a regular expression, you must escape it by doubling
  (``\\``).

