#!/usr/bin/env python3

from distutils.core import setup

setup(name='useful',
      version='1.3',
      author="Kandalintsev Alexandre",
      author_email='spam@messir.net',
      license="GPLv3",
      description="Modules simplifying everyday life",
      packages=['useful'],
      package_dir = {'useful': './'}
)
