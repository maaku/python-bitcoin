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

from bitcoin.crypto import *
from bitcoin.serialize import serialize_beint

# ===----------------------------------------------------------------------===

MERKLE_LIST = [
    dict(list_=[], root=0),
    dict(list_=[0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33bL],
         root=0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33bL),
    dict(list_=[0x50671f9e3b0719fcd23b2976eedf6e0a6f19ae7a8f023c3e66b9b1fbe207a006L,
                0x603b9dbb388987175f8ddbdae9a8ad77a999e63b356e6172b331905387b515f7L,
                0xec258956c3069ea974a569fbacd320fd183d65fa6d4c318ad4e55da6260c0f3dL],
         root=0x5d438b61fa23d20bfac0a6eaf5c426e2abdd48637c7dd70a620b0b7ab7cd6092L),
    dict(list_=[0x9156235baa55ea841c4384faa543004fd5a56661d22dfbc2bbd5313c85044e08L,
                0xc6f50393c676f1f3b669c93f62c3f0e46349f6d2aff13ed8976bd649382ff6fcL,
                0x4817fad15ce7604ae5a478888a29b4ade8000596a0e9267747b1d4f0bd1a6defL,
                0x16952eba67618e90857d530a63477ea09dd89575ac00c114e20e8068b4e0297cL],
         root=0xb1cd750f2a242deeaf3b452aa69a4a46f9f66e866c07eda22677f1287688bb1eL),
]

class TestMerkle(unittest2.TestCase):
    "Test merkle API under a variety of scenarios."
    __metaclass__ = ScenarioMeta
    class test_merkle_root(ScenarioTest):
        scenarios = MERKLE_LIST
        def __test__(self, list_, root):
            self.assertEqual(merkle(list_), root)

NESTED_MERKLE = [
    dict(list_=[0x67050eeb5f95abf57449d92629dcf69f80c26247e207ad006a862d1e4e6498ffL,
                [0x9c2e4d8fe97d881430de4e754b4205b9c27ce96715231cffc4337340cb110280L,
                 [0x0c08173828583fc6ecd6ecdbcca7b6939c49c242ad5107e39deb7b0a5996b903L],
                 0x80903da4e6bbdf96e8ff6fc3966b0cfd355c7e860bdd1caa8e4722d9230e40acL],
                0x5a9eab9148389395eff050ddf00220d722123ca8736c862bf200316389b3f611L,
                0xb2928391f8a477a27749a556b7386f4da4391e98df1c76459ba7f4ac2ee1a8f7L,
                [0x93f620df2bb7d859378709f71b820725ef54d985e86662c51027ccfd18d66208L,
                 [0x68b6acce6948c45ed26e193c33443b4aedc1c25e6f96e29a3d939a774f8b74d1L,
                  0xa8e26fa85a95a531ebd98b4454d17790430cc4a11ce157e2ad051f7c3c128ce8L],
                 0x9823a2989686ae381368f8f461f09a146f65b9a60c33592ca9613bcebe9abce0L],
                [0xbf5d3affb73efd2ec6c36ad3112dd933efed63c4e1cbffcfa88e2759c144f2d8L,
                 0x39361160903c6695c6804b7157c7bd10013e9ba89b1f954243bc8e3990b08db9L],
                0x6632753d6ca30fea890f37fc150eaed8d068acf596acb2251b8fafd72db977d3L],
         root=0x681ac33995f3421e8302a55cf929b9d84031cf5f5bb6ec5898435b6dbdb5455fL),
]

class TestNestedMerkle(unittest2.TestCase):
    "Test merkle API using explicit (version=2) Merkle trees."
    __metaclass__ = ScenarioMeta
    class test_nested_merkle_root(ScenarioTest):
        scenarios = NESTED_MERKLE
        def __test__(self, list_, root):
            self.assertEqual(merkle(list_), root)

# ===----------------------------------------------------------------------===

