#!/usr/bin/env python3

from functools import total_ordering
from collections import deque
from select import select
import termios
import signal
import math
import tty
import sys
import os

from useful.timer import Timer
from useful.myenum import Enum
from blessings import Terminal

t = Terminal()

# from useful.log import Log
# log = Log("libgui")


class Range:
  def __init__(self, min, max):
    assert min <= max
    self.min = min
    self.max = max

  def __contains__(self, other):
    return self.min <= other <= self.max


def splitline(line, size):
  """ Chop line into chunks of specified size. """
  result = []
  ptr = 0
  while ptr < len(line):
    chunk = line[ptr:ptr+size]
    result.append(chunk)
    ptr += size
  return result


class Error(Exception):
  """ Generic class for all errors of this module. """


class NoSpace(Error):
  """ Not enough space to display widget. """


@total_ordering
class XY:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def __add__(self, other):
    return self.__class__(self.x + other.x,
                          self.y + other.y)

  def __sub__(self, other):
    return self.__class__(self.x - other.x,
                          self.y - other.y)

  def __gt__(self, other):
    return self.x > other.x and self.y > other.y

  def __ge__(self, other):
    return self.x >= other.x and self.y >= other.y

  def __eq__(self, other):
    if not isinstance(other, self.__class__):
      return False
    return self.x == other.x and self.y == other.y

  def __iter__(self):
    return iter([self.x, self.y])

  def __repr__(self):
    cls = self.__class__.__name__
    return "%s(%s, %s)" % (cls, self.x, self.y)


class Canvas:
  size = None
  pos  = XY(0, 0)

  def __init__(self):
    self.resize()

  def curs_set(self, lvl):
    """ Set cursor visibility. """
    # TODO
    pass

  def set_pos(self, pos=None):
    assert XY(0, 0) <= pos < self.size
    self.pos = pos
    raw = t.move(self.pos.y, self.pos.x)
    print(raw, end='')

  def resize(self):
    self.size = XY(t.width, t.height)
    return self.size

  def clear(self):
    print(t.clear)

  def printf(self, text, pos, movecur=False):
    if movecur:
        print(t.move(pos.y, pos.x), end='')
        print(str(text), end='')
    else:
      with t.location(pos.x, pos.y):
        print(str(text), end='')
    sys.stdout.flush()


fixed = 0
horiz = 1
vert = 2
both = 3


class Widget:
  pos = XY(0, 0)      # position
  size = XY(0, 0)     # actual widget size calculated in set_size
  minsize = XY(1, 1)  # minimum size for stretching widgets
  stretch = fixed     # widget size policy
  id = None           # ID that can be selected
  all_ids = []        # used for checking ID uniqueness
  focus_order = []
  parent = None       # parent widget
  cur_focus = None    # currently focused widget
  can_focus = False   # widget can receive a focus
  canvas = None       # where all widgets draw themselves
  has_focus = False

  def __init__(self, *children, **kwargs):
    self.children = list(children)
    for child in children:
      if child.id:
        if child.id in self.all_ids:
          raise Exception("duplicate ID \"%s\", "
                          "IDs must be unique" % child.id)
        self.all_ids.append(child.id)
      child.parent = self
    self.__dict__.update(kwargs)
    if self.can_focus:
      self.focus_order.append(self)
      if not Widget.cur_focus:
        Widget.cur_focus = self

  def initroot(self, canvas=None, clear=False):
    if not canvas:
      canvas = Canvas()
    if clear:
      canvas.clear()
    self.set_canvas(canvas)
    self.set_size(canvas.size)
    self.set_pos(XY(0, 0))
    self.setup_sigwinch()
    self.draw()
    if self.cur_focus:
      self.cur_focus.on_focus()

  def move_focus(self, inc=1):
    """ Switch focus to next widget. """
    idx = self.focus_order.index(self)
    idx = (idx + inc) % len(self.focus_order)
    newfocus = self.focus_order[idx]
    if newfocus != Widget.cur_focus:
      Widget.cur_focus.on_focus_loss()
      Widget.cur_focus = newfocus
      newfocus.on_focus()

  def set_size(self, maxsize):
    """ Request widget to position itself. """
    if self.minsize and self.minsize >= maxsize:
      raise NoSpace("{}: min size: {}, available: {}"
                    .format(self, self.minsize, maxsize))
    if self.stretch == both:
      self.size = maxsize
    elif self.stretch == horiz:
      self.size = XY(maxsize.x, self.minsize.y)
    elif self.stretch == vert:
      self.size = XY(self.minsize.x, maxsize.y)
    elif self.stretch == fixed:
      pass  # keep size unchanged
    else:
      raise Exception("unknown stretch policy %s" % self.stretch)
    return self.size

  def set_pos(self, pos=XY(0, 0)):
    self.pos = pos

  def set_canvas(self, canvas):
    self.canvas = canvas
    for child in self.children:
      child.set_canvas(canvas)

  def on_focus(self):
    """ Widget received focus. """
    self.has_focus = True

  def on_focus_loss(self):
    self.has_focus = False

  def draw(self):
    """ Draw widget on canvas. """
    raise NotImplementedError

  def clear(self, filler=' '):
    for y in range(self.size.y):
      pos = XY(self.pos.x, self.pos.y+y)
      self.canvas.printf(filler*self.size.x, pos)

  def input(self, key):
    if key == ARROW.UP:
      self.move_focus(-1)
    elif key in [ARROW.DOWN, '\n']:
      self.move_focus(1)

  def on_sigwinch(self, sig, frame):
    self.canvas.resize()
    self.canvas.clear()
    self.initroot(self.canvas)
    self.draw()
    if self.cur_focus:
      self.cur_focus.on_focus()

  def setup_sigwinch(self):
    # there is no old hanlder, see 'python Issue3949'
    signal.signal(signal.SIGWINCH,
                  self.on_sigwinch)

  def __getitem__(self, id):
    if self.id == id:
      return self
    for child in self.children:
      try:
        return child[id]
      except KeyError:
        pass
    raise KeyError

  def __repr__(self):
    cls = self.__class__.__name__
    id_ = self.id if self.id else id(self)
    return "<{}@{:x}>".format(cls, id_)


