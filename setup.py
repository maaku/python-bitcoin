#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import os

from distutils.core import setup

from bitcoin import get_version

# Compile the list of packages available, because distutils doesn't have an
# easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('bitcoin'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[len('bitcoin')+1:] # Strip "bitcoin/" or "bitcoin\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

version = get_version().replace(' ', '-')
setup(name='python-bitcoin',
    version=version,
    description=
        u"A collection of serialization and utility methods needed to "
        u"implement the bitcoin protocol.",
    author='RokuSigma Inc.',
    author_email='python-bitcoin@monetize.io',
    url='http://www.github.com/monetizeio/python-bitcoin/',
    download_url='http://pypi.python.org/packages/source/p/python-bitcoin/python-bitcoin-%s.tar.gz' % version,
    package_dir={'bitcoin': 'bitcoin'},
    packages=packages,
    package_data={'bitcoin': data_files},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

#
# End of File
#
