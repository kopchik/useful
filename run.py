from subprocess import *
import shlex

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
  run(*args, sudo='root', **kwargs)

def sudo_(*args, **kwargs):
  """The same as sudo(), but ignores exceptions"""
  run_(*args, sudo='root', **kwargs)
