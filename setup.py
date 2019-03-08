#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

import os

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()
requires = [x for x in filter(lambda r:'libs/' not in r,
    open(os.path.join(here, 'requirements.txt')).read().split())]
packages = [x for x in filter(lambda p:not p.startswith('xunit'), find_packages())]

from bitcoin import get_version
version = get_version().replace(' ', '-')
setup(**{
    'name': 'python-bitcoin',
    'version': version,
    'description':
        u"A collection of serialization and utility methods needed to "
        u"implement the bitcoin protocol.",
    'long_description': README + '\n\n' + CHANGES,
    'author':       'Monetize.io Inc.',
    'author_email': 'python-bitcoin@monetize.io',
    'url':          'http://www.github.com/monetizeio/python-bitcoin/',
    'download_url': 'http://pypi.python.org/packages/source/p/python-bitcoin/python-bitcoin-%s.tar.gz' % version,
    'packages': packages,
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    'install_requires': requires,
})
