#!/usr/bin/env python3

import sys
import os

class MyPipe:
  """ os.pipe2() that closes fds"""
  def __init__(self, flags=0):
    self.flags = flags

  def __enter__(self):
    self.r, self.w = os.pipe2(self.flags)
    return self.r, self.w

  def __exit__(self, *args, **kwargs):
    for fd in [self.r, self.w]:
      try:
        os.close(fd)
      except OSError as err:
        print("MyPipe: cannot close fd %s:"%fd, err, file=sys.stderr)


if __name__ == '__main__':
  with MyPipe() as (r,w):
    out = os.fdopen(w, "w")
    in_ = os.fdopen(r, "r")
    print("Some data sent over pipeline", file=out, flush=True)
    print(in_.readline())
