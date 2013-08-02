from subprocess import *
import shlex
import os

def run(cmd, sudo=False):
  """Just runs cmd"""
  if isinstance(cmd, str):
    cmd = shlex.split(cmd)
  if sudo:
    cmd = ["sudo", "-u", sudo] + cmd
  check_call(cmd)

def run_(*args, **kwargs):
  """The same as run(), but ignores exceptions"""
  try:
    run(*args, **kwargs)
  except Exception as err:
    print("ignoring:", err)

def sudo(*args, **kwargs):
  """run cmd with sudo -u root"""
  if os.geteuid() == 0:
    run(*args, **kwargs)
  else:
    run(*args, sudo='root', **kwargs)

def sudo_(*args, **kwargs):
  """The same as sudo(), but ignores exceptions"""
  try:
    sudo(*args, **kwargs)
  except Exception as err:
    print("ignoring:", err)
