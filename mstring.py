#!/usr/bin/env python3
""" This modules uses deep python magic
    and therefore cannot be considered reliabale.
    You have been warned.
"""
import inspect
import re

def s(string, lvl=1):
  variables = re.findall("\$\{([a-zA-Z_\.]+)\}", string, re.M)

  if not variables:
    return string

  frame = inspect.currentframe().f_back
  for _ in range(lvl-1):
    frame = frame.f_back
  f_locals = frame.f_locals

  for variable in variables:
    try:
        path = variable.split(".")
        value = f_locals[path.pop(0)]
        while path:
          value = getattr(value, path.pop(0))
    except KeyError:
      continue
    string = string.replace("${%s}" % variable, str(value))

  del f_locals
  return string


def s2(string, lvl=1):
  substitutions = re.findall("\{([a-zA-Z_0-9\:\.]+)\}", string, re.M)

  if not substitutions:
    return string

  frame = inspect.currentframe().f_back
  for _ in range(lvl-1):
    frame = frame.f_back
  f_locals = frame.f_locals

  for expr in substitutions:
    fmt = "{}"
    variable = expr
    if variable.find(':') != -1:
      variable, fmt = variable.split(':')
      fmt = "{:%s}" % fmt
    path = variable.split(".")
    try:
      value = f_locals[path.pop(0)]
      while path:
        value = getattr(value, path.pop(0))
    except KeyError:
      continue
    value = fmt.format(value)
    string = string.replace("{%s}" % expr, str(value))

  del f_locals
  return string


def prints(string, *args, **kwargs):
  string = s2(string, lvl=2)
  print(string, *args, **kwargs)


if __name__ == '__main__':
  class Generic: pass
  class Test:
    def __init__(self):
      s = s2

      # basic test
      x=1
      assert s("{x}") == str(x)
      y=2
      assert s("{x}/{y}") == "{x}/{y}".format(x=x,y=y)

      # test single-depth substitution
      self.test = 1
      assert s("{self.test}") == str(self.test)

      # test nested substitution
      self.nested = Generic()
      self.nested.test = "haba"
      assert s("{self.nested.test}") == self.nested.test

      # test prints
      from io import StringIO
      buf = StringIO()
      prints("{self.nested.test}", file=buf, end='')
      assert buf.getvalue() == self.nested.test
  test = Test()
