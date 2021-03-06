#!/usr/bin/env python3

# from http://norvig.com/python-iaq.html
class Struct:
  def __init__(self, **entries):
    self.__dict__.update(entries)

  def __repr__(self):
    args = ['%s=%s' % (k, repr(v)) for (k,v) in vars(self).items()]
    return 'Struct(%s)' % ', '.join(args)

  def update(self, **entries):
    self.__dict__.update(entries)

  def __dir__(self):
    return (attr for attr in self.__dict__.keys()
            if not attr.startswith('__'))


class DefaultStruct(Struct):
  def __getattr__(self, name):
    value = DefaultStruct()
    setattr(self, name, value)
    return value

if __name__ == '__main__':
  struct = Struct(a=1, b=2)
  struct.update(c=3)
  print(struct)
