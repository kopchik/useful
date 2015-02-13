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

  def reset(self):
    os.write(self.write_fd, b'r')

  def cancel(self):
    os.write(self.write_fd, b'c')

  def run(self):
    while True:
      ready_fds = select.select([self.read_fd], [], [],
                                self.timeout)
      print(ready_fds[0])
      if self.read_fd in ready_fds[0]:
        mode = os.read(self.read_fd, 1)
        if mode == b'r':
          # print("timer was reset")
          continue
        elif mode == b'c':
          # print("timer canceled")
          break
        else:
          raise Exception("unknown mode %s" % mode)
      try:
        self.cb()
      except Exception as err:
        print("error from cb (ignored): %s" % err, file=sys.stderr)
