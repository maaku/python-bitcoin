# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

# Python 2 and 3 compatibility utilities
import six

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

# Python patterns, base encoding
from bitcoin.serialize import (
    serialize_varint, deserialize_varint,
    serialize_varchar, deserialize_varchar,
    serialize_hash, deserialize_hash,
    serialize_beint, deserialize_beint,
    serialize_list, deserialize_list,
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
        self.assertRaises(ValueError, serialize_varint, -1)

class TestLargeValueEncode(unittest2.TestCase):
    """Test that encoding a number greater than 2**64-1 results in a value
    error."""
    def test_large_number(self):
        self.assertRaises(ValueError, serialize_varint, 2**64)

INVALID_VARINT = [
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
        scenarios = INVALID_VARINT
        def __test__(self, invalid):
            file_ = StringIO(invalid)
            self.assertRaises(EOFError, deserialize_varint, file_)

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

INVALID_VARCHAR = [
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
        scenarios = INVALID_VARCHAR
        def __test__(self, invalid):
            file_ = StringIO(invalid)
            self.assertRaises(EOFError, deserialize_varchar, file_)

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
        self.assertRaises(ValueError, serialize_hash, -1, 32)

class TestLargeHashValue(unittest2.TestCase):
    """Test that encoding a hash value greater than is representable results
    in an exception."""
    def test_large_hash(self):
        self.assertRaises(ValueError, serialize_hash, 2**256, 32)

INVALID_HASH = [
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
        scenarios = INVALID_HASH
        def __test__(self, len_, invalid):
            file_ = StringIO(invalid)
            self.assertRaises(EOFError, deserialize_hash, file_, len_)

# ===----------------------------------------------------------------------===

BEINT = [
    dict(hash_=0L, len_=2, result='\x00'*2),
    dict(hash_=0x0100L, len_=2, result='\x01\x00'),
    dict(hash_=0x020100L, len_=3, result='\x02\x01\x00'),
    dict(hash_=0x020100L, len_=4, result='\x00\x02\x01\x00'),
    dict(hash_=0x06050403020100L, len_=7, result='\x06\x05\x04\x03\x02\x01\x00'),
]

class TestSerializeBeint(unittest2.TestCase):
    """Test serialization and deserialization of big integer values under a
    variety of standard scenarios."""
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = BEINT
        def __test__(self, hash_, len_, result):
            self.assertEqual(serialize_beint(hash_, len_), result)
            self.assertEqual(serialize_beint(hash_), result.lstrip(six.int2byte(0)))
    class test_deserialize(ScenarioTest):
        scenarios = BEINT
        def __test__(self, hash_, len_, result):
            file_ = StringIO(result)
            self.assertEqual(deserialize_beint(file_, len_), hash_)

class TestSerializeLeint(unittest2.TestCase):
    """Test serialization and deserialization of little integer values under a
    variety of standard scenarios."""
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = BEINT
        def __test__(self, hash_, len_, result):
            result = result[::-1]
            self.assertEqual(serialize_leint(hash_, len_), result)
            self.assertEqual(serialize_leint(hash_), result.rstrip(six.int2byte(0)))
    class test_deserialize(ScenarioTest):
        scenarios = BEINT
        def __test__(self, hash_, len_, result):
            result = result[::-1]
            file_ = StringIO(result)
            self.assertEqual(deserialize_leint(file_, len_), hash_)

# ===----------------------------------------------------------------------===

VARINT_LIST = [
    dict(list_=[], result='\x00'),
    dict(list_=[0], result='\x01' '\x00'),
    dict(list_=[1,2,3], result='\x03' '\x01' '\x02' '\x03'),
    dict(list_=[0xfd,2**16-1,2**32-1,2**64-1],
         result='\x04' '\xfd\xfd\x00' '\xfd\xff\xff' '\xfe\xff\xff\xff\xff'
                '\xff\xff\xff\xff\xff\xff\xff\xff\xff'),
]

class TestSerializeVarintList(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = VARINT_LIST
        def __test__(self, list_, result):
            self.assertEqual(serialize_list(list_, serialize_varint), result)
    class test_deserialize(ScenarioTest):
        scenarios = VARINT_LIST
        def __test__(self, list_, result):
            file_ = StringIO(result)
            self.assertEqual(list(deserialize_list(file_, deserialize_varint)), list_)

VARCHAR_LIST = [
    dict(list_=[], result='\x00'),
    dict(list_=['abc'], result='\x01' '\x03abc'),
    dict(list_=['a','b','c'], result='\x03' '\x01a' '\x01b' '\x01c'),
    dict(list_=['9c2e4d8fe97d881430de4e754b4205b9c27ce96715231cffc4337340cb110280'.decode('hex'),
                '0c08173828583fc6ecd6ecdbcca7b6939c49c242ad5107e39deb7b0a5996b903'.decode('hex'),
                '80903da4e6bbdf96e8ff6fc3966b0cfd355c7e860bdd1caa8e4722d9230e40ac'.decode('hex')],
         result=''.join(['\x03',
                '209c2e4d8fe97d881430de4e754b4205b9c27ce96715231cffc4337340cb110280'.decode('hex'),
                '200c08173828583fc6ecd6ecdbcca7b6939c49c242ad5107e39deb7b0a5996b903'.decode('hex'),
                '2080903da4e6bbdf96e8ff6fc3966b0cfd355c7e860bdd1caa8e4722d9230e40ac'.decode('hex')]))
]

class TestSerializeVarcharList(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = VARCHAR_LIST
        def __test__(self, list_, result):
            self.assertEqual(serialize_list(list_, serialize_varchar), result)
    class test_deserialize(ScenarioTest):
        scenarios = VARCHAR_LIST
        def __test__(self, list_, result):
            file_ = StringIO(result)
            self.assertEqual(list(deserialize_list(file_, deserialize_varchar)), list_)

HASH_LIST = [
    dict(list_=[], len_=32, result='\x00'),
    dict(list_=[0xe3,0xb0,0xc4,0x42], len_=1, result='04e3b0c442'.decode('hex')),
    dict(list_=[57899701122132101464827042574540132333372807239036611982162394440476474027676L,
                 1684842915225173030403236558293661766361892666541902041157183603580616509452L,
                77910985759381492884405384511824803321298316529212868719112358856289568002176L],
         len_=32,
         result=''.join(['\x03',
                '9c2e4d8fe97d881430de4e754b4205b9c27ce96715231cffc4337340cb110280'.decode('hex'),
                '0c08173828583fc6ecd6ecdbcca7b6939c49c242ad5107e39deb7b0a5996b903'.decode('hex'),
                '80903da4e6bbdf96e8ff6fc3966b0cfd355c7e860bdd1caa8e4722d9230e40ac'.decode('hex')])),
]

class TestSerializeHashList(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = HASH_LIST
        def __test__(self, list_, len_, result):
            self.assertEqual(serialize_list(list_, lambda h:serialize_hash(h, len_)), result)
    class test_deserialize(ScenarioTest):
        scenarios = HASH_LIST
        def __test__(self, list_, len_, result):
            file_ = StringIO(result)
            self.assertEqual(list(deserialize_list(file_, lambda f:deserialize_hash(f, len_))), list_)

# FIXME: test serialization of a list of inputs, outputs, transactions,
#     blocks, etc.

INVALID_LIST = [
    dict(invalid='030102'.decode('hex'), deserializer=deserialize_varint),
    dict(invalid='040002aabb03ccddee'.decode('hex'), deserializer=deserialize_varchar),
    dict(invalid='05aabbccdd'.decode('hex'), deserializer=lambda f:deserialize_hash(f,1)),
]

class TestInvalidListSerialization(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_invalid_serialization(ScenarioTest):
        scenarios = INVALID_LIST
        def __test__(self, invalid, deserializer):
            file_ = StringIO(invalid)
            self.assertRaises(EOFError, lambda f,d:list(deserialize_list(f,d)), file_, deserializer)

#
# End of File
#
