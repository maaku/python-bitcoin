# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import six

from .crypto import hash256
from .errors import InvalidBase58Error, Base58ChecksumError
from .serialize import serialize_beint, deserialize_beint
from .utils import StringIO

# ===----------------------------------------------------------------------===

b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def b58_encode(b, errors='strict'):
    "Encode bytes to a base58-encoded string."
    len_ = len(b)

    # Convert big-endian bytes to integer
    n = deserialize_beint(StringIO(b), len_)

    # Divide that integer into base58
    res = []
    while n > 0:
        n, r = divmod (n, 58)
        res.append(b58_digits[r])
    res = ''.join(res[::-1])

    # Encode leading zeros as base58 zeros
    pad = 0
    for c in b:
        if c == six.int2byte(0): pad += 1
        else: break
    return (b58_digits[0] * pad + res, len_)

def b58_decode(s, errors='strict'):
    "Decode a base58-encoding string, returning bytes."
    if not s:
        return (b'', 0)

    # Convert the string to an integer
    n = 0
    for c in s:
        n *= 58
        if c not in b58_digits:
            raise InvalidBase58Error(u"character %r is not a valid base58 "
                u"character" % c)
        digit = b58_digits.index(c)
        n += digit

    # Convert the integer to bytes
    res = serialize_beint(n, (n.bit_length()+7)//8 or 1)

    # Add padding back.
    pad = 0
    for c in s[:-1]:
        if c == b58_digits[0]: pad += 1
        else: break
    return (b'\x00' * pad + res, len(s))

import codecs
try:
    codecs.lookup('base58')
except LookupError:
    def searcher(name):
        if name == 'base58':
            return codecs.CodecInfo(b58_encode, b58_decode, name=name)
        else:
            return None
    codecs.register(searcher)

#
# End of File
#
