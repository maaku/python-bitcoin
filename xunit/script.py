# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

# Python standard library, unit-testing
import unittest

# Scenario unit-testing
from scenariotest import ScenarioMeta, ScenarioTest

from bitcoin.script import *
from bitcoin.tools import BytesIO

COMPRESS_SCRIPT = [
    dict(script=Script().join([
             ScriptOp(OP_DUP),
             ScriptOp(OP_HASH160),
             ScriptOp(data=bytes.fromhex('ae46ca27a4af3b78413b4d598fdddeffad9f7629')),
             ScriptOp(OP_EQUALVERIFY),
             ScriptOp(OP_CHECKSIG)]),
         string=bytes.fromhex('00ae46ca27a4af3b78413b4d598fdddeffad9f7629')),
    dict(script=Script().join([
             ScriptOp(OP_HASH160),
             ScriptOp(data=bytes.fromhex('b472a266d0bd89c13706a4132ccfb16f7c3b9fcb')),
             ScriptOp(OP_EQUAL)]),
         string=bytes.fromhex('01b472a266d0bd89c13706a4132ccfb16f7c3b9fcb')),
    dict(script=Script().join([
             ScriptOp(data=bytes.fromhex('029b4b68495bb7cdc737fada24b80adff2b7a08d77424368'
                                         'e7ae56f5f14980b282')),
             ScriptOp(OP_CHECKSIG)]),
         string=bytes.fromhex('029b4b68495bb7cdc737fada24b80adff2b7a08d77424368e7ae56f5f1'
                              '4980b282')),
    dict(script=Script().join([
             ScriptOp(data=bytes.fromhex('03d0e86fa3d42ebcd38019e976dd66d32d4339060f705b8f'
                                         '70f407647aa6ff52de')),
             ScriptOp(OP_CHECKSIG)]),
         string=bytes.fromhex('03d0e86fa3d42ebcd38019e976dd66d32d4339060f705b8f70f407647a'
                              'a6ff52de')),
    dict(script=Script().join([
             ScriptOp(data=bytes.fromhex('049b4b68495bb7cdc737fada24b80adff2b7a08d77424368'
                                         'e7ae56f5f14980b2828013534e6c110c2c596a05eb3453cb'
                                         'dd69be14fece788d6a2e855fb9c96bed36')),
             ScriptOp(OP_CHECKSIG)]),
         string=bytes.fromhex('049b4b68495bb7cdc737fada24b80adff2b7a08d77424368e7ae56f5f1'
                              '4980b282')),
    dict(script=Script().join([
             ScriptOp(data=bytes.fromhex('04d0e86fa3d42ebcd38019e976dd66d32d4339060f705b8f'
                                         '70f407647aa6ff52de6ffd9b7778468cfa80657b26ce0a34'
                                         'efcd7edc38197c400ced9ab0d619eec77d')),
             ScriptOp(OP_CHECKSIG)]),
         string=bytes.fromhex('05d0e86fa3d42ebcd38019e976dd66d32d4339060f705b8f70f407647a'
                              'a6ff52de')),
    dict(script=Script().join([ScriptOp(OP_RETURN)]),
         string=bytes.fromhex('076a')),
]

class TestCompressScript(unittest.TestCase):
    "Test compression and decompression of scripts."
    __metaclass__ = ScenarioMeta
    class test_compress_script(ScenarioTest):
        scenarios = COMPRESS_SCRIPT
        def __test__(self, script, string):
            file_ = BytesIO()
            pickler = ScriptPickler(file_)
            pickler.dump(script)
            self.assertEqual(file_.getvalue(), string)
            file_ = BytesIO()
            pickler = ScriptPickler()
            pickler.dump(script, file=file_)
            self.assertEqual(file_.getvalue(), string)
            self.assertEqual(pickler.dumps(script), string)
    class test_decompress_script(ScenarioTest):
        scenarios = COMPRESS_SCRIPT
        def __test__(self, script, string):
            file_ = BytesIO(string)
            pickler = ScriptPickler(file_)
            self.assertEqual(pickler.load(), script)
            file_ = BytesIO(string)
            pickler = ScriptPickler()
            self.assertEqual(pickler.load(file=file_), script)
            self.assertEqual(pickler.loads(string), script)
