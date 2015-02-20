#!/usr/bin/env python3
from threading import Thread
import select
import sys
import os


class Timer(Thread):
  def __init__(self, cb, timeout):
    super().__init__(daemon=True)
    self.cb = cb
    self.timeout = timeout
    read_fd, write_fd = os.pipe()
    self.read_fd = read_fd
    self.write_fd = write_fd

  def restart(self, timeout=None):
    """ Restart timer. """
    if timeout:
      self.timeout = timeout
    os.write(self.write_fd, b'r')

  def cancel(self):
    """ Canceled, no events will fire until restarted. """
    os.write(self.write_fd, b'c')

  def abort(self):
    """ Stop timer completely, timer thread will quit. """
    os.write(self.write_fd, b'a')

  def run(self):
    while True:
      ready_fds = select.select([self.read_fd], [], [],
                                self.timeout)
      if self.read_fd in ready_fds[0]:
        mode = os.read(self.read_fd, 1)
        if mode == b'r':    # restart
          continue
        elif mode == b'c':  # cancel pending events
          self.timeout = None
          continue
        elif mode == b'a':  # abort
          break
        else:
          raise Exception("unknown mode %s" % mode)
      try:
        self.cb()
      except Exception as err:
        print("error from cb (ignored): %s" % err, file=sys.stderr)
