#!/usr/bin/env python3
from fnmatch import fnmatch
from copy import copy
import time
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
  file = sys.stderr
  def __init__(self, prefix=[], file=None):
    if isinstance(prefix, str):
        prefix = prefix.split('.')
    self.prefix = prefix
    self.path = copy(self.prefix)
    if file:
      self.file = file

  def __getattr__(self, name):
    self.path.append(name)
    return self

  def __call__(self, *args, **kwargs):
    self.log(*args, **kwargs)

  def log(self, *msg):
    if logfilter.test(self.path):
      path = '.'.join(self.path)
      msg = " ".join(str(m) for m in msg)
      ts  = time.strftime("%Y/%m/%d %H:%M:%S ")
      msg = ts + path + ': ' + msg
      if self.file == sys.stderr:
        style = styles.get(self.path[-1], styles['debug'])
        print(colored(msg, **style), file=self.file)
      else:
        print(msg, file=self.file)
    self.path = copy(self.prefix)


if __name__ == '__main__':
  log = Log(["test"])
  log.test1.test2.error("haba-haba")
