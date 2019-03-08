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

from bitcoin.ledger import *
from bitcoin.core import Output
from bitcoin.destination import PubKeyHashId
from bitcoin.tools import BytesIO

# ===----------------------------------------------------------------------===

class TestUnspentTransaction(unittest.TestCase):
    def test_default_init(self):
        utx = UnspentTransaction()
        self.assertEqual(utx.version, 1)
        self.assertEqual(utx.height, 0)
        self.assertEqual(len(utx), 0)
        self.assertFalse(bool(utx))

    def test_add_outputs(self):
        utx = UnspentTransaction(version=1, height=120891)
        self.assertFalse(bool(utx))

        utx[16] = Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script)
        self.assertEqual(utx.serialize(),
            ('01' '08' '0020'
             'bbd123' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             '86af3b').decode('hex'))

        utx[4] = Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)
        self.assertEqual(utx.serialize(),
            ('01' '08' '0220'
             '86ef97d579' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
             'bbd123'     '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             '86af3b').decode('hex'))

    def test_remove_outputs(self):
        utx = UnspentTransaction((
                (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
                (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script)),
            ), version=1, height=120891)
        self.assertEqual(utx.serialize(),
            ('01' '08' '0220'
             '86ef97d579' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
             'bbd123'     '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             '86af3b').decode('hex'))
        del utx[4]
        self.assertEqual(utx.serialize(),
            ('01' '08' '0020'
             'bbd123' '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             '86af3b').decode('hex'))
        del utx[16]
        with self.assertRaises(TypeError):
            utx.serialize()

        utx = UnspentTransaction((
                (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
                (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script)),
            ), version=1, height=120891)
        self.assertEqual(utx.serialize(),
            ('01' '08' '0220'
             '86ef97d579' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
             'bbd123'     '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
             '86af3b').decode('hex'))
        del utx[16]
        self.assertEqual(utx.serialize(),
            ('01' '00' '02'
             '86ef97d579' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
             '86af3b').decode('hex'))
        del utx[4]
        with self.assertRaises(TypeError):
            utx.serialize()

UNSPENT_TRANSACTION = [
    dict(version=1, height=203998,
         items = ((1, Output(60000000000, PubKeyHashId(0x351d7cf86bb3297fa5cf03c8e77f074e94156181).script)),),
         string = bytes.fromhex('01' '02'
                   '8358' '00816115944e077fe7c803cfa57f29b36bf87c1d35'
                   '8bb85e')),
    dict(version=1, height=120891,
         items = (
             (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
             (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script))),
         string = bytes.fromhex('01' '08' '0220'
                   '86ef97d579' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
                   'bbd123'     '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
                   '86af3b')),
    dict(version=2, height=120891,
         items = (
             (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
             (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script))),
         string = bytes.fromhex('02' '08' '0220'
                   '86ef97d579' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
                   'bbd123'     '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
                   '86af3b' '00')),
    dict(version=2, height=120891, reference_height=1000,
         items = (
             (4, Output(234925952, PubKeyHashId(0xeea463952d3cb47e05a5509c8e1b0fb5aa1cb061).script)),
             (16, Output(110397, PubKeyHashId(0xa4ca55957f7ef1c7aa500f1e16e24d4a1a8f988c).script))),
         string = bytes.fromhex('02' '08' '0220'
                   '86ef97d579' '0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee'
                   'bbd123'     '008c988f1a4a4de2161e0f50aac7f17e7f9555caa4'
                   '86af3b' '8668')),
]

class TestUnspentTransactionScenarios(unittest.TestCase):
    __metaclass__ = ScenarioMeta
    class test_init_from_items(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, height, items, string, **kwargs):
            utx = UnspentTransaction(items, version=version, height=height, **kwargs)
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_init_from_dict(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, height, items, string, **kwargs):
            obj = dict(items)
            utx = UnspentTransaction(obj, version=version, height=height, **kwargs)
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_init_from_other(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, height, items, string, **kwargs):
            obj = UnspentTransaction(items, version=version, height=height, **kwargs)
            utx = UnspentTransaction(obj)
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_init_via_assignment(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, height, items, string, **kwargs):
            utx = UnspentTransaction()
            utx.version = version
            utx.height = height
            if 'reference_height' in kwargs:
                utx.reference_height = kwargs['reference_height']
            for idx,output in items:
                utx[idx] = output
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_init_from_serialization(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, height, items, string, **kwargs):
            utx = UnspentTransaction.deserialize(BytesIO(string))
            self.assertEqual(utx.version, version)
            self.assertEqual(utx.height, height)
            if 'reference_height' in kwargs:
                self.assertEqual(utx.reference_height, kwargs['reference_height'])
            for idx,output in items:
                self.assertIn(idx, utx)
                self.assertEqual(utx[idx], output)
            self.assertEqual(utx.serialize(), string)

    class test_equality(ScenarioTest):
        scenarios = UNSPENT_TRANSACTION
        def __test__(self, version, height, items, string, **kwargs):
            utx1 = UnspentTransaction.deserialize(BytesIO(string))
            utx2 = UnspentTransaction.deserialize(BytesIO(string))
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
