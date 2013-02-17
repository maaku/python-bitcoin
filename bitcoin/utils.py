#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

"Miscellaneous types and utility codes used in other parts of python-bitcoin."

__all__ = [
    'StringIO'
    'target_from_compact',
]

# ===----------------------------------------------------------------------===

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

# ===----------------------------------------------------------------------===

def target_from_compact(bits):
    len_ = (bits >> 24) & 0xff
    return (bits & 0xffffffL) << (8 * (len_ - 3))

#
# End of File
#
