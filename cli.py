#!/usr/bin/env python3
from collections import OrderedDict
import shlex
import re

current_class = None
class NoMatch(Exception): pass

class command:
  def __init__(self, raw, help=None):
    r = []
    for tok in shlex.split(raw):
      if tok.startswith("["):
        name = tok.strip("[]")
        r += [r"(?P<%s>\w+)\s*" % name]
      else:
        r += [tok]
    self.regexp = " ".join(r)

  def __call__(self, f):
    global current_class
    if not hasattr(current_class, "__cmdmap__"):
      current_class.__cmdmap__ = OrderedDict()
    current_class.__cmdmap__[self.regexp] = f
    return f


class MetaCLI(type):
  def __init__(cls, name, bases, ns):
    global current_class
    current_class = cls


class CLI(metaclass=MetaCLI):
  """Base class for CLI interfaces"""
  def run_cmd(self, cmd):
    for r, f in self.__cmdmap__.items():
      m = re.match(r, cmd)
      if m:
        f(self, **m.groupdict())
        break
    else:
      raise NoMatch("no such command defined: %s" % cmd)


if __name__ == '__main__':
  class Example(CLI):
    @command("start [name]")
    def do_start(self, name=None):
      print("STARTED", name)

  cli = CLI()
  cli.run_cmd("start test")
