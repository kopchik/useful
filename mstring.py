#!/usr/bin/env python3
""" This modules uses deep python magic
    and therefore cannot be considered reliabale.
    You have been warned. 
""" 
import inspect
import re

def s(string):
  variables = re.findall("\$\{(\S+)\}", string, re.M)

  if not variables:
    return string

  f_locals = inspect.currentframe().f_back.f_locals
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


if __name__ == '__main__':
  class Generic: pass
  class Test:
    def __init__(self):
      # basic test
      x=1
      assert s("${x}") == str(x)
      y=2
      assert s("${x}/${y}") == "{x}/{y}".format(x=x,y=y)
      
      # test single-depth substitution
      self.test = 1
      assert s("${self.test}") == str(self.test)

      # test nested substitution
      self.nested = Generic()
      self.nested.test = "haba"
      assert s("${self.nested.test}") == str(self.nested.test)
  test = Test()
