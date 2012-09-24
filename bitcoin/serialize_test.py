#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === bitcoin.serialize_test ----------------------------------------------===
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

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

# Python patterns, base encoding
from bitcoin.serialize import (
    serialize_varint, deserialize_varint,
    serialize_varchar, deserialize_varchar,
    serialize_hash, deserialize_hash,
)

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

VARINT = [
    dict(long_=0, result='\x00'),
    dict(long_=1, result='\x01'),
    dict(long_=2, result='\x02'),
    dict(long_=3, result='\x03'),
    dict(long_=250, result='\xfa'),
    dict(long_=251, result='\xfb'),
    dict(long_=252, result='\xfc'),
    dict(long_=253, result='\xfd\xfd\x00'),
    dict(long_=254, result='\xfd\xfe\x00'),
    dict(long_=255, result='\xfd\xff\x00'),
    dict(long_=256, result='\xfd\x00\x01'),
    dict(long_=2**16-2, result='\xfd\xfe\xff'),
    dict(long_=2**16-1, result='\xfd\xff\xff'),
    dict(long_=2**16,   result='\xfe\x00\x00\x01\x00'),
    dict(long_=2**16+1, result='\xfe\x01\x00\x01\x00'),
    dict(long_=2**32-2, result='\xfe\xfe\xff\xff\xff'),
    dict(long_=2**32-1, result='\xfe\xff\xff\xff\xff'),
    dict(long_=2**32,   result='\xff\x00\x00\x00\x00\x01\x00\x00\x00'),
    dict(long_=2**32+1, result='\xff\x01\x00\x00\x00\x01\x00\x00\x00'),
    dict(long_=2**64-2, result='\xff\xfe\xff\xff\xff\xff\xff\xff\xff'),
    dict(long_=2**64-1, result='\xff\xff\xff\xff\xff\xff\xff\xff\xff'),
]

class TestSerializeVarint(unittest2.TestCase):
    """Test serialization and deserialization of varints under a variety of
    standard scenarios."""
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = VARINT
        def __test__(self, long_, result):
            self.assertEqual(serialize_varint(long_), result)
    class test_deserialize(ScenarioTest):
        scenarios = VARINT
        def __test__(self, long_, result):
            file_ = StringIO(result)
            self.assertEqual(deserialize_varint(file_), long_)

class TestNegativeNumberEncode(unittest2.TestCase):
    "Test that encoding a negative number results in a value error."
    def test_negative_number(self):
        self.assertRaises(BaseException, serialize_varint, -1)

class TestLargeValueEncode(unittest2.TestCase):
    """Test that encoding a number greater than 2**64-1 results in a value
    error."""
    def test_large_number(self):
        self.assertRaises(BaseException, serialize_varint, 2**64)

VARINT2 = [
    dict(invalid='\xfd'),
    dict(invalid='\xfd\x00'),
    dict(invalid='\xfe'),
    dict(invalid='\xfe\x00'),
    dict(invalid='\xfe\x00\x00'),
    dict(invalid='\xfe\x00\x00\x00'),
    dict(invalid='\xff'),
    dict(invalid='\xff\x00'),
    dict(invalid='\xff\x00\x00'),
    dict(invalid='\xff\x00\x00\x00'),
    dict(invalid='\xff\x00\x00\x00\x00'),
    dict(invalid='\xff\x00\x00\x00\x00\x00'),
    dict(invalid='\xff\x00\x00\x00\x00\x00\x00'),
    dict(invalid='\xff\x00\x00\x00\x00\x00\x00\x00'),
]

class TestInvalidVarintSerialization(unittest2.TestCase):
    """Test that deserialization of an incomplete varint structure results in
    a value error."""
    __metaclass__ = ScenarioMeta
    class test_invalid_serialization(ScenarioTest):
        scenarios = VARINT2
        def __test__(self, invalid):
            file_ = StringIO(invalid)
            self.assertRaises(BaseException, deserialize_varint, file_)

# ===----------------------------------------------------------------------===

