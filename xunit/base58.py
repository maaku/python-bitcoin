# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

# Python 2 and 3 compatibility utilities
import six

# Python standard library, unit-testing
import unittest

# Scenario unit-testing
from scenariotest import ScenarioMeta, ScenarioTest

from bitcoin.base58 import *

# ===----------------------------------------------------------------------===

BASE58_CODEC = [
    dict(data='', result=u""),
    dict(data=chr(0), result=u"1"),
    dict(data     = b'\x00'+bytes.fromhex('1f8b1340c286881bcc449c37569ae320b013785d'+'48427760'),
         result   = u"13snZ4ZyCzaL7358SmgvHGC9AxskqumNxP"),
    dict(data     = b'\x05'+bytes.fromhex('5ece0cadddc415b1980f001785947120acdb36fc'+'b43c48af'),
         result   = u"3ALJH9Y951VCGcVZYAdpA3KchoP9McEj1G"),
    # src/test/data/base58_encode_decode.json:
    dict(data=bytes.fromhex('61'), result=u"2g"),
    dict(data=bytes.fromhex('626262'), result=u"a3gV"),
    dict(data=bytes.fromhex('636363'), result=u"aPEr"),
    dict(data=bytes.fromhex('516b6fcd0f'), result=u"ABnLTmg"),
    dict(data=bytes.fromhex('bf4f89001e670274dd'), result=u"3SEo3LWLoPntC"),
    dict(data=bytes.fromhex('572e4794'), result=u"3EFU7m"),
    dict(data=bytes.fromhex('ecac89cad93923c02321'), result=u"EJDM8drfXA6uyA"),
    dict(data=bytes.fromhex('10c8511e'), result=u"Rt5zm"),
    dict(data=bytes.fromhex('00000000000000000000'), result=u"1111111111"),
    dict(data   = bytes.fromhex('73696d706c792061206c6f6e6720737472696e67'),
         result = u"2cFupjhnEsSn59qHXstmK2ffpLv2"),
    dict(data   = bytes.fromhex('00eb15231dfceb60925886b67d065299925915aeb172c06647'),
         result = u"1NS17iag9jJgTHD1VXjvLCEnZuQ3rJDE9L"),
]

class TestCodecBase58(unittest.TestCase):
    "Test encoding and decoding of base58 values."
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = BASE58_CODEC
        def __test__(self, data, result):
            self.assertEqual(data.encode('base58'), result)
    class test_deserialize(ScenarioTest):
        scenarios = BASE58_CODEC
        def __test__(self, data, result):
            self.assertEqual(result.decode('base58'), data)

# ===----------------------------------------------------------------------===

from bitcoin.errors import HashChecksumError

HASH_CHECKED_DATA = [
    dict(data     = b'\x00' + bytes.fromhex('1f8b1340c286881bcc449c37569ae320b013785d'),
         checksum = bytes.fromhex('48427760'),
         base58   = u"13snZ4ZyCzaL7358SmgvHGC9AxskqumNxP"),
    dict(data     = b'\x05' + bytes.fromhex('5ece0cadddc415b1980f001785947120acdb36fc'),
         checksum = bytes.fromhex('b43c48af'),
         base58   = u"3ALJH9Y951VCGcVZYAdpA3KchoP9McEj1G"),
]

class TestHashCheckedData(unittest.TestCase):
    "Test checksummed base58 values"
    __metaclass__ = ScenarioMeta
    class test_init(ScenarioTest):
        scenarios = HASH_CHECKED_DATA
        def __test__(self, data, checksum, base58):
            checked = HashCheckedData(base58.decode('base58'))
            self.assertEqual(checked, b''.join([data, checksum]))
            self.assertEqual(checked.data, data)
            self.assertEqual(checked.checksum, checksum)
            self.assertEqual(checked.encode('base58'), base58)
            checked = HashCheckedData(data, add_hash=True)
            self.assertEqual(checked, b''.join([data, checksum]))
            self.assertEqual(checked.data, data)
            self.assertEqual(checked.checksum, checksum)
            self.assertEqual(checked.encode('base58'), base58)
            with self.assertRaises(HashChecksumError):
                checked = HashCheckedData(
                    add_hash = False,
                    data     = b''.join([
                            data,
                            checksum[:-1],
                            six.int2byte(0xff & ~ord(checksum[-1:]))
                        ]))

