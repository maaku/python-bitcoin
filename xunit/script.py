# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

from bitcoin.script import *
from bitcoin.utils import StringIO

COMPRESS_SCRIPT = [
    dict(script=Script([
             ScriptOp(OP_DUP),
             ScriptOp(OP_HASH160),
             ScriptOp(data='ae46ca27a4af3b78413b4d598fdddeffad9f7629'.decode('hex')),
             ScriptOp(OP_EQUALVERIFY),
             ScriptOp(OP_CHECKSIG)]),
         string=b'00ae46ca27a4af3b78413b4d598fdddeffad9f7629'.decode('hex')),
    dict(script=Script([
             ScriptOp(OP_HASH160),
             ScriptOp(data='b472a266d0bd89c13706a4132ccfb16f7c3b9fcb'.decode('hex')),
             ScriptOp(OP_EQUAL)]),
         string=b'01b472a266d0bd89c13706a4132ccfb16f7c3b9fcb'.decode('hex')),
    dict(script=Script([
             ScriptOp(data=('029b4b68495bb7cdc737fada24b80adff2b7a08d77424368'
                            'e7ae56f5f14980b282').decode('hex')),
             ScriptOp(OP_CHECKSIG)]),
         string=(b'029b4b68495bb7cdc737fada24b80adff2b7a08d77424368e7ae56f5f1'
                 b'4980b282').decode('hex')),
    dict(script=Script([
             ScriptOp(data=('03d0e86fa3d42ebcd38019e976dd66d32d4339060f705b8f'
                            '70f407647aa6ff52de').decode('hex')),
             ScriptOp(OP_CHECKSIG)]),
         string=(b'03d0e86fa3d42ebcd38019e976dd66d32d4339060f705b8f70f407647a'
                 b'a6ff52de').decode('hex')),
    dict(script=Script([
             ScriptOp(data=('049b4b68495bb7cdc737fada24b80adff2b7a08d77424368'
                            'e7ae56f5f14980b2828013534e6c110c2c596a05eb3453cb'
                            'dd69be14fece788d6a2e855fb9c96bed36').decode('hex')),
             ScriptOp(OP_CHECKSIG)]),
         string=(b'049b4b68495bb7cdc737fada24b80adff2b7a08d77424368e7ae56f5f1'
                 b'4980b282').decode('hex')),
    dict(script=Script([
             ScriptOp(data=('04d0e86fa3d42ebcd38019e976dd66d32d4339060f705b8f'
                            '70f407647aa6ff52de6ffd9b7778468cfa80657b26ce0a34'
                            'efcd7edc38197c400ced9ab0d619eec77d').decode('hex')),
             ScriptOp(OP_CHECKSIG)]),
         string=(b'05d0e86fa3d42ebcd38019e976dd66d32d4339060f705b8f70f407647a'
                 b'a6ff52de').decode('hex')),
    dict(script=Script([ScriptOp(OP_RETURN)]),
         string=b'076a'.decode('hex')),
]

class TestCompressScript(unittest2.TestCase):
    "Test compression and decompression of scripts."
    __metaclass__ = ScenarioMeta
    class test_compress_script(ScenarioTest):
        scenarios = COMPRESS_SCRIPT
        def __test__(self, script, string):
            file_ = StringIO()
            pickler = ScriptPickler(file_)
            pickler.dump(script)
            self.assertEqual(file_.getvalue(), string)
            file_ = StringIO()
            pickler = ScriptPickler()
            pickler.dump(script, file=file_)
            self.assertEqual(file_.getvalue(), string)
            self.assertEqual(pickler.dumps(script), string)
    class test_decompress_script(ScenarioTest):
        scenarios = COMPRESS_SCRIPT
        def __test__(self, script, string):
            file_ = StringIO(string)
            pickler = ScriptPickler(file_)
            self.assertEqual(pickler.load(), script)
            file_ = StringIO(string)
            pickler = ScriptPickler()
            self.assertEqual(pickler.load(file=file_), script)
            self.assertEqual(pickler.loads(string), script)

#
# End of File
#
