#!/usr/bin/env python3
from itertools import chain
import inspect
import sys


def assert_isinstance(v, expected):
  if not isinstance(v, expected):
    actual = type(v)
    raise AssertionError(
      "Expected type {expected}, got {actual}".format(**locals()))


#TODO: check return value
def type_check(f):
  try:
    argspec = inspect.getfullargspec(f)
  except TypeError:
    # print("cannot inspect", f)
    return f
  annotations = argspec.annotations
  if not annotations:
    return f
  names = argspec.args
  def wrapper(*vs, **kvs):
    for name, v in chain(zip(names, vs), kvs.items()):
      typ = annotations.get(name, object)
      assert_isinstance(v, typ)

    r = f(*vs, **kvs)
    typ = annotations.get('return', object)
    assert_isinstance(r, typ)
    return r

  return wrapper


if not __debug__:
  print("notice: type checking disabled", file=sys.stderr)
  type_check = lambda f: f


class TypeCheck(type):
    def __new__(self, name, bases, ns):
        new_ns = {}
        for attr, value in ns.items():
            if callable(value):
              new_ns[attr] = type_check(value)
            else:
              new_ns[attr] = value
        return type.__new__(self, name, bases, new_ns)


if __name__ == '__main__':
  @type_check
  def test(name:str, greeting:str="Hello,"):
    print(greeting, name)

  test("Exe", greeting="Go to hell,")