BAD_HASH_DATA = [
    # Too short:
    dict(data=b''),
    dict(data=b'\x00'),
    dict(data=b'\x00'*2),
    dict(data=b'\x00'*3),
    # Bad checksum:
    dict(data=b'\x00'*4),
]

class TestBadHashChecksum(unittest.TestCase):
    "Test bad checksums for HashCheckedData"
    __metaclass__ = ScenarioMeta
    class test_bad_checksum(ScenarioTest):
        scenarios = BAD_HASH_DATA
        def __test__(self, data):
            with self.assertRaises(HashChecksumError):
                checked = HashCheckedData(data, add_hash=False)

# ===----------------------------------------------------------------------===

VERSIONED_PAYLOAD = [
    dict(version  = 0,
         payload  = bytes.fromhex('1f8b1340c286881bcc449c37569ae320b013785d'),
         checksum = bytes.fromhex('48427760'),
         base58   = u"13snZ4ZyCzaL7358SmgvHGC9AxskqumNxP"),
    dict(version  = 5,
         payload  = bytes.fromhex('5ece0cadddc415b1980f001785947120acdb36fc'),
         checksum = bytes.fromhex('b43c48af'),
         base58   = u"3ALJH9Y951VCGcVZYAdpA3KchoP9McEj1G"),
]

class TestVersionedPayload(unittest.TestCase):
    "Test versioned base58 payloads"
    __metaclass__ = ScenarioMeta
    class test_init(ScenarioTest):
        scenarios = VERSIONED_PAYLOAD
        def __test__(self, version, payload, checksum, base58):
            data = b''.join([six.int2byte(version), payload])
            checked = VersionedPayload(base58.decode('base58'))
            self.assertEqual(checked, b''.join([data, checksum]))
            self.assertEqual(checked.version, version)
            self.assertEqual(checked.payload, payload)
            self.assertEqual(checked.data, data)
            self.assertEqual(checked.checksum, checksum)
            self.assertEqual(checked.encode('base58'), base58)
    class test_init_with_version(ScenarioTest):
        scenarios = VERSIONED_PAYLOAD
        def __test__(self, version, payload, checksum, base58):
            data = b''.join([six.int2byte(version), payload])
            checked = VersionedPayload(payload, version=version)
            self.assertEqual(checked, b''.join([data, checksum]))
            self.assertEqual(checked.version, version)
            self.assertEqual(checked.payload, payload)
            self.assertEqual(checked.data, data)
            self.assertEqual(checked.checksum, checksum)
            self.assertEqual(checked.encode('base58'), base58)
    class test_init_with_version_explicit_hash(ScenarioTest):
        scenarios = VERSIONED_PAYLOAD
        def __test__(self, version, payload, checksum, base58):
            data = b''.join([six.int2byte(version), payload])
            checked = VersionedPayload(payload + checksum,
                version = version, add_hash = False)
            self.assertEqual(checked, b''.join([data, checksum]))
            self.assertEqual(checked.version, version)
            self.assertEqual(checked.payload, payload)
            self.assertEqual(checked.data, data)
            self.assertEqual(checked.checksum, checksum)
            self.assertEqual(checked.encode('base58'), base58)

class TestInvalidInit(unittest.TestCase):
    def test_invalid_init_with_version_only(self):
        with self.assertRaises(VersionedPayloadError):
            VersionedPayload(version=0)
    def test_invalid_init_with_empty_data(self):
        with self.assertRaises(VersionedPayloadError):
            VersionedPayload(data=b'', add_hash=True)
