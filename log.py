#!/usr/bin/env python3
from datetime import datetime
from functools import partial

import traceback
import string
import syslog
import sys

try:
    from termcolor import colored
except ImportError:
    import warnings
    warnings.warn("no termcolor module, colors not supported")
    colored = lambda text, *args, **kwargs: text

TBLIMIT = 6
KEEPALIVE = 3
nothing = lambda *x,**y: None
outputs = []


def add_output(output):
  global outputs
  outputs += [output]


class Output:
  def __init__(self, verbosity="debug", colored=True):
    self.verbosity = verbosity
    self.colored = colored

  def write(self, msg):
    print(msg, file=sys.stderr)
outputs += [Output()]


class SyslogOutput(Output):
  def __init__(self, verbosity="debug"):
    super().__init__(verbosity=verbosity, colored=False)

  def write(self, msg):
    syslog.syslog(msg)


class FileOutput(Output):
  def __init__(self, path=None, verbosity="debug"):
    assert path, "please specify path to file"
    super().__init__(verbosity=verbosity, colored=True)
    self.fd = open(path, 'a', buffering=1)

  def write(self, msg):
    self.fd.write(msg+'\n')


class Log:
  styles = {
    'debug': {},
    'info': {},
    'notice': {'color': 'green', 'attrs': ['bold']},
    'error': {'color': 'red'},
    'critical': {'color': 'red', 'attrs': ['reverse']},
  }
  priority = ['debug', 'notice', 'error', 'critical']

  def __init__(self, name, verbosity=None,
               fmt="{tstamp:%H:%M:%S} {cat} {name}: {msg}"):
    self.__verbosity = None
    self.__fmt = fmt
    self.__name = name
    self.__format = string.Formatter().format

  def set_verbosity(self, verbosity):
    assert verbosity in self.priority
    self.__verbosity = verbosity

  def log(self, msg, category=None, style=None, tb=None):
    assert category, "category argument is mandatory"
    tstamp = datetime.today()
    msg = self.__format(self.__fmt, msg=msg, cat=category,
                        tstamp=tstamp, name=self.__name)

    if tb:
      if sys.exc_info() != (None, None, None):
        tb = traceback.format_exc(TBLIMIT)
      else:
        tb = traceback.format_stack(limit=TBLIMIT)
        tb = "".join(tb)
      msg += tb

    # TODO: check channel verbosity
    for output in outputs:
      # print("printing to", output)
      if output.colored:
        output.write(colored(msg, **style))
      else:
        output.write(msg)


  def __call__(self, *args, **kwargs):
    return self.debug(*args, **kwargs)

  def __getattr__(self, category, **kwargs):
    if category in self.priority and self.__verbosity in self.priority:
      index = self.priority.index
      if index(category) < index(self.__verbosity):
        return nothing

    style = {}
    if category in self.styles:
      style = self.styles[category]

    return partial(self.log, category=category, style=style, **kwargs)


if __name__ == '__main__':
  add_output(SyslogOutput())
  log = Log("test")
  log.debug("debug")
  log.info("info")
  log.notice("notice")
  log.error("error")
  log.critical("critical")
  log.critical("test")
