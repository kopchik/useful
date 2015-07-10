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


def nsplit(l, n):
  """from http://stackoverflow.com/questions/2130016/"""
  avg = len(l) / n
  out = []
  last = 0.0

  while last < len(l):
    out.append(l[int(last):int(last + avg)])
    last += avg

  return out


def invoke(cmd, ns, **params):
  ''' Parse function arguments.
      Arguments from CMD have precedence
      over **params.
  '''
  import inspect  # lazy loading
  funcname = None
  tokens = cmd.split(',')
  if tokens[0].find('=') == -1:
    funcname = tokens.pop(0)
  params.update(dict(s.split('=', 1) for s in tokens))
  if not funcname:
    assert 'func' in params, "please specify func=blah in parameters"
    funcname = params.pop('func')
  func = ns[funcname]
  # do type conversion according to func annotation
  argspec = inspect.getfullargspec(func)
  annotations = argspec.annotations
  for name, typ in annotations.items():
    if name not in params:
      continue
    value = params[name]
    params[name] = typ(value)

  return func, params


def partition(l, key):
  r = []
  idxmap = {}
  for e in l:
    k = key(e)
    if k not in idxmap:
      a = []
      r.append(a)
      idxmap[k] = a
    idxmap[k].append(e)
  return r


def partition2(l, key):
  left, right = [], []
  for e in l:
    if key(e):
      left.append(e)
    else:
      right.append(e)
  return left, right
