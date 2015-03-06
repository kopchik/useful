import subprocess
import inspect


def dictzip(d1, d2):
  for k, v1 in d1.items():
    v2 = d2[k]
    yield (k, v1, v2)


def flatten(l):
  for e in l:
    if isinstance(e, (list, tuple)):
      yield from flatten(e)
    else:
      yield e


def readfd(fd, seek0=True, conv=float, sep=None):
  if seek0:
    fd.seek(0)
  raw = fd.read()
  return [conv(r) for r in raw.split(sep)]


def invoke(cmd, ns, **params):
  ''' Parse function arguments.
      Arguments from CMD have precedence
      over **params.
  '''
  params.update(dict(s.split('=', 1) for s in cmd.split('|')))
  assert 'func' in params, "please specify func=blah in parameters"
  funcname = params.pop('func')
  func = ns[funcname]
  # do type conversions accordin to annotations
  argspec = inspect.getfullargspec(func)
  annotations = argspec.annotations
  for name, typ in annotations.items():
    if name not in params:
      continue
    value = params[name]
    params[name] = typ(value)

  return func, params
