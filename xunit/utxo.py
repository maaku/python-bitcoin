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

from bitcoin.utxo import *
from bitcoin.core import Output
from bitcoin.destination import PubKeyHashId
from bitcoin.tools import StringIO

# ===----------------------------------------------------------------------===

class TestUnspentTransaction(unittest2.TestCase):
    def test_default_init(self):
        utx = UnspentTransaction()
        self.assertEqual(utx.version, 1)
        self.assertFalse(utx.is_coinbase)
        self.assertEqual(utx.height, 0)
        self.assertEqual(len(utx), 0)
        self.assertFalse(bool(utx))

    def test_add_outputs(self):
        utx = UnspentTransaction(version=1, coinbase=True, height=120891)
        self.assertFalse(bool(utx))

        utx[16] = Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script)
        self.assertEqual(utx.serialize(),
            ('01' '09' '0040'
             'fe23290f00' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             'fe3bd80100').decode('hex'))

        utx[4] = Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)
        self.assertEqual(utx.serialize(),
            ('01' '09' '0440'
             'fe792b067e' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
             'fe23290f00' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             'fe3bd80100').decode('hex'))

    def test_remove_outputs(self):
        utx = UnspentTransaction((
                (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
                (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script)),
            ), version=1, coinbase=True, height=120891)
        self.assertEqual(utx.serialize(),
            ('01' '09' '0440'
             'fe792b067e' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
             'fe23290f00' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             'fe3bd80100').decode('hex'))
        del utx[4]
        self.assertEqual(utx.serialize(),
            ('01' '09' '0040'
             'fe23290f00' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             'fe3bd80100').decode('hex'))
        del utx[16]
        with self.assertRaises(TypeError):
            utx.serialize()

        utx = UnspentTransaction((
                (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
                (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script)),
            ), version=1, coinbase=True, height=120891)
        self.assertEqual(utx.serialize(),
            ('01' '09' '0440'
             'fe792b067e' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
             'fe23290f00' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             'fe3bd80100').decode('hex'))
        del utx[16]
        self.assertEqual(utx.serialize(),
            ('01' '01' '04'
             'fe792b067e' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
             'fe3bd80100').decode('hex'))
        del utx[4]
        with self.assertRaises(TypeError):
            utx.serialize()

UNSPENT_TRANSACTION = [
    dict(version=1, coinbase=False, height=203998,
         items = ((1, Output(60000000000, PubKeyHashId(0x351d7cf86bb3297fa5cf03c8e77f074e94156181).script)),),
         string = ('01' '04'
                   'fd5802' '00816115944e077fe7c803cfa57f29b36bf87c1d35'
                   'fede1c0300').decode('hex')),
    dict(version=1, coinbase=True, height=120891,
         items = (
             (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
             (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script))),
         string = ('01' '09' '0440'
                   'fe792b067e' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
                   'fe23290f00' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
                   'fe3bd80100').decode('hex')),
    dict(version=2, coinbase=True, height=120891,
         items = (
             (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
             (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script))),
         string = ('02' '09' '0440'
                   'fe792b067e' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
                   'fe23290f00' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
                   'fe3bd80100' '00').decode('hex')),
    dict(version=2, coinbase=True, height=120891, reference_height=1000,
         items = (
             (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
             (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script))),
         string = ('02' '09' '0440'
                   'fe792b067e' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
                   'fe23290f00' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
                   'fe3bd80100' 'fde803').decode('hex')),
]

class TestUnspentTransactionScenarios(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_init_from_items(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, coinbase, height, items, string, **kwargs):
            utx = UnspentTransaction(items, version=version, coinbase=coinbase,
                                     height=height, **kwargs)
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.is_coinbase, coinbase)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_init_from_dict(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, coinbase, height, items, string, **kwargs):
            obj = dict(items)
            utx = UnspentTransaction(obj, version=version, coinbase=coinbase,
                                     height=height, **kwargs)
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.is_coinbase, coinbase)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_init_from_other(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, coinbase, height, items, string, **kwargs):
            obj = UnspentTransaction(items, version=version, coinbase=coinbase,
                                     height=height, **kwargs)
            utx = UnspentTransaction(obj)
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.is_coinbase, coinbase)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_init_via_assignment(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, coinbase, height, items, string, **kwargs):
            utx = UnspentTransaction()
            utx.version = version
            utx.is_coinbase = coinbase
            utx.height = height
            if 'reference_height' in kwargs:
                utx.reference_height = kwargs['reference_height']
            for idx,output in items:
                utx[idx] = output
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.is_coinbase, coinbase)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_init_from_serialization(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, coinbase, height, items, string, **kwargs):
            utx = UnspentTransaction.deserialize(StringIO(string))
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.is_coinbase, coinbase)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_equality(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, coinbase, height, items, string, **kwargs):
            utx1 = UnspentTransaction.deserialize(StringIO(string))
            utx2 = UnspentTransaction.deserialize(StringIO(string))
            self.assertTrue(utx1 == utx2)
            self.assertFalse(utx1 != utx2)
            self.assertEqual(utx1.serialize(), utx2.serialize())

            utx2.version = version - 1
            self.assertFalse(utx1 == utx2)
            self.assertTrue(utx1 != utx2)
            self.assertNotEqual(utx1.serialize(), utx2.serialize())
            utx2.version = version
            self.assertTrue(utx1 == utx2)
            self.assertEqual(utx1.serialize(), utx2.serialize())

            utx2.is_coinbase = not coinbase
            self.assertFalse(utx1 == utx2)
            self.assertTrue(utx1 != utx2)
            self.assertNotEqual(utx1.serialize(), utx2.serialize())
            utx2.is_coinbase = coinbase

            utx2.height = height + 1
            self.assertFalse(utx1 == utx2)
            self.assertTrue(utx1 != utx2)
            self.assertNotEqual(utx1.serialize(), utx2.serialize())
            utx2.height = height

            if version in (2,):
                utx2.reference_height = height - 1
                self.assertFalse(utx1 == utx2)
                self.assertTrue(utx1 != utx2)
                self.assertNotEqual(utx1.serialize(), utx2.serialize())
                utx2.reference_height = utx1.reference_height
            self.assertTrue(utx1 == utx2)
            self.assertEqual(utx1.serialize(), utx2.serialize())

            del utx2[next(six.iterkeys(utx2))]
            if utx2:
                self.assertFalse(utx1 == utx2)
                self.assertTrue(utx1 != utx2)
                self.assertNotEqual(utx1.serialize(), utx2.serialize())

#
# End of File
#
