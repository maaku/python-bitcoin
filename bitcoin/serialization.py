#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === bitcoin.utils.serialization -----------------------------------------===
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

"Utility functions used in implementing the block chain serialization format."

from struct import pack, unpack

__all__ = [
  'serialize_varint',
  'deserialize_varint',
  'serialize_varchar',
  'deserialize_varchar',
  'serialize_uint256',
  'deserialize_uint256',
  'uint256_from_compact',
  'serialize_list',
  'deserialize_list',
  'serialize_uint256_list',
  'deserialize_uint256_list',
]

def serialize_varint(long_):
  if long_ < 253:
    return chr(long_)
  elif long_ <= 0xFFFFL:
    return chr(253) + pack("<H", long_)
  elif long_ <= 0xFFFFFFFFL:
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

def serialize_uint256(long_):
  result = ''
  for i in xrange(4):
    result += pack("<Q", long_ & 0xFFFFFFFFFFFFFFFFL)
    long_ >>= 64
  if long_:
    raise ValueError(_(u"integer exceeds 256 bits in length"))
  return result

def deserialize_uint256(file_):
  result = 0L
  for idx in xrange(4):
    limb = unpack("<Q", file_.read(8))[0]
    result += limb << (idx * 64)
  return result

def uint256_from_compact(bits):
  len_ = (bits >> 24) & 0xFF
  return (bits & 0xFFFFFFL) << (8 * (len_ - 3))

def serialize_list(list_):
  result = serialize_varint(len(list_))
  for item in list_:
    result += item.serialize()
  return result

def deserialize_list(class_, file_):
  for _ in xrange(deserialize_varint(file_)):
    yield class_.deserialize(file_)
  raise StopIteration

def serialize_uint256_list(list_):
  result = serialize_varint(len(list_))
  for item in list_:
    result += serialize_uint256(item)
  return result

def deserialize_uint256_list(file_):
  for _ in xrange(deserialize_varint(file_)):
    yield deserialize_uint256(file_)
  raise StopIteration

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
