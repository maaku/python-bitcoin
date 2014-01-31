# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

# Python 2 and 3 compatibility utilities
import six

# Python standard library, unit-testing
import unittest2

# Scenario unit-testing
from scenariotest import ScenarioMeta, ScenarioTest

# Python patterns, base encoding
from bitcoin.serialize import *

from bitcoin.defaults import CHAIN_PARAMETERS, CLIENT_VERSION

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

COMPACT_SIZE = [
    dict(size=0, result='\x00'),
    dict(size=1, result='\x01'),
    dict(size=2, result='\x02'),
    dict(size=3, result='\x03'),
    dict(size=250, result='\xfa'),
    dict(size=251, result='\xfb'),
    dict(size=252, result='\xfc'),
    dict(size=253, result='\xfd\xfd\x00'),
    dict(size=254, result='\xfd\xfe\x00'),
    dict(size=255, result='\xfd\xff\x00'),
    dict(size=256, result='\xfd\x00\x01'),
    dict(size=2**16-2, result='\xfd\xfe\xff'),
    dict(size=2**16-1, result='\xfd\xff\xff'),
    dict(size=2**16,   result='\xfe\x00\x00\x01\x00'),
    dict(size=2**16+1, result='\xfe\x01\x00\x01\x00'),
    dict(size=2**32-2, result='\xfe\xfe\xff\xff\xff'),
    dict(size=2**32-1, result='\xfe\xff\xff\xff\xff'),
    dict(size=2**32,   result='\xff\x00\x00\x00\x00\x01\x00\x00\x00'),
    dict(size=2**32+1, result='\xff\x01\x00\x00\x00\x01\x00\x00\x00'),
    dict(size=2**64-2, result='\xff\xfe\xff\xff\xff\xff\xff\xff\xff'),
    dict(size=2**64-1, result='\xff\xff\xff\xff\xff\xff\xff\xff\xff'),
]

class TestSerializeCompactSize(unittest2.TestCase):
    """Test serialization and deserialization of CompactSize under a variety
    of standard scenarios."""
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = COMPACT_SIZE
        def __test__(self, size, result):
            self.assertEqual(CompactSize(size).serialize(), result)
    class test_deserialize(ScenarioTest):
        scenarios = COMPACT_SIZE
        def __test__(self, size, result):
            file_ = StringIO(result)
            self.assertEqual(CompactSize.deserialize(file_), size)

class TestNegativeNumberCompactSize(unittest2.TestCase):
    "Test that encoding a negative number results in a value error."
    def test_negative_number(self):
        self.assertRaises(ValueError,
            lambda n:CompactSize(n).serialize(), -1)

class TestLargeValueCompactSize(unittest2.TestCase):
    "Test that encoding a number greater than 2**64-1 results in a value error."
    def test_large_number(self):
        self.assertRaises(ValueError,
            lambda n:CompactSize(n).serialize(), 2**64)