VARCHAR = [
    dict(str_='', result='\x00'),
    dict(str_='a', result='\x01a'),
    dict(str_='bc', result='\x02bc'),
    dict(str_='123', result='\x03123'),
    dict(str_='\x01\x02', result='\x02\x01\x02'),
    dict(str_='Ping\x00Pong\n', result='\x0aPing\x00Pong\n'),
    dict(str_='\x7f\x80\x00\xff', result='\x04\x7f\x80\x00\xff'),
    dict(str_='a'*0xfc, result='\xfc'+'a'*0xfc),
    dict(str_='a'*0xfd, result='\xfd\xfd\x00'+'a'*0xfd),
    dict(str_='a'*0xffff, result='\xfd\xff\xff'+'a'*0xffff),
    dict(str_='a'*0x10000, result='\xfe\x00\x00\x01\x00'+'a'*0x10000),
]

class TestSerializeVarchar(unittest2.TestCase):
    """Test serialization and deserialization of varchars (strings) under a
    variety of standard scenarios."""
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = VARCHAR
        def __test__(self, str_, result):
            self.assertEqual(serialize_varchar(str_), result)
    class test_deserialize(ScenarioTest):
        scenarios = VARCHAR
        def __test__(self, str_, result):
            file_ = StringIO(result)
            self.assertEqual(deserialize_varchar(file_), str_)

VARCHAR2 = [
    dict(invalid='\x01'),
    dict(invalid='\x02'),
    dict(invalid='\x02a'),
    dict(invalid='\x03a'),
    dict(invalid='\x03ab'),
    dict(invalid='\xfd\xfd\x00'+'a'*0xfc),
]

class TestInvalidVarcharSerialization(unittest2.TestCase):
    """Test that deserialization of an incomplete varint structure results in
    a value error."""
    __metaclass__ = ScenarioMeta
    class test_invalid_serialization(ScenarioTest):
        scenarios = VARCHAR2
        def __test__(self, invalid):
            file_ = StringIO(invalid)
            self.assertRaises(BaseException, deserialize_varchar, file_)

# ===----------------------------------------------------------------------===

HASH = [
    dict(hash_=0L, len_=1, result='\x00'),
    dict(hash_=0L, len_=2, result='\x00'*2),
    dict(hash_=0L, len_=8, result='\x00'*8),
    dict(hash_=0L, len_=20, result='\x00'*20),
    dict(hash_=0L, len_=32, result='\x00'*32),
    dict(hash_=1L, len_=1, result='\x01'),
    dict(hash_=1L, len_=32, result='\x01'+'\x00'*31),
    dict(hash_=0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26fL,
         len_=32,
         result='000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'.decode('hex')[::-1])
]

class TestSerializeHash(unittest2.TestCase):
    """Test serialization and deserialization of hashes (large integers
    serialized as little-endian byte-arrays) under a variety of standard
    scenarios."""
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = HASH
        def __test__(self, hash_, len_, result):
            self.assertEqual(serialize_hash(hash_, len_), result)
    class test_deserialize(ScenarioTest):
        scenarios = HASH
        def __test__(self, hash_, len_, result):
            file_ = StringIO(result)
            self.assertEqual(deserialize_hash(file_, len_), hash_)

class TestNegativeHashValue(unittest2.TestCase):
    "Test that serializing a negative hash results in an exception."
    def test_negative_hash(self):
        self.assertRaises(BaseException, serialize_hash, (-1, 32))

class TestLargeHashValue(unittest2.TestCase):
    """Test that encoding a hash value greater than is representable results
    in an exception."""
    def test_large_hash(self):
        self.assertRaises(BaseException, serialize_hash, (2**256, 32))

HASH2 = [
    dict(len_=1, invalid=''),
    dict(len_=2, invalid='\x00'),
    dict(len_=20, invalid=''),
    dict(len_=20, invalid='\x00'*19),
    dict(len_=32, invalid=''),
    dict(len_=32, invalid='\x00'*31),
]

class TestInvalidHashSerialization(unittest2.TestCase):
    """Test deserialization of an invalid hash representation results in an
    exception."""
    __metaclass__ = ScenarioMeta
    class test_invalid_serialization(ScenarioTest):
        scenarios = HASH2
        def __test__(self, len_, invalid):
            file_ = StringIO(invalid)
            self.assertRaises(BaseException, deserialize_hash, (file_, len_))

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