class VList(Widget):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def set_pos(self, pos):
    self.pos = pos
    size_y = 0
    for child in self.children:
      child_pos = XY(pos.x, pos.y+size_y)
      child.set_pos(child_pos)
      size_y += child.size.y

  def set_size(self, maxsize):
    rigid, flexible = [], []
    for child in self.children:
      if child.stretch in [fixed, horiz]:
        rigid.append(child)
      else:
        flexible.append(child)

    size_x, size_y = 0, 0
    size = XY(size_x, size_y)
    for child in rigid:
      child_maxsize = XY(maxsize.x, maxsize.y-size.y)
      child.set_size(child_maxsize)
      size_x = max(size_x, child.size.x)
      size_y += child.size.y
      size = XY(size_x, size_y)
    flex_ybudget = maxsize.y - size.y
    for child in flexible:
      child_maxsize = XY(maxsize.x, flex_ybudget//len(flexible))
      child.set_size(child_maxsize)
      size_x = max(size_x, child.size.x)
      size_y += child.size.y
      size = XY(size_x, size_y)
    self.size = size

    return self.size

  def draw(self):
    for widget in self.children:
      widget.draw()


class HList(VList):
  def set_size(self, maxsize):
    num = len(self.children)
    maxx = maxsize.x // len(self.children)
    for child in self.children:
      child_maxsize=XY(maxx, maxsize.y)
      child.set_size(child_maxsize)
    self.size = XY(maxsize.x, max(child.size.y for child in self.children))
    return self.size

  def set_pos(self, pos):
    self.pos = pos
    for i, child in enumerate(self.children):
      child_pos = XY(pos.x + self.size.x // len(self.children) * i, pos.y)
      child.set_pos(child_pos)


class String(Widget):
  def __init__(self, text="", **kwargs):
    super().__init__(**kwargs)
    self.text = text

  def update(self, newtext):
    # TODO: suboptimal code, we can clear only the rest of the string
    if len(newtext) < len(self.text):
      self.clear()
    self.text = newtext[:self.size.x]  # TODO: resize or clip with elipsis?
    self.draw()

  def draw(self):
    self.canvas.printf(self.text[:self.size.x], self.pos)


class Button(String):
  can_focus = True

  def __init__(self, text='OK!', cb=None, **kwargs):
    super().__init__(**kwargs)
    self.size = XY(len(text)+2, 1)
    self.text = text
    self.cb = cb

  def on_focus(self):
    super().on_focus()
    self.canvas.set_pos(self.pos)
    self.draw()
    self.canvas.curs_set(0)

  def on_focus_loss(self):
    super().on_focus_loss()
    self.draw()

  def on_click(self):
    if self.cb:
      self.cb()

  def input(self, key):
    if key == '\n':
      self.on_click()
    else:
      self.has_focus = False
      self.draw()
      super().input(key)

  def draw(self):
    if self.has_focus:
      text = '█%s█' % self.text
    else:
      text = ' %s ' % self.text
    self.canvas.printf(text, self.pos)


class Text(Widget):
  """ Text canvas. """
  minsize = XY(5, 5)
  stretch = both

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.lines = deque(maxlen=1000)
    self.dirty = 0  # buffer needs to be flushed
    self.timer = Timer(self.draw, None)
    self.timer.start()

  def draw(self, force=True):
    if not force:
      if not self.dirty:
        self.timer.restart(0.3)
      self.dirty += 1
      if self.dirty < 5:
        return
    self.dirty = 0
    self.timer.cancel()

    # wrap long lines
    result = []
    for line in self.lines:
      chunks = splitline(line, self.size.x)
      result.extend(chunks)
    # display only visible lines
    visible = result[-self.size.y:]
    for i, line in enumerate(visible):
      pos = self.pos + XY(0, i)
      # self.canvas.printf(" "*self.size.x, pos)
      self.canvas.printf(line, pos)
      filler = " " * (self.size.x - len(line))
      self.canvas.printf(filler, pos + XY(len(line), 0))

  def println(self, s):
    self.lines.append(str(s))
    self.draw(force=False)

  def write(self, s):
    """ This one is just to emulate file API. """
    self.println(s.strip())

  def clear(self):
    self.lines.clear()
    self.draw()


class Input(Widget):
  minsize = XY(5, 1)
  stretch = horiz
  can_focus = True

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.text = ""

  def on_focus(self):
    self.draw()

  def input(self, key):
    if key in ARROW:
      super().input(key)
    elif key == SPECIAL.BSPACE:
      if self.text:
        self.text = self.text[:-1]
        self.draw()
    elif key.isprintable():
      if len(self.text) < self.size.x:
        self.text += key
        self.draw()

  def draw(self):
    self.canvas.printf(' '*self.size.x, self.pos)
    self.canvas.printf(self.text, self.pos, movecur=True)


class CMDInput(Input):
  def __init__(self, cb=None, **kwargs):
    super().__init__(**kwargs)
    self.text = ""
    self.cb = cb

  def input(self, key):
    if key == '\n':
      if self.cb:
        self.cb(self.text)
      self.text = ''
      self.draw()
    else:
      super().input(key)


class Border(Widget):
  def __init__(self, *args, label="", **kwargs):
    super().__init__(*args, **kwargs)
    assert len(self.children) == 1,  \
        "border fits only one child"
    self.label = label
    self.stretch = self.children[0].stretch

  def set_size(self, maxsize):
    label = self.label
    child = self.children[0]
    child.set_size(maxsize-XY(2, 2))
    size_x = max(child.size.x, len(label))  # make sure label fits
    size_y = child.size.y
    self.size = XY(size_x, size_y) + XY(2, 2)  # 2x2 is a border
    return self.size

  def set_pos(self, pos):
    super().set_pos(pos)
    child = self.children[0]
    child.set_pos(pos+XY(1, 1))  # 1x1 is offset by border

  def draw(self):
    pos = self.pos
    canvas = self.canvas
    for y in [pos.y, pos.y+self.size.y-1]:
      for x in range(pos.x+1, pos.x+self.size.x-1):
        canvas.printf('─', pos=XY(x, y))

    for x in [pos.x, pos.x+self.size.x-1]:
      for y in range(pos.y+1, pos.y+self.size.y-1):
        canvas.printf('│', pos=XY(x, y))

    canvas.printf('┌', pos)
    canvas.printf('┐', pos+XY(self.size.x-1, 0))
    canvas.printf('└', pos+XY(0, self.size.y-1))
    canvas.printf('┘', pos+self.size-XY(1, 1))

    canvas.printf(self.label, pos+XY(1, 0))
    self.children[0].draw()


class Bar(Widget):
  stretch = horiz

  def __init__(self, value=0, fmt="{:.3f}", color=t.green,
               r=Range(0, 1), overflow=t.red+t.bold, **kwargs):
    super().__init__(**kwargs)
    self.fmt = fmt
    self.value = value
    self.color = color
    self.range = r
    self.overflow = overflow

  def set_size(self, maxsize):
    assert maxsize.y >= 1, "not enough screen space"
    self.size = XY(maxsize.x, 1)
    return self.size

  def update(self, value):
    self.value = value
    self.draw()

  def draw(self):
    width = self.size.x
    value = self.value
    pos_x = self.pos.x
    pos_y = self.pos.y
    r = self.range
    # length = math.ceil(width*min(1, datum/maxval))
    percent = (self.value - r.min) / (r.max - r.min)
    percent = min(percent, 1)
    percent = max(percent, 0)
    length = math.ceil(width*percent)
    s = self.fmt.format(value)
    label_len = len(s)
    # s += "█" * (length - len(s))
    s += " " * (self.size.x - len(s))
    color = self.color if value in self.range else self.overflow
    self.canvas.printf(color + t.reverse + s[:length] +
                       t.normal + s[length:], XY(pos_x, pos_y))


class Bars(Widget):
  def __init__(self, data=[0], maxval=None, showvals=True, **kwargs):
    assert isinstance(data, list)
    super().__init__(**kwargs)
    self.num = len(data)
    self.data = data
    self.maxval = maxval
    self.showvals = showvals

  def set_size(self, maxsize):
    size_x = maxsize.x
    size_y = self.num
    size = XY(size_x, size_y)
    assert size < maxsize
    self.size = size
    return self.size

  def update(self, data):
    assert isinstance(data, list)
    self.data = data
    self.draw()

  def draw(self):
    width = self.size.x
    if self.maxval:
      maxval = self.maxval
    else:
      maxval = max(self.data)
    if not maxval:
      return
    for i, datum in enumerate(self.data):
      pos_x = self.pos.x
      pos_y = self.pos.y + i
      length = math.ceil(width*min(1, datum/maxval))
      s = "{:.2f}".format(datum)
      s += "█" * (length - len(s))
      s += " " * (self.size.x - len(s))
      self.canvas.printf(t.red+t.inverse+s[:length]+t.normal+s[length:], XY(pos_x, pos_y))


SPECIAL = Enum("ESC BSPACE ENTER CTRLC".split())
ARROW = Enum("UP DOWN LEFT RIGHT".split())
# from string.printable
ascii = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!'  \
        '"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'
ASCII = Enum(ascii.split())


def myinput(timeout=None):
  stdin = sys.stdin
  special = False
  while True:
    try:
      r, _, _ = select([stdin], [], [], timeout)
      if not r:
        yield None
        continue
      ch = os.read(stdin.fileno(), 1)
    except InterruptedError:  # "[Errno 4] Interrupted system call"
      continue
    ch = ch.decode()
    if ch == '\x1b':
      if special:
        yield SPECIAL.ESC
      else:
        special = True
    elif ch == '[':
      if not special:
        yield ch
    else:
      if special:
        special = False
        if   ch == 'A': yield ARROW.UP
        elif ch == 'B': yield ARROW.DOWN
        elif ch == 'C': yield ARROW.RIGHT
        elif ch == 'D': yield ARROW.LEFT
      else:
        if   ch == '\x7f':
          yield SPECIAL.BSPACE
        elif ch == '\x03':
          os.kill(0, signal.SIGINT)
          # yield SPECIAL.CTRLC
        elif ch == '\r':
          # yield SPECIAL.ENTER
          yield '\n'
        else:
          yield ch


def mywrapper(f):
  def wrapped(*args, **kwargs):
    with t.fullscreen():
      fd = sys.stdin.fileno()
      old_settings = termios.tcgetattr(fd)
      tty.setraw(fd)
      try:
        return f()
      finally:
        termios.tcsetattr(fd, termios.TCSADRAIN,
                          old_settings)
  return wrapped


def loop(root, clear=True):
  root.initroot(clear=clear)

  for key in myinput():
    #if key == SPECIAL.CTRLC:
    #  os.kill(0, signal.SIGINT)
    #  continue
    if root.cur_focus:
      root.cur_focus.input(key)
