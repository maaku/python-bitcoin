#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === bitcoin.crypto ------------------------------------------------------===
# Copyright © 2012 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
# ===----------------------------------------------------------------------===

import hashlib
from itertools import count, izip
import numbers

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from .serialize import serialize_hash, deserialize_hash

__all__ = [
    'hash256',
    'hash160',
    'merkle',
]

# ===----------------------------------------------------------------------===

def hash256(str_):
    hash_ = hashlib.sha256(hashlib.sha256(str_).digest()).digest()
    return deserialize_hash(StringIO(hash_), 32)

def hash160(str_):
    h = hashlib.new('ripemd160')
    hash_ = h.update(hashlib.sha256(str_).digest()).digest()
    return deserialize_hash(StringIO(hash_), 20)

# ===----------------------------------------------------------------------===

def merkle(hashes):
    hashes = list(hashes)
    for idx, child in filter(lambda h:not isinstance(h[1], numbers.Integral),
                             izip(count(), hashes)):
        hashes[idx] = merkle(child)
    while len(hashes) > 1:
        hashes = map(lambda h:serialize_hash(h, 32), hashes)
        hashes.append(hashes[-1])
        hashes = [hash256(l+r) for l,r in izip(*[iter(hashes)]*2)]
    return hashes and hashes[0] or 0L

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
