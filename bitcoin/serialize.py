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
    'BigCompactSize',
    'LittleCompactSize',
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

class _BaseCompactSize(int):
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
                return '\xfd' + pack(self.SHORT_FMT, self)
            elif self <= 0xffffffff:
                return '\xfe' + pack(self.INT_FMT, self)
            elif self <= 0xffffffffffffffff:
                return '\xff' + pack(self.LONG_FMT, self)
        raise ValueError(u"out of bounds: %d" % self)

    @classmethod
    def deserialize(cls, file_):
        result = unpack("<B", _force_read(file_, 1))[0]
        if result == 253:
            result = unpack(cls.SHORT_FMT, _force_read(file_, 2))[0]
        elif result == 254:
            result = unpack(cls.INT_FMT, _force_read(file_, 4))[0]
        elif result == 255:
            result = unpack(cls.LONG_FMT, _force_read(file_, 8))[0]
        return cls(result)

class BigCompactSize(_BaseCompactSize):
    SHORT_FMT = ">H"
    INT_FMT   = ">I"
    LONG_FMT  = ">Q"

class LittleCompactSize(_BaseCompactSize):
    SHORT_FMT = "<H"
    INT_FMT   = "<I"
    LONG_FMT  = "<Q"

class LittleInteger(int):
    "Little-endian serialized integer representation."
    def serialize(self, len_=None):
        if self < 0:
            raise ValueError(u"received integer value is negative")

        result = []
        while self:
            result.append(pack("<Q", self & 0xffffffffffffffff))
            self >>= 64
        result = b''.join(result)
        result = result.rstrip(b'\x00')

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
        for idx in range(len_//8):
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

class BigInteger(int):
    "Big-endian serialized integer representation."
    def serialize(self, *args, **kwargs):
        return LittleInteger(self).serialize(*args, **kwargs)[::-1]

    @classmethod
    def deserialize(cls, file_, len_):
        result = 0
        for idx in range(len_//8):
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

class BigNum(int):
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

class VarInt(int):
    def serialize(self):
        if not self:
            return six.int2byte(0)
        parts = list()
        while self:
            parts.append(six.int2byte((self&0x7f) | (parts and 0x80 or 0x00)))
            if self <= 0x7f:
                break
            self >>= 7
            self  -= 1
        return b''.join(reversed(parts))

    @classmethod
    def deserialize(cls, file_):
        result = 0
        while True:
            limb = unpack(">B", _force_read(file_, 1))[0]
            result <<= 7
            result  |= limb & 0x7f
            if limb & 0x80:
                result += 1
            else:
                break
        return result

class FlatData(six.binary_type):
    "Wrapper for serializing arrays and POD."
    def serialize(self):
        return self

    @classmethod
    def deserialize(cls, file_, len_):
        return len_ and _force_read(file_, len_) or b''

def serialize_iterator(iter_, serializer=lambda i:i.serialize(),
        prefix = lambda n:LittleCompactSize(n).serialize(), *args, **kwargs):
    len_, result = 0, b''
    for item in iter_:
        result += serializer(item, *args, **kwargs); len_ += 1
    return prefix(len_) + result

def deserialize_iterator(file_, deserializer, prefix=LittleCompactSize.deserialize, *args, **kwargs):
    for _ in range(prefix(file_)):
        yield deserializer(file_, *args, **kwargs)
    raise StopIteration

# End of File
