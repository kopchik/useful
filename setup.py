#!/usr/bin/env python3

from distutils.core import setup

setup(name='exeutilz',
      version='1.2',
      author="Kandalintsev Alexandre",
      author_email='spam@messir.net',
      license="GPLv3",
      description="Modules simplifying everyday life",
      packages=['useful'],
      package_dir = {'useful': './'}
)
