#!/usr/bin/env python

from distutils.core import setup

setup(name='exeutilz',
      version='1.0', #TODO: remove dup version from __init__.py
      author="Kandalintsev Alexandre",
      author_email='spam@messir.net',
      license="GPLv3",
      description="Modules for simplifying everday life",
      packages=['useful'],
      package_dir = {'useful': './'}
)