HASH160 = [
    dict(data  = b'',
         hash_ = 0xcb9f3b7c6fb1cf2c13a40637c189bdd066a272b4),
    dict(data  = b'abc',
         hash_ = 0x33dce478a942391c98a36aa5d74424148ce91bbb),
    dict(data  = ('BGeK/bD+VUgnGWfxpnEwtxBc1qgo4DkJpnli4OofYd62Sfa8P0zvOMTzVQTlHsES3lw4Tfe6C41X'
                  'ikxwK2vxHV8=').decode('base64'),
         hash_ = 0x188fb8eb50fbf0f6eb995342d527bf5cb107e962),
]

class TestHash160(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_hash160(ScenarioTest):
        scenarios = HASH160
        def __test__(self, data, hash_):
            self.assertEqual(hash160(data).intdigest(), hash_)

# ===----------------------------------------------------------------------===

HASH256 = [
    dict(data  = b'',
         hash_ = 0x56944c5d3f98413ef45cf54545538103cc9f298e0575820ad3591376e2e0f65d),
    dict(data  = b'abc',
         hash_ = 0x58636c3ec08c12d55aedda056d602d5bcca72d8df6a69b519b72d32dc2428b4f),
    dict(data  = ('AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAO6Pt/Xp7ErJ6xyw+Z3aPYX/IG8OI'
                  'ilEyOp+4qkseXkopq19J//8AHR2sK3w=').decode('base64'),
         hash_ = 0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f),
]

class TestHash256(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_hash256(ScenarioTest):
        scenarios = HASH256
        def __test__(self, data, hash_):
            self.assertEqual(hash256(data).intdigest(), hash_)

# ===----------------------------------------------------------------------===

class TestSECP256k1(unittest2.TestCase):
    def test_name(self):
        self.assertEqual(SECP256k1.name, 'SECP256k1')
    def test_order(self):
        self.assertEqual(SECP256k1.order,
            0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141l)

# ===----------------------------------------------------------------------===

SECRET = [
    dict(exponent=0x12b004fff7f4b69ef8650e767f18f11ede158148b425660723b9f9a66e61f747,
         secret=('8012b004fff7f4b69ef8650e767f18f11ede158148b425660723b9f9a66e61f747'
                 'ef4604d4').decode('hex'),
         compressed_secret=('8012b004fff7f4b69ef8650e767f18f11ede158148b42566'
                            '0723b9f9a66e61f747017555cd1c').decode('hex')),
]

class TestSecret(unittest2.TestCase):
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
                    serialize_beint(exponent, 32),
                    secret[-4:]]), compressed=False)
            with self.assertRaises(InvalidSecretError):
                Secret(b''.join([
                    six.int2byte(0x80),
                    serialize_beint(exponent, 32),
                    secret[-4:]]), compressed=True)
            obj = Secret(b''.join([
                six.int2byte(0x80),
                serialize_beint(exponent, 32),
                secret[-4:]]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            with self.assertRaises(InvalidSecretError):
                Secret(b''.join([
                    six.int2byte(0x80),
                    serialize_beint(exponent, 32),
                    six.int2byte(0x01),
                    compressed_secret[-4:]]), compressed=False)
            with self.assertRaises(InvalidSecretError):
                Secret(b''.join([
                    six.int2byte(0x80),
                    serialize_beint(exponent, 32),
                    six.int2byte(0x01),
                    compressed_secret[-4:]]), compressed=True)
            obj = Secret(b''.join([
                six.int2byte(0x80),
                serialize_beint(exponent, 32),
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
                    serialize_beint(exponent, 32),
                    secret[-4:]]))
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=True, data=b''.join([
                    six.int2byte(0x80),
                    serialize_beint(exponent, 32),
                    secret[-4:]]))
            obj = Secret(data=b''.join([
                six.int2byte(0x80),
                serialize_beint(exponent, 32),
                secret[-4:]]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            obj = Secret(add_hash=False, data=b''.join([
                six.int2byte(0x80),
                serialize_beint(exponent, 32),
                secret[-4:]]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            obj = Secret(add_hash=True, data=b''.join([
                six.int2byte(0x80),
                serialize_beint(exponent, 32)]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=True, data=b''.join([
                    six.int2byte(0x80),
                    serialize_beint(exponent, 32),
                    six.int2byte(0x01),
                    compressed_secret[-4:]]))
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=False, data=b''.join([
                    six.int2byte(0x80),
                    serialize_beint(exponent, 32),
                    six.int2byte(0x01),
                    compressed_secret[-4:]]))
            obj = Secret(data=b''.join([
                six.int2byte(0x80),
                serialize_beint(exponent, 32),
                six.int2byte(0x01),
                compressed_secret[-4:]]))
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)
            obj = Secret(add_hash=False, data=b''.join([
                six.int2byte(0x80),
                serialize_beint(exponent, 32),
                six.int2byte(0x01),
                compressed_secret[-4:]]))
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)
            obj = Secret(add_hash=True, data=b''.join([
                    six.int2byte(0x80),
                    serialize_beint(exponent, 32),
                    six.int2byte(0x01)]))
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)

    class test_init_from_payload(ScenarioTest):
        scenarios = SECRET
        def __test__(self, exponent, secret, compressed_secret):
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=False, payload=b''.join([
                    serialize_beint(exponent, 32)]))
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=True, payload=b''.join([
                    serialize_beint(exponent, 32)]))
            obj = Secret(payload=b''.join([serialize_beint(exponent, 32)]))
            self.assertEqual(obj, secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertFalse(obj.compressed)
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=False, payload=b''.join([
                    serialize_beint(exponent, 32),
                    six.int2byte(0x01)]))
            with self.assertRaises(InvalidSecretError):
                Secret(compressed=True, payload=b''.join([
                    serialize_beint(exponent, 32),
                    six.int2byte(0x01)]))
            obj = Secret(payload=b''.join([
                serialize_beint(exponent, 32),
                six.int2byte(0x01)]))
            self.assertEqual(obj, compressed_secret)
            self.assertEqual(obj.exponent, exponent)
            self.assertTrue(obj.compressed)

