# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"Utility functions used in implementing the block chain serialization format."

import six
from struct import pack, unpack

__all__ = [
    'SER_NETWORK',
    'SER_DISK',
    'SER_HASH',
    'CompactSize',
    'BigInteger',
    'LittleInteger',
    'BigNum',
    'VarInt',
    'FlatData',
    'serialize_iterator',
    'deserialize_iterator',
]

SER_NETWORK = 1 << 0
SER_DISK    = 1 << 1
SER_HASH    = 1 << 2

def _force_read(file_, len_):
    data = file_.read(len_)
    if len(data) != len_:
        raise EOFError(u"unexpected end-of-file")
    return data

class CompactSize(long):
    """\
    Compact size
      size <  253        -- 1 byte
      size <= USHRT_MAX  -- 3 bytes  (253 + 2 bytes)
      size <= UINT_MAX   -- 5 bytes  (254 + 4 bytes)
      size >  UINT_MAX   -- 9 bytes  (255 + 8 bytes)"""
    def serialize(self):
        if 0 <= self:
            if self < 253:
                return chr(self)
            elif self <= 0xffff:
                return '\xfd' + pack("<H", self)
            elif self <= 0xffffffff:
                return '\xfe' + pack("<I", self)
            elif self <= 0xffffffffffffffff:
                return '\xff' + pack("<Q", self)
        raise ValueError(u"out of bounds: %d" % self)

    @classmethod
    def deserialize(cls, file_):
        result = unpack("<B", _force_read(file_, 1))[0]
        if result == 253:
            result = unpack("<H", _force_read(file_, 2))[0]
        elif result == 254:
            result = unpack("<I", _force_read(file_, 4))[0]
        elif result == 255:
            result = unpack("<Q", _force_read(file_, 8))[0]
        return cls(result)

class LittleInteger(long):
    "Little-endian serialized integer representation."
    def serialize(self, len_=None):
        if self < 0:
            raise ValueError(u"received integer value is negative")

        result = []
        while self:
            result.append(pack("<Q", self & 0xffffffffffffffffL))
            self >>= 64
        result = b''.join(result)
        result = result.rstrip('\x00')

        if len_ > 0:
            result_len = len(result)
            if result_len < len_:
                result = result + b'\x00' * (len_ - result_len)
            elif result_len > len_:
                raise ValueError(u"integer exceeds maximum representable value")

        return result

    @classmethod
    def deserialize(cls, file_, len_):
        result = 0
        for idx in xrange(len_//8):
            limb = unpack("<Q", _force_read(file_, 8))[0]
            result += limb << (idx * 64)
        if len_ & 4:
            limb = unpack("<I", _force_read(file_, 4))[0]
            result += limb << ((len_ & ~7) * 8)
        if len_ & 2:
            limb = unpack("<H", _force_read(file_, 2))[0]
            result += limb << ((len_ & ~3) * 8)
        if len_ & 1:
            limb = unpack("<B", _force_read(file_, 1))[0]
            result += limb << ((len_ & ~1) * 8)
        return cls(result)

class BigInteger(long):
    "Big-endian serialized integer representation."
    def serialize(self, *args, **kwargs):
        return LittleInteger(self).serialize(*args, **kwargs)[::-1]

    @classmethod
    def deserialize(cls, file_, len_):
        result = 0
        for idx in xrange(len_//8):
            limb = unpack(">Q", _force_read(file_, 8))[0]
            result = (result << 64) + limb
        if len_ & 4:
            limb = unpack(">I", _force_read(file_, 4))[0]
            result = (result << 32) + limb
        if len_ & 2:
            limb = unpack(">H", _force_read(file_, 2))[0]
            result = (result << 16) + limb
        if len_ & 1:
            limb = unpack(">B", _force_read(file_, 1))[0]
            result = (result << 8) + limb
        return cls(result)

class BigNum(long):
    def serialize(self, *args, **kwargs):
        neg = self < 0
        bytes_ = BigInteger(self).serialize(*args, **kwargs)
        if not bytes_ or bytes_[:1] > six.int2byte(0x7f):
            bytes_ = six.int2byte(0) + bytes_
        if neg:
            bytes_ = b''.join([six.int2byte(ord(bytes_[:1])|0x80), bytes_[1:]])
        return bytes_

    @classmethod
    def deserialize(cls, file_, len_, *args, **kwargs):
        n = BigInteger.deserialize(file_, len_, *args, **kwargs)
        e = 2**(len_*8 - 1)
        if n >= e:
            n = e - n
        return cls(n)

# FIXME: VarInt and CompactSize are two totally different types!! This is just
# temporary code that should be removed ASAP, as soon as the unit tests are
# re-written to use the actual VarInt format.
class VarInt(CompactSize):
    pass

class FlatData(six.binary_type):
    "Wrapper for serializing arrays and POD."
    def serialize(self):
        return self

    @classmethod
    def deserialize(cls, file_, len_):
        return len_ and _force_read(file_, len_) or b''

def serialize_iterator(iter_, serializer=lambda i:i.serialize(),
        prefix = lambda n:CompactSize(n).serialize(), *args, **kwargs):
    len_, result = 0, b''
    for item in iter_:
        result += serializer(item, *args, **kwargs); len_ += 1
    return prefix(len_) + result

def deserialize_iterator(file_, deserializer, prefix=CompactSize.deserialize, *args, **kwargs):
    for _ in xrange(prefix(file_)):
        yield deserializer(file_, *args, **kwargs)
    raise StopIteration
