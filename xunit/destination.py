# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

# Python standard library, unit-testing
import unittest

# Scenario unit-testing
from scenariotest import ScenarioMeta, ScenarioTest

from bitcoin.destination import *
from bitcoin.crypto import VerifyingKey
from bitcoin.script import *
from bitcoin.tools import BytesIO

import bitcoin.base58
import codecs

# ===----------------------------------------------------------------------===

PUBKEY = [
    dict(verifying_key = VerifyingKey.deserialize(BytesIO(
             codecs.decode('muqdFiyLkdVygf59nrWJFwJMHCBhdYdU2tXs8AUz7iWD', 'base58'))),
         script = Script().join([
             ScriptOp(data=bytes.fromhex('029b4b68495bb7cdc737fada24b80adff2b7a08d77424368'
                                         'e7ae56f5f14980b282')),
             ScriptOp(OP_CHECKSIG)])),
    dict(verifying_key = VerifyingKey.deserialize(BytesIO(
             codecs.decode('28kSUszMTVjiXUNNjN8aFMzj4Ztfp36ktAtoPgqUW1Fy7', 'base58'))),
         script = Script().join([
             ScriptOp(data=bytes.fromhex('03d0e86fa3d42ebcd38019e976dd66d32d4339060f705b8f'
                                         '70f407647aa6ff52de')),
             ScriptOp(OP_CHECKSIG)])),
    dict(verifying_key = VerifyingKey.deserialize(BytesIO(
             codecs.decode('QaWyScoeyxXKkPc8C8CBhsGfegd5NxVZGju32yBHEX86'
                           'kw3qEoYo9uu2k4ZtAnyZ6dvBaY2egggd2JujSxZgduW5', 'base58'))),
         script = Script().join([
             ScriptOp(data=bytes.fromhex('049b4b68495bb7cdc737fada24b80adff2b7a08d77424368'
                                         'e7ae56f5f14980b2828013534e6c110c2c596a05eb3453cb'
                                         'dd69be14fece788d6a2e855fb9c96bed36')),
             ScriptOp(OP_CHECKSIG)])),
]

class TestPubKeyDestination(unittest.TestCase):
    __metaclass__ = ScenarioMeta
    class test_pubkey_destination(ScenarioTest):
        scenarios = PUBKEY
        def __test__(self, verifying_key, script):
            id_ = PubKeyId(verifying_key)
            self.assertEqual(id_.verifying_key, verifying_key)
            self.assertEqual(id_.script, script)
            verifying_key.compressed = not verifying_key.compressed
            id_.verifying_key = verifying_key
            self.assertEqual(id_.verifying_key, verifying_key)
            self.assertNotEqual(id_.script, script)

# ===----------------------------------------------------------------------===

PUBKEY_HASH = [
    dict(hash = 0x29769fadffdedd8f594d3b41783bafa427ca46ae,
         script = Script().join([
             ScriptOp(OP_DUP),
             ScriptOp(OP_HASH160),
             ScriptOp(data=bytes.fromhex('ae46ca27a4af3b78413b4d598fdddeffad9f7629')),
             ScriptOp(OP_EQUALVERIFY),
             ScriptOp(OP_CHECKSIG)])),
]

class TestPubKeyHashDestination(unittest.TestCase):
    __metaclass__ = ScenarioMeta
    class test_pubkey_hash_destination(ScenarioTest):
        scenarios = PUBKEY_HASH
        def __test__(self, hash, script):
            id_ = PubKeyHashId(hash)
            self.assertEqual(id_.hash, hash)
            self.assertEqual(id_.script, script)
            hash = 2**160 - 1 - hash
            id_.hash = hash
            self.assertEqual(id_.hash, hash)
            self.assertNotEqual(id_.script, script)

# ===----------------------------------------------------------------------===

SCRIPT_HASH = [
    dict(hash = 0xcb9f3b7c6fb1cf2c13a40637c189bdd066a272b4,
         script = Script().join([
             ScriptOp(OP_HASH160),
             ScriptOp(data=bytes.fromhex('b472a266d0bd89c13706a4132ccfb16f7c3b9fcb')),
             ScriptOp(OP_EQUAL)])),
]

class TestScriptDestination(unittest.TestCase):
    __metaclass__ = ScenarioMeta
    class test_script_destination(ScenarioTest):
        scenarios = SCRIPT_HASH
        def __test__(self, hash, script):
            id_ = ScriptHashId(hash)
            self.assertEqual(id_.hash, hash)
            self.assertEqual(id_.script, script)
            hash = 2**160 - 1 - hash
            id_.hash = hash
            self.assertEqual(id_.hash, hash)
            self.assertNotEqual(id_.script, script)

# End of File
