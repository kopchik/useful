#!/usr/bin/env python3

import socket
import random
try:
  import ipaddress
except ImportError:
  try:
    import ipaddr as ipaddress
  except ImportError:
    raise Exception("You need either ipaddr or ipaddress (py3.3 included) module")


def isaddr(addr):
  try:
    return ipaddress.ip_address(addr)
  except:
    return False


def resolve(addr, v4only=False, v6only=False):
  proto = socket.SOL_TCP
  family = 0
  if isaddr(addr):
    #TODO: check if it is v4 or v6 addr
    return addr

  assert not (v4only and v6only), \
    "either v4only or v6nly"
  if v4only:
    family = socket.AF_INET
  elif v6only:
    family = socket.AF_INET6
  r = socket.getaddrinfo(addr, 6666, family=family, proto=proto)
  return random.choice(r)[4][0]


def r4(addr):
  return resolve(addr, v4only=True)


def r6(addr):
  return resolve(addr, v6only=True)

if __name__ == '__main__':
  print("IPv6 address of kliga.ru is ...", end=' ')
  try:
    print(r6("kliga.ru"))
  except socket.gaierror:
    print("cant resolve it :(")
