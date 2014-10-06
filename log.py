#!/usr/bin/env python3
from fnmatch import fnmatch
from copy import copy
import sys

try:
  from termcolor import colored
except ImportError:
  colored = lambda s, *arg, **kwargs: s

levels = ["debug", "info", "critical"]

styles = {
  'debug': {'color': 'white'},
  'info': {'color': 'green'},
  'notice': {'color': 'green', 'attrs': ['bold']},
  'error': {'color': 'red'},
  'critical': {'color': 'red', 'attrs': ['reverse']},
}


class Filter:
  def __init__(self, rules=[], default=True):
    self.rules = rules
    self.default = default

  def test(self, path):
    path = ".".join(path)
    for pattern,mode in self.rules:
      if fnmatch(path, pattern):
        return mode
    return self.default

logfilter = Filter()


class Log:
  def __init__(self, prefix=[]):
    if isinstance(prefix, str):
        prefix = prefix.split('.')
    self.prefix = prefix
    self.path = copy(self.prefix)

  def __getattr__(self, name):
    self.path.append(name)
    return self

  def __call__(self, *args, **kwargs):
    self.log(*args, **kwargs)

  def log(self, *msg):
    if logfilter.test(self.path):
      style = styles.get(self.path[-1], styles['debug'])
      msg = '.'.join(self.path)+': '+" ".join(str(m) for m in msg)
      print(colored(msg, **style), file=sys.stderr)
    self.path = copy(self.prefix)


if __name__ == '__main__':
  log = Log(["test"])
  log.test1.test2.error("haba-haba")
