#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === bitcoin.serialize ---------------------------------------------------===
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

# ===----------------------------------------------------------------------===
# This file is based in part on code published as part of the pynode project.
# The original work is copyrighted by it's authors and licensed according to
# the terms of the MIT license (below); modifications since then are the
# property of RokuSigma Inc. and subject to the above-referenced
# confidentiality and non-disclosure agreements.
# ===----------------------------------------------------------------------===

# ===----------------------------------------------------------------------===
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ===----------------------------------------------------------------------===

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
    return file_.read(len_)

def serialize_hash(long_, len_):
    if long_ < 0:
        raise ValueError(_(u"negative hash value doesn't make any sense"))
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
        raise ValueError(_(u"hash value exceeds maximum representable value"))
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
        yield serializer(file_)
    raise StopIteration

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
