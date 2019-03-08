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

from bitcoin.crypto import *
from bitcoin.serialize import BigInteger

# ===----------------------------------------------------------------------===

class TestSECP256k1(unittest.TestCase):
    def test_name(self):
        self.assertEqual(SECP256k1.name, 'SECP256k1')
    def test_order(self):
        self.assertEqual(SECP256k1.order,
            0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141)

# ===----------------------------------------------------------------------===

SECRET = [
    dict(exponent=0x12b004fff7f4b69ef8650e767f18f11ede158148b425660723b9f9a66e61f747,
         secret=bytes.fromhex('8012b004fff7f4b69ef8650e767f18f11ede158148b425660723b9f9a66e61f747'
                              'ef4604d4'),
         compressed_secret=bytes.fromhex('8012b004fff7f4b69ef8650e767f18f11ede158148b42566'
                                         '0723b9f9a66e61f747017555cd1c')),
]

class TestSecret(unittest.TestCase):
    __metaclass__ = ScenarioMeta
    class test_init_with_exponent(ScenarioTest):
        scenarios = SECRET
        def __test__(self, exponent, secret, compressed_secret):
            obj = Secret(exponent, compressed=False)
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            obj = Secret(exponent, compressed=True)
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)
            # Not specifying compressed defaults to compressed=True
            obj = Secret(exponent)
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)

    class test_init_from_other(ScenarioTest):
        scenarios = SECRET
        def __test__(self, exponent, secret, compressed_secret):
            with self.assertRaises(InvalidSecretError):
                Secret(b''.join([
                    six.int2byte(0x80),
                    BigInteger(exponent).serialize(32),
                    secret[-4:]]), compressed=False)
            with self.assertRaises(InvalidSecretError):
                Secret(b''.join([
                    six.int2byte(0x80),
                    BigInteger(exponent).serialize(32),
                    secret[-4:]]), compressed=True)
            obj = Secret(b''.join([
                six.int2byte(0x80),
                BigInteger(exponent).serialize(32),
                secret[-4:]]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            with self.assertRaises(InvalidSecretError):
                Secret(b''.join([
                    six.int2byte(0x80),
                    BigInteger(exponent).serialize(32),
                    six.int2byte(0x01),
                    compressed_secret[-4:]]), compressed=False)
            with self.assertRaises(InvalidSecretError):
                Secret(b''.join([
                    six.int2byte(0x80),
                    BigInteger(exponent).serialize(32),
                    six.int2byte(0x01),
                    compressed_secret[-4:]]), compressed=True)
            obj = Secret(b''.join([
                six.int2byte(0x80),
                BigInteger(exponent).serialize(32),
                six.int2byte(0x01),
                compressed_secret[-4:]]))
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)

    class test_init_from_data(ScenarioTest):
        scenarios = SECRET
        def __test__(self, exponent, secret, compressed_secret):
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=False, data=b''.join([
                    six.int2byte(0x80),
                    BigInteger(exponent).serialize(32),
                    secret[-4:]]))
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=True, data=b''.join([
                    six.int2byte(0x80),
                    BigInteger(exponent).serialize(32),
                    secret[-4:]]))
            obj = Secret(data=b''.join([
                six.int2byte(0x80),
                BigInteger(exponent).serialize(32),
                secret[-4:]]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            obj = Secret(add_hash=False, data=b''.join([
                six.int2byte(0x80),
                BigInteger(exponent).serialize(32),
                secret[-4:]]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            obj = Secret(add_hash=True, data=b''.join([
                six.int2byte(0x80),
                BigInteger(exponent).serialize(32)]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=True, data=b''.join([
                    six.int2byte(0x80),
                    BigInteger(exponent).serialize(32),
                    six.int2byte(0x01),
                    compressed_secret[-4:]]))
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=False, data=b''.join([
                    six.int2byte(0x80),
                    BigInteger(exponent).serialize(32),
                    six.int2byte(0x01),
                    compressed_secret[-4:]]))
            obj = Secret(data=b''.join([
                six.int2byte(0x80),
                BigInteger(exponent).serialize(32),
                six.int2byte(0x01),
                compressed_secret[-4:]]))
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)
            obj = Secret(add_hash=False, data=b''.join([
                six.int2byte(0x80),
                BigInteger(exponent).serialize(32),
                six.int2byte(0x01),
                compressed_secret[-4:]]))
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)
            obj = Secret(add_hash=True, data=b''.join([
                    six.int2byte(0x80),
                    BigInteger(exponent).serialize(32),
                    six.int2byte(0x01)]))
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)

    class test_init_from_payload(ScenarioTest):
        scenarios = SECRET
        def __test__(self, exponent, secret, compressed_secret):
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=False, payload=b''.join([
                    BigInteger(exponent).serialize(32)]))
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=True, payload=b''.join([
                    BigInteger(exponent).serialize(32)]))
            obj = Secret(payload=b''.join([BigInteger(exponent).serialize(32)]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=False, payload=b''.join([
                    BigInteger(exponent).serialize(32),
                    six.int2byte(0x01)]))
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=True, payload=b''.join([
                    BigInteger(exponent).serialize(32),
                    six.int2byte(0x01)]))
            obj = Secret(payload=b''.join([
                BigInteger(exponent).serialize(32),
                six.int2byte(0x01)]))
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)

class TestInvalidSecret(unittest.TestCase):
    def test_zero_exponent(self):
        with self.assertRaises(InvalidSecretError):
            Secret(0)
    def test_zero_exponent_modulo_order(self):
        with self.assertRaises(InvalidSecretError):
            Secret(SECP256k1.order)

INVALID_SECRET = [
    # Too short:
    dict(data=bytes.fromhex('80c9403978')),
    dict(data=bytes.fromhex('80aaa39001da')),
    dict(data=bytes.fromhex('80aaaa4aed84b5')),
    dict(data=bytes.fromhex('80aaaaaac05059f9')),
    dict(data=bytes.fromhex('80aaaaaaaacefeae53')),
    dict(data=bytes.fromhex('80aaaaaaaaaa8c320e33')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaa5a665f8')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaae3f86dfb')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaacb6cc949')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaa61692a74')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaa321fe192')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaa4fc531d')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaa16e56673')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaf27e7229')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaa4dd31ac3')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaae4d3898c')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa7a093f27')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa70f0f079')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab0d03310')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa4032bec4')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaad1bdc2a6')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa08842663')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa13804d87')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa2f309376')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa6fcb36d9')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa80cd17e3')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa3837c3'
               'ba')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa2afb'
               '1017')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa64'
               'fe3d5f')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               '1ff0722c')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aa60be0015')),
    dict(data=bytes.fromhex('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaff5ad9e4')),
    # Skipped from the sequence because they actually are valid encoded
    # secrets:
    #dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    #           'aaaaaa29c70ff0')),
    #dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    #           'aaaaaa010ad26876')),
    # Too long (note that the compression flag is in the right place so we
    # really are just testing length restrictions):
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaa01aa17cbb871')),
    # Incorrect version:
    dict(data=('00aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaa5f664771')),
    dict(data=('81aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaa011209e510')),
    # Invalid compression flag
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaa004156aa8f')),
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaaffbd5d1019')),
]

class TestInvalidSecret(unittest.TestCase):
    __metaclass__ = ScenarioMeta
    class test_invalid_init_with_exponent(ScenarioTest):
        scenarios = INVALID_SECRET
        def __test__(self, data):
            with self.assertRaises(InvalidSecretError):
                Secret(data)
