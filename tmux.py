#!/usr/bin/env python3
import subprocess
import shlex
import os


DEBUG = False
if DEBUG:
  from useful.log import Log, add_output, FileOutput
  add_output(FileOutput("/tmp/tmux_debug"))
  log = Log("tmux")
  log.debig("=== started ===")


def run(cmd):
  if DEBUG:
    log.debug(cmd)
  cmd = shlex.split(cmd)
  subprocess.call(cmd, close_fds=True)


def check_run(cmd):
  if DEBUG:
    log.debug(cmd)
  cmd = shlex.split(cmd)
  subprocess.check_output(cmd, close_fds=True)


class NoWindow(Exception):
  """No such window to select"""


class TMUX:
  def __init__(self, socket="default", session="default", remain_on_exit=False):
    self._prefix = "tmux -L %s " % socket
    self._session = session
    self._socket = socket

    if 'TMUX' in os.environ:
     del os.environ["TMUX"]

    try:
      check_run(self._prefix+"has-session -t {session}".format(session=session))
      if DEBUG:
        log.debug("we have session %s" % session)
    except subprocess.CalledProcessError:
      check_run(self._prefix+"new-session -s {session} -d".format(session=session))
      if remain_on_exit:
        check_run(self._prefix+"set-option -t {session} set-remain-on-exit on".format(session=session))


  def run(self, _cmd, name=None):
    cmd  = self._prefix+"neww "
    if name:
      cmd += "-n {windowname} ".format(windowname=name)
    cmd += "-t {session}: \"{cmd}\"".format(session=self._session, cmd=_cmd)
    check_run(cmd)


  #TODO: check if there is a window with this name
  def attach(self, name=None):
    if name:
      try:
        check_run(self._prefix+"selectw -t {session}:{name}".format(session=self._session,name=name))
      except subprocess.CalledProcessError:
        raise NoWindow("no such window: %s" % name)
    check_run(self._prefix+"attach -t {session}".format(session=self._session))



if __name__ == '__main__':
  tmux = TMUX(session="TEST")
  tmux.run("echo sleeping", name="sleep")
  # tmux.run("sleep 10", name="sleep")
  tmux.attach(name="sleep")
  print("test")