class TestInvalidSecret(unittest2.TestCase):
    def test_zero_exponent(self):
        with self.assertRaises(InvalidSecretError):
            Secret(0)
    def test_zero_exponent_modulo_order(self):
        with self.assertRaises(InvalidSecretError):
            Secret(SECP256k1.order)

INVALID_SECRET = [
    # Too short:
    dict(data='80c9403978'.decode('hex')),
    dict(data='80aaa39001da'.decode('hex')),
    dict(data='80aaaa4aed84b5'.decode('hex')),
    dict(data='80aaaaaac05059f9'.decode('hex')),
    dict(data='80aaaaaaaacefeae53'.decode('hex')),
    dict(data='80aaaaaaaaaa8c320e33'.decode('hex')),
    dict(data='80aaaaaaaaaaaaa5a665f8'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaae3f86dfb'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaacb6cc949'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaa61692a74'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaa321fe192'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaa4fc531d'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaa16e56673'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaf27e7229'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaa4dd31ac3'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaae4d3898c'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa7a093f27'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa70f0f079'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab0d03310'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa4032bec4'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaad1bdc2a6'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa08842663'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa13804d87'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa2f309376'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa6fcb36d9'.decode('hex')),
    dict(data='80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa80cd17e3'.decode('hex')),
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa3837c3'
               'ba').decode('hex')),
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa2afb'
               '1017').decode('hex')),
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa64'
               'fe3d5f').decode('hex')),
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               '1ff0722c').decode('hex')),
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aa60be0015').decode('hex')),
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaff5ad9e4').decode('hex')),
    # Skipped from the sequence because they actually are valid encoded
    # secrets:
    #dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    #           'aaaaaa29c70ff0').decode('hex')),
    #dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    #           'aaaaaa010ad26876').decode('hex')),
    # Too long (note that the compression flag is in the right place so we
    # really are just testing length restrictions):
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaa01aa17cbb871').decode('hex')),
    # Incorrect version:
    dict(data=('00aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaa5f664771').decode('hex')),
    dict(data=('81aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaa011209e510').decode('hex')),
    # Invalid compression flag
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaa004156aa8f').decode('hex')),
    dict(data=('80aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
               'aaaaaaffbd5d1019').decode('hex')),
]

class TestInvalidSecret(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_invalid_init_with_exponent(ScenarioTest):
        scenarios = INVALID_SECRET
        def __test__(self, data):
            with self.assertRaises(InvalidSecretError):
                Secret(data)

#
# End of File
#
