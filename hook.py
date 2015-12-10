#!/usr/bin/env python3
from .log import Log
from collections import defaultdict


class Hook:
  """ Simple callback dispatcher. """
  def __init__(self):
    self.cb_map = defaultdict(list)
    self.log = Log("hook")

  def decor(self, event):
    def wrap(cb):
      self.register(event, cb)
      return cb
    return wrap
  __call__ = decor

  def register(self, event, cb):
    self.cb_map[event].append(cb)

  def has_hook(self, event):
    return event in self.cb_map

  def fire(self, event, *args, **kwargs):
    if event not in self.cb_map:
       self.log.notice("no handler for {}".format(event))
       return

    handlers = self.cb_map[event]
    for handler in handlers:
      try:
        handler(event, *args, **kwargs)
      # except SupressEvent:
        # break
      except Exception as err:
        msg="error on event {ev}: {err} ({typ}) (in {hdl})" \
                .format(err=err, typ=type(err), ev=event, hdl=handler)
        self.log.error(msg)


