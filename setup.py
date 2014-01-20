#!/usr/bin/env python3

from distutils.core import setup
from __init__ import __version__

setup(name='useful',
      version=".".join(map(str,__version__)),
      author="Kandalintsev Alexandre",
      author_email='spam@messir.net',
      license="GPLv3",
      description="Modules simplifying everyday life",
      packages=['useful'],
      package_dir = {'useful': './'}
)
