#!/usr/bin/env python3

class Struct:
  def __init__(self, **entries):
    self.__dict__.update(entries)

  def __repr__(self):
    args = ['%s=%s' % (k, repr(v)) for (k,v) in vars(self).items()]
    return 'Struct(%s)' % ', '.join(args)

  def update(self, **entries):
    self.__dict__.update(entries)

if __name__ == '__main__':
  struct = Struct(a=1, b=2)
  struct.update(c=3)
  print(struct)