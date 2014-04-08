#!/usr/bin/env python3

class Reader:
  def __init__(self, data, sep=',', type=None):
    self.sep = sep
    self.data = iter(data)
    self.type = type

  def __iter__(self):
    return self

  def __next__(self):
    raw = ''
    while not raw or raw.startswith('#'):  # skip comments
      raw = next(self.data).strip()
    data = raw.split(self.sep)
    if not self.type:
      return data
    assert len(self.type) == len(data), \
      "number of columns doesn't match self.type"
    return [func(datum) for func, datum in zip(self.type, data)]


if __name__ == '__main__':
  data = \
"""
test1,1
test2,2
"""
  reader = Reader(data.splitlines(), type=(str,int))
  for d in reader:
    print(d)
