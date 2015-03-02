#!/usr/bin/env python3
class Enum:
  def __init__(self, members):
    self.members = members
    for member in members:
      setattr(self, member, member)
  def __contains__(self, other):
    if other in self.members:
      return True
    for member in self.members:
      if isinstance(member, Enum) and other in member:
        return True
    return False

if __name__ == '__main__':
  SPECIAL = Enum("ESC BSPACE".split())
  assert SPECIAL.ESC in SPECIAL
