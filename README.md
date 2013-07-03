Useful
======

Python useful utils collection. Contains the following modules.


log
---

Simple logger where logging module is overkill.

TODO:

1. Rename Output class to Channel.
1. Check channel verbosity.


typecheck
---------

Checks if arguments match the function annotation.


resolver
--------

A simple function that just resolves domain names to ip addresses.

TODO:

1. Returns only one random record.

1. Supports only A-records for now.


tmux
----

Trivial tmux wrapper.


cli
---

Command line parser.


mlockall
--------

A mlockall/munlockall ctypes wrapper.


mystruct
--------

A structure-like class from http://norvig.com/python-iaq.html


bench
-----

Things like stop watch live there.


mypipe
------

It's an os.pipe2() that closes fds when leaving with-statement.


mstring
-------

Magic expansion of variables in strings. *Never* use this code
because it relies on inspect module that considered harmful.
