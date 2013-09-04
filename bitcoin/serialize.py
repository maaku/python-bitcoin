# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

"Utility functions used in implementing the block chain serialization format."

import six

from struct import pack, unpack

__all__ = [
    'SER_NETWORK',
    'SER_DISK',
    'SER_HASH',
    'serialize_varint',
    'deserialize_varint',
    'serialize_varchar',
    'deserialize_varchar',
    'serialize_beint',
    'deserialize_beint',
    'serialize_leint',
    'deserialize_leint',
    'serialize_hash',
    'deserialize_hash',
    'serialize_list',
    'deserialize_list',
]

SER_NETWORK = 1 << 0
SER_DISK    = 1 << 1
SER_HASH    = 1 << 2

def _force_read(file_, len_):
    data = file_.read(len_)
    if len(data) != len_:
        raise EOFError(u"unexpected end-of-file")
    return data

def serialize_varint(long_):
    if 0 <= long_:
        if long_ < 253:
            return chr(long_)
        elif long_ <= 0xffffL:
            return chr(253) + pack("<H", long_)
        elif long_ <= 0xffffffffL:
            return chr(254) + pack("<I", long_)
        elif long_ <= 0xffffffffffffffffL:
            return chr(255) + pack("<Q", long_)
    raise ValueError(u"out of bounds: %d" % long_)

def deserialize_varint(file_):
    result = unpack("<B", _force_read(file_, 1))[0]
    if result == 253:
        result = unpack("<H", _force_read(file_, 2))[0]
    elif result == 254:
        result = unpack("<I", _force_read(file_, 4))[0]
    elif result == 255:
        result = unpack("<Q", _force_read(file_, 8))[0]
    return result

def serialize_varchar(str_):
    return serialize_varint(len(str_)) + str_

def deserialize_varchar(file_):
    len_ = deserialize_varint(file_)
    return len_ and _force_read(file_, len_) or b''

def serialize_leint(long_, len_=None):
    if long_ < 0:
        raise ValueError(u"received integer value is negative")

    result = []
    while long_:
        result.append(pack("<Q", long_ & 0xffffffffffffffffL))
        long_ >>= 64
    result = b''.join(result)
    result = result.rstrip('\x00')

    if len_ is not None:
        result_len = len(result)
        if result_len < len_:
            result = result + b'\x00' * (len_ - result_len)
        elif result_len > len_:
            raise ValueError(u"integer value exceeds maximum representable value")

    return result

def deserialize_leint(file_, len_):
    result = 0L
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
    return result

def serialize_beint(long_, len_=None):
    return serialize_leint(long_, len_)[::-1]

def deserialize_beint(file_, len_):
    result = 0L
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
    return result

serialize_hash = serialize_leint
deserialize_hash = deserialize_leint

def serialize_list(list_, serializer=lambda i:i.serialize()):
    result = serialize_varint(len(list_))
    for item in list_:
        result += serializer(item)
    return result

def deserialize_list(file_, deserializer):
    for _ in xrange(deserialize_varint(file_)):
        yield deserializer(file_)
    raise StopIteration

#
# End of File
#
