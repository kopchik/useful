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
nothing = lambda *x,**y: None
outputs = []  # default outputs
priority = ['debug', 'info', 'notice', 'error', 'critical']

class Output:
  styles = {
    'debug': {},
    'info': {},
    'notice': {'color': 'green', 'attrs': ['bold']},
    'error': {'color': 'red'},
    'critical': {'color': 'red', 'attrs': ['reverse']},
  }

  def __init__(self, lvl=0):
    self.lvl = lvl

  def write(self, msg, lvl=0):
    if lvl >= self.lvl:
      self.writer(msg, lvl=lvl)

  def writer(self, msg, lvl=None):
    category = priority[lvl]
    style = {}
    if category in self.styles:
      style = self.styles[category]
    print(colored(msg, **style), file=sys.stderr)
outputs += [Output()]


class SyslogOutput(Output):
  def __init__(self, lvl=0):
    super().__init__(lvl=lvl)

  def writer(self, msg, lvl=None):
    syslog.syslog(msg)


class FileOutput(Output):
  def __init__(self, path=None, lvl=0):
    assert path, "please specify path to file"
    self.fd = open(path, 'a', buffering=1)
    super().__init__(lvl)

  def writer(self, msg):
    self.fd.write(msg+'\n')


class Log:
  def __init__(self, name, lvl=None,
               fmt="{tstamp:%H:%M:%S} {cat} {name}: {msg}", outputs=outputs):
    self.lvl = 0
    self.fmt = fmt
    self.name = name
    self.format = string.Formatter().format
    self.outputs = outputs

  def set_lvl(self, lvl):
    assert lvl in self.priority
    self.lvl = lvl

  def log(self, msg, *args, lvl=0, style=None, tb=None):
    if lvl < self.lvl:
      return

    # expand msg
    if args:
      try:
        msg = msg % args
      except TypeError:
        # fallback
        msg = " ".join([msg]+list(args))

    tstamp = datetime.today()
    msg = self.format(self.fmt, msg=msg, cat=priority[lvl],
                        tstamp=tstamp, name=self.name)

    if tb:
      if sys.exc_info() != (None, None, None):
        tb = traceback.format_exc(TBLIMIT)
      else:
        tb = traceback.format_stack(limit=TBLIMIT)
        tb = "".join(tb)
      msg += tb

    for output in self.outputs:
        output.write(msg, lvl=lvl)


  def __call__(self, *args, **kwargs):
    return self.debug(*args, **kwargs)


  def __getattr__(self, category, **kwargs):
    if category in priority:
      lvl = priority.index(category)
      if lvl < self.lvl:
        return nothing
    else:
      print("unknown category %s" % category, file=sys.stderr)
      lvl = 1

    return partial(self.log, lvl=lvl, **kwargs)


if __name__ == '__main__':
  outputs += [SyslogOutput()]
  log = Log("test")
  log.debug("debug")
  log.info("info")
  log.notice("notice")
  log.error("error")
  log.critical("critical")
  log.critical("test")