INVALID_COMPACT_SIZE = [
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

class TestInvalidCompactSizeSerialization(unittest2.TestCase):
    """Test that deserialization of an incomplete CompactSize structure
    results in a value error."""
    __metaclass__ = ScenarioMeta
    class test_invalid_serialization(ScenarioTest):
        scenarios = INVALID_COMPACT_SIZE
        def __test__(self, invalid):
            file_ = StringIO(invalid)
            self.assertRaises(EOFError,
                CompactSize.deserialize, file_)

# ===----------------------------------------------------------------------===

FLAT_DATA = [
    dict(data=''),
    dict(data='a'),
    dict(data='bc'),
    dict(data='123'),
    dict(data='\x01\x02'),
    dict(data='Ping\x00Pong\n'),
    dict(data='\x7f\x80\x00\xff'),
    dict(data='a'*0xfc),
    dict(data='a'*0xfd),
    dict(data='a'*0xffff),
    dict(data='a'*0x10000),
]

class TestSerializeFlatData(unittest2.TestCase):
    """Test serialization and deserialization of FlatData (strings) under a
    variety of standard scenarios."""
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = FLAT_DATA
        def __test__(self, data):
            self.assertEqual(
                FlatData(data).serialize(),
                data)
    class test_deserialize(ScenarioTest):
        scenarios = FLAT_DATA
        def __test__(self, data):
            self.assertEqual(
                FlatData.deserialize(StringIO(data), len(data)),
                data)

# ===----------------------------------------------------------------------===

BIG_INTEGER = [
    dict(hash_=0L, len_=1, result='\x00'),
    dict(hash_=0L, len_=2, result='\x00'*2),
    dict(hash_=0L, len_=20, result='\x00'*20),
    dict(hash_=0L, len_=32, result='\x00'*32),
    dict(hash_=1L, len_=1, result='\x01'),
    dict(hash_=1L, len_=32, result='\x00'*31+'\x01'),
    dict(hash_=0x0100L, len_=2, result='\x01\x00'),
    dict(hash_=0x020100L, len_=3, result='\x02\x01\x00'),
    dict(hash_=0x020100L, len_=4, result='\x00\x02\x01\x00'),
    dict(hash_=0x06050403020100L, len_=7, result='\x06\x05\x04\x03\x02\x01\x00'),
    dict(hash_=0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26fL,
         len_=32,
         result='000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'.decode('hex')),
]

class TestSerializeBigInteger(unittest2.TestCase):
    """Test serialization and deserialization of big integer values under a
    variety of standard scenarios."""
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = BIG_INTEGER
        def __test__(self, hash_, len_, result):
            self.assertEqual(BigInteger(hash_).serialize(len_), result)
            self.assertEqual(
                BigInteger(hash_).serialize(),
                result.lstrip(six.int2byte(0)))
    class test_deserialize(ScenarioTest):
        scenarios = BIG_INTEGER
        def __test__(self, hash_, len_, result):
            file_ = StringIO(result)
            self.assertEqual(BigInteger.deserialize(file_, len_), hash_)

class TestNegativeBigIntegerValue(unittest2.TestCase):
    "Test that serializing a negative big integer value results in an exception."
    def test_negative_big_integer(self):
        self.assertRaises(ValueError,
            lambda n,l:BigInteger(n).serialize(l), -1, 32)

class TestLargeBigIntegerValue(unittest2.TestCase):
    """Test that encoding a big integer value greater than is representable
    results in an exception."""
    def test_large_big_integer(self):
        self.assertRaises(ValueError,
            lambda n,l:BigInteger(n).serialize(l), 2**256, 32)

class TestSerializeLittleInteger(unittest2.TestCase):
    """Test serialization and deserialization of little integer values under a
    variety of standard scenarios."""
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = BIG_INTEGER
        def __test__(self, hash_, len_, result):
            result = result[::-1]
            self.assertEqual(LittleInteger(hash_).serialize(len_), result)
            self.assertEqual(
                LittleInteger(hash_).serialize(),
                result.rstrip(six.int2byte(0)))
    class test_deserialize(ScenarioTest):
        scenarios = BIG_INTEGER
        def __test__(self, hash_, len_, result):
            result = result[::-1]
            file_ = StringIO(result)
            self.assertEqual(LittleInteger.deserialize(file_, len_), hash_)

class TestNegativeLittleIntegerValue(unittest2.TestCase):
    "Test that serializing a negative little integer value results in an exception."
    def test_negative_little_integer(self):
        self.assertRaises(ValueError,
            lambda n,l:LittleInteger(n).serialize(l), -1, 32)

class TestLargeLittleIntegerValue(unittest2.TestCase):
    """Test that encoding a little integer value greater than is representable
    results in an exception."""
    def test_large_little_integer(self):
        self.assertRaises(ValueError,
            lambda n,l:LittleInteger(n).serialize(l), 2**256, 32)

INVALID_BIG_INTEGER = [
    dict(len_=1, invalid=''),
    dict(len_=2, invalid='\x00'),
    dict(len_=20, invalid=''),
    dict(len_=20, invalid='\x00'*19),
    dict(len_=32, invalid=''),
    dict(len_=32, invalid='\x00'*31),
]

class TestInvalidBigIntegerSerialization(unittest2.TestCase):
    """Test deserialization of an invalid big integer representation results
    in an exception."""
    __metaclass__ = ScenarioMeta
    class test_invalid_serialization(ScenarioTest):
        scenarios = INVALID_BIG_INTEGER
        def __test__(self, len_, invalid):
            file_ = StringIO(invalid)
            self.assertRaises(EOFError, BigInteger.deserialize, file_, len_)

class TestInvalidLittleIntegerSerialization(unittest2.TestCase):
    """Test deserialization of an invalid little integer representation results
    in an exception."""
    __metaclass__ = ScenarioMeta
    class test_invalid_serialization(ScenarioTest):
        scenarios = INVALID_BIG_INTEGER
        def __test__(self, len_, invalid):
            file_ = StringIO(invalid[::-1])
            self.assertRaises(EOFError, LittleInteger.deserialize, file_, len_)

# ===----------------------------------------------------------------------===

COMPACT_SIZE_LIST = [
    dict(list_=[], result='\x00'),
    dict(list_=[0], result='\x01' '\x00'),
    dict(list_=[1,2,3], result='\x03' '\x01' '\x02' '\x03'),
    dict(list_=[0xfd,2**16-1,2**32-1,2**64-1],
         result='\x04' '\xfd\xfd\x00' '\xfd\xff\xff' '\xfe\xff\xff\xff\xff'
                '\xff\xff\xff\xff\xff\xff\xff\xff\xff'),
]

class TestSerializeCompactSizeList(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = COMPACT_SIZE_LIST
        def __test__(self, list_, result):
            self.assertEqual(
                serialize_iterator(list_, lambda n:CompactSize(n).serialize()),
                result)
    class test_deserialize(ScenarioTest):
        scenarios = COMPACT_SIZE_LIST
        def __test__(self, list_, result):
            file_ = StringIO(result)
            self.assertEqual(
                list(deserialize_iterator(file_, CompactSize.deserialize)),
                list_)

from bitcoin.hash import hash160, hash256

HASH_LIST = [
    dict(list_=[], compressor=hash160, result='\x00'),
    dict(list_=[], compressor=hash256, result='\x00'),
    dict(list_=[1292449372288863884094820641297402186192998806594L,
                1175657851699757026654588809656041930282180078663L,
                1349297413382569173582680094155095764663829224436L],
         compressor=hash160,
         result=''.join(['\x03',
                '42b4e6b435e8101600df0c3a63f3989f2b6f63e2'.decode('hex'),
                '47ec8c0afb5580f73e21fbd6ca05adee4352eecd'.decode('hex'),
                'f45bdfc174331f53d2bf8fdd6d439d86ad9658ec'.decode('hex')])),
    dict(list_=[57899701122132101464827042574540132333372807239036611982162394440476474027676L,
                 1684842915225173030403236558293661766361892666541902041157183603580616509452L,
                77910985759381492884405384511824803321298316529212868719112358856289568002176L],
         compressor=hash256,
         result=''.join(['\x03',
                '9c2e4d8fe97d881430de4e754b4205b9c27ce96715231cffc4337340cb110280'.decode('hex'),
                '0c08173828583fc6ecd6ecdbcca7b6939c49c242ad5107e39deb7b0a5996b903'.decode('hex'),
                '80903da4e6bbdf96e8ff6fc3966b0cfd355c7e860bdd1caa8e4722d9230e40ac'.decode('hex')])),
]

class TestSerializeHashList(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = HASH_LIST
        def __test__(self, list_, compressor, result):
            self.assertEqual(serialize_iterator(list_, lambda h:compressor.serialize(h)), result)
    class test_deserialize(ScenarioTest):
        scenarios = HASH_LIST
        def __test__(self, list_, compressor, result):
            file_ = StringIO(result)
            self.assertEqual(list(deserialize_iterator(file_, lambda f:compressor.deserialize(f))), list_)

# FIXME: test serialization of a list of inputs, outputs, transactions,
#     blocks, etc.

INVALID_LIST = [
    dict(invalid='030102'.decode('hex'), deserializer=CompactSize.deserialize),
    dict(invalid='05aabbccdd'.decode('hex'), deserializer=lambda f:LittleInteger.deserialize(f,1)),
]

class TestInvalidListSerialization(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_invalid_serialization(ScenarioTest):
        scenarios = INVALID_LIST
        def __test__(self, invalid, deserializer):
            file_ = StringIO(invalid)
            self.assertRaises(EOFError, lambda f,d:list(deserialize_iterator(f,d)), file_, deserializer)
