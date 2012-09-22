#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === setup.py ------------------------------------------------------------===
# Copyright © 2012, RokuSigma Inc. and contributors as an unpublished work.
# See AUTHORS for details.
#
# RokuSigma Inc. (the “Company”) Confidential
#
# NOTICE: All information contained herein is, and remains the property of the
# Company. The intellectual and technical concepts contained herein are
# proprietary to the Company and may be covered by U.S. and Foreign Patents,
# patents in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from the
# Company. Access to the source code contained herein is hereby forbidden to
# anyone except current Company employees, managers or contractors who have
# executed Confidentiality and Non-disclosure agreements explicitly covering
# such access.
#
# The copyright notice above does not evidence any actual or intended
# publication or disclosure of this source code, which includes information
# that is confidential and/or proprietary, and is a trade secret, of the
# Company. ANY REPRODUCTION, MODIFICATION, DISTRIBUTION, PUBLIC PERFORMANCE,
# OR PUBLIC DISPLAY OF OR THROUGH USE OF THIS SOURCE CODE WITHOUT THE EXPRESS
# WRITTEN CONSENT OF THE COMPANY IS STRICTLY PROHIBITED, AND IN VIOLATION OF
# APPLICABLE LAWS AND INTERNATIONAL TREATIES. THE RECEIPT OR POSSESSION OF
# THIS SOURCE CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR IMPLY ANY
# RIGHTS TO REPRODUCE, DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE,
# USE, OR SELL ANYTHING THAT IT MAY DESCRIBE, IN WHOLE OR IN PART.
# ===----------------------------------------------------------------------===

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
  description='A collection of serialization and utility methods needed to implement the bitcoin protocol.',
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
    'License :: Other/Proprietary License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
  ],
)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
