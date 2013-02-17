#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

"Utility functions used in implementing the block chain serialization format."

from struct import pack, unpack

__all__ = [
    'serialize_varint',
    'deserialize_varint',
    'serialize_varchar',
    'deserialize_varchar',
    'serialize_hash',
    'deserialize_hash',
    'serialize_list',
    'deserialize_list',
]

def serialize_varint(long_):
    if long_ < 253:
        return chr(long_)
    elif long_ <= 0xffffL:
        return chr(253) + pack("<H", long_)
    elif long_ <= 0xffffffffL:
        return chr(254) + pack("<I", long_)
    return chr(255) + pack("<Q", long_)

def deserialize_varint(file_):
    result = unpack("<B", file_.read(1))[0]
    if result == 253:
        result = unpack("<H", file_.read(2))[0]
    elif result == 254:
        result = unpack("<I", file_.read(4))[0]
    elif result == 255:
        result = unpack("<Q", file_.read(8))[0]
    return result

def serialize_varchar(str_):
    return serialize_varint(len(str_)) + str_

def deserialize_varchar(file_):
    len_ = deserialize_varint(file_)
    result = len_ and file_.read(len_) or ''
    if len_ != len(result):
        raise ValueError('unexpected end-of-file in varchar serialization')
    return result

def serialize_hash(long_, len_):
    if long_ < 0:
        raise ValueError(u"received hash value is negative")
    result = ''
    for _ in xrange(len_//8):
        result += pack("<Q", long_ & 0xffffffffffffffffL)
        long_ >>= 64
    if len_ & 4:
        result += pack("<I", long_ & 0xffffffffL)
        long_ >>= 32
    if len_ & 2:
        result += pack("<H", long_ & 0xffffL)
        long_ >>= 16
    if len_ & 1:
        result += pack("<B", long_ & 0xffL)
        long_ >>= 8
    if long_:
        raise ValueError(u"hash value exceeds maximum representable value")
    return result

def deserialize_hash(file_, len_):
    result = 0L
    for idx in xrange(len_//8):
        limb = unpack("<Q", file_.read(8))[0]
        result += limb << (idx * 64)
    if len_ & 4:
        limb = unpack("<I", file_.read(4))[0]
        result += limb << ((len_ & ~7) * 8)
    if len_ & 2:
        limb = unpack("<H", file_.read(2))[0]
        result += limb << ((len_ & ~3) * 8)
    if len_ & 1:
        limb = unpack("<B", file_.read(1))[0]
        result += limb << ((len_ & ~1) * 8)
    return result

def serialize_list(list_, serializer):
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
