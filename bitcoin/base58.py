# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import six

__all__ = [
    'InvalidBase58Error',
    'HashCheckedData',
    'HashChecksumError',
    'VersionedPayload',
    'VersionedPayloadError',
]

from .errors import InvalidBase58Error, HashChecksumError, VersionedPayloadError
from .serialize import serialize_beint, deserialize_beint
from .tools import StringIO

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

# ===----------------------------------------------------------------------===

class HashCheckedData(six.binary_type):
    def __new__(cls, data=b'', add_hash=False, *args, **kwargs):
        # If add_hash is set then we need to create and append a checksum to
        # the data string passed in. We also do this
        if add_hash:
            checksum = hash256(data).digest()[:4]
            bytes_ = b''.join([data, checksum])
        # Otherwise we assume that the data has a checksum already, which we
        # extract out and verify.
        else:
            # Hash checksum is always 4 bytes, even for the empty string. So
            # if there's less than 4 bytes, then there's nowhere to hide the
            # checksum...
            if len(data) < 4:
                raise HashChecksumError(u"data not large enough to contain "
                    "checksum: %s" % repr(data))
            # Extract the checksum:
            data, checksum, bytes_ = data[:-4], data[-4:], data
            # Verify that the stored checksum matches the actual value:
            if checksum != hash256(data).digest()[:4]:
                raise HashChecksumError(u"checksum doesn't match: %s != %s" % (
                    hash256(data).hexdigest()[:8], checksum.encode('hex')))
        # We're little more than a wrapper around Python's native binary type.
        # Use that constructor to create the instance:
        return super(HashCheckedData, cls).__new__(cls, bytes_, *args, **kwargs)

    # Data and checksum are merely slices into the combined binary data:
    data = property(lambda self: self[:-4])
    checksum = property(lambda self: self[-4:])

# ===----------------------------------------------------------------------===

class VersionedPayload(HashCheckedData):
    """A versioned payload is a hash checked data string that is prefixed by a
    single-byte version number. It is used primarily for serializing bitcoin
    addresses and private keys into human-readible format."""
    def __new__(cls, payload=None, version=None, *args, **kwargs):
        # It is possible to explicitly create from serialized data by passing
        # a 'data' keyword argument:
        if payload is None:
            # The version is encoded as the first byte of the 'data' keyword
            # argument, so you can't specify it explicitly as well
            if version is not None:
                raise VersionedPayloadError(u"cannot specify version when "
                     u"initializing from serialized data")

            payload = super(VersionedPayload, cls).__new__(cls, *args, **kwargs)

            # A versioned payload must have a data field at least one byte in
            # length, as the first byte is the version:
            if not payload.data:
                raise VersionedPayloadError(
                    u"not enough bytes in data for version prefix")

            return payload

        if version is not None:
            # It is the typical case that if the 'version' kwarg is specified,
            # the user also would want the hash to be auto-generated as well,
            # because it is rare indeed that the caller would have attached the
            # checksum but not the prefix.
            kwargs.setdefault('add_hash', True)
            payload = b''.join([six.int2byte(version), payload])
        # Use the superclass to generate an immutable value representing the
        # generated object:
        return super(VersionedPayload, cls).__new__(cls, payload, *args, **kwargs)

    # Version and payload are extracted as slices of the checksummed data:
    version = property(lambda self: ord(self[:1]))
    payload = property(lambda self: self[1:-4])

# ===----------------------------------------------------------------------===

# Placed at the bottom of the file so as to avoid a circular import
# dependency that would otherwise occur (the Secret class within the crypto
# module derives from VersionedPayload).
from .crypto import hash256

#
# End of File
#
