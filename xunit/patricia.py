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
# Python bitcoin, optimized StringIO
from bitcoin.tools import StringIO
# Python bitcoin, iterator compare
from bitcoin.tools import icmp
# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

from bitcoin.patricia import *

# ===----------------------------------------------------------------------===

class TestPatriciaLink(unittest2.TestCase):
    def test_init(self):
        pn = PatriciaNode()
        pl = PatriciaLink(b'', pn)
        self.assertEqual(pl.prefix, b'')
        self.assertEqual(pl.node, pn)
        pl2 = PatriciaLink(b'\x01', PatriciaNode())
        self.assertEqual(pl2.prefix, b'\x01')
        self.assertEqual(pl2.node, pn)

    def test_eq(self):
        pn = PatriciaNode()
        self.assertEqual(
            PatriciaLink(b'', PatriciaNode()),
            PatriciaLink(b'', PatriciaNode()))
        self.assertNotEqual(
            PatriciaLink(b'abc', PatriciaNode()),
            PatriciaLink(b'', PatriciaNode()))
        self.assertEqual(
            PatriciaLink(b'abc', PatriciaNode()),
            PatriciaLink(b'abc', PatriciaNode()))
        self.assertNotEqual(
            PatriciaLink(b'abc', PatriciaNode()),
            PatriciaLink(b'abc', PatriciaNode(value=b'')))
        self.assertEqual(
            PatriciaLink(b'abc', PatriciaNode(value=b'')),
            PatriciaLink(b'abc', PatriciaNode(value=b'')))

# ===----------------------------------------------------------------------===

class TestPatriciaNode(unittest2.TestCase):
    def test_init(self):
        pn = PatriciaNode()
        self.assertEqual(pn.flags, 0)
        self.assertEqual(pn.value, None)
        self.assertEqual(pn.extra, None)
        self.assertEqual(list(pn.children), [])
        self.assertEqual(pn.hash,
            0x905c0ed9955a5c67b7edc8881fe862fddce009a2294ef8f4ba03834b4aeb7f40)
        pn2 = PatriciaNode(value=b'123')
        self.assertEqual(pn2.flags, PatriciaNode.HAS_VALUE)
        self.assertEqual(pn2.value, b'123')
        self.assertEqual(pn2.extra, None)
        self.assertEqual(list(pn2.children), [])
        self.assertEqual(pn2.hash,
            0x15c6b6b38c63faf012642cefdf729ff2d49336d1e3f65f75f6233d7819f06a2f)
        pl = PatriciaLink(b'abc', pn2)
        pn3 = PatriciaNode(children=[pl])
        self.assertEqual(pn3.flags, 0)
        self.assertEqual(pn3.value, None)
        self.assertEqual(pn3.extra, None)
        self.assertEqual(list(pn3.children), [pl])
        self.assertEqual(pn3.hash,
            0x9b6967124fb421102830af64a04ddcf5498b5c9d75f667464d1259c134ad7c3e)
        pn4 = PatriciaNode(children={b'abc': pn2})
        self.assertEqual(pn4.flags, 0)
        self.assertEqual(pn4.value, None)
        self.assertEqual(pn4.extra, None)
        self.assertEqual(list(pn4.children), [pl])
        self.assertEqual(pn4.hash,
            0x9b6967124fb421102830af64a04ddcf5498b5c9d75f667464d1259c134ad7c3e)
        pn5 = PatriciaNode(b'456', b'', {b'abc': pn2})
        self.assertEqual(pn5.flags, PatriciaNode.HAS_VALUE|PatriciaNode.HAS_EXTRA)
        self.assertEqual(pn5.value, b'456')
        self.assertEqual(pn5.extra, b'')
        self.assertEqual(list(pn4.children), [pl])
        self.assertEqual(pn5.hash,
            0x77c13dd7bb80e7b9a4574e42d23dd6b32f250e376f7a424dfe427fedbf3d393d)

    def test_invalid_init_parameters(self):
        with self.assertRaises(TypeError):
            pn = PatriciaNode(flags=PatriciaNode.HAS_VALUE)
        with self.assertRaises(TypeError):
            pn = PatriciaNode(flags=PatriciaNode.HAS_VALUE, value=None)
        # An older version of PatriciaNode uses hashes for the `value` field.
        # The new code takes binary strings, and rejects integer values to make
        # finding bugs from the conversion process easier:
        with self.assertRaises(TypeError):
            pn = PatriciaNode(flags=PatriciaNode.HAS_VALUE, value=0)
        with self.assertRaises(TypeError):
            pn = PatriciaNode(flags=PatriciaNode.HAS_VALUE,
                value = 0x56944c5d3f98413ef45cf54545538103cc9f298e0575820ad3591376e2e0f65d)

SCENARIOS = [
    dict(value = None, extra = None, children = [],
         str_  = '\x00\x00',
         hash_ = 0x905c0ed9955a5c67b7edc8881fe862fddce009a2294ef8f4ba03834b4aeb7f40),
]

class TestPatriciaNodeSerialization(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, value, extra, children, str_, hash_):
            pn = PatriciaNode(value, extra, children)
            self.assertEqual(pn.serialize(), str_)
            self.assertEqual(pn.hash, hash_)
    class test_deserialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, value, extra, children, str_, hash_):
            pn = PatriciaNode.deserialize(StringIO(str_))
            self.assertEqual(pn.value, value)
            self.assertEqual(pn.extra, extra)
            self.assertEqual(list(pn.children), children)
            self.assertEqual(pn.hash, hash_)

# ===----------------------------------------------------------------------===

SENTINAL = object()

ADDRESS_TO_VALUE = {
    b'':       six.int2byte(1),
    b'abc':    six.int2byte(2),
    b'abcdef': six.int2byte(4),
    b'abcxyz': six.int2byte(8)}
VALUE_TO_ADDRESS = dict(
    (v,k) for k,v in six.iteritems(ADDRESS_TO_VALUE))

SCENARIOS = [
    {
        'hash_':   0x905c0ed9955a5c67b7edc8881fe862fddce009a2294ef8f4ba03834b4aeb7f40,
    },
    {
        b'':       six.int2byte(1),
        'hash_':   0x6738296fcff48401c1fd9bb15eec17b71437148ed763633e91f143e4f1f02054,
    },
    {
        b'abc':    six.int2byte(2),
        'hash_':   0xe8616e6b3ac855f6769633b8dccd1408b5c32ef3a623afaba9c8fc2c4c9fb617,
    },
    {
        b'':       six.int2byte(1),
        b'abc':    six.int2byte(2),
        'hash_':   0x8c4222f0f3235fa0e85401b4ec895c08c6e3e8f9ac5385fbe24214190c0300ae,
    },
    {
        b'abcdef': six.int2byte(4),
        'hash_':   0xc15e1aa3ae5aa69ced4fa1edd7e74acd1fab334e955c309875c1817b2eef6733,
    },
    {
        b'':       six.int2byte(1),
        b'abcdef': six.int2byte(4),
        'hash_':   0xeeaa7f935bf52eeabc7c8d4fe155ce1423bd70a468b365d6fffb6006bb65c023,
    },

    {
        b'abc':    six.int2byte(2),
        b'abcdef': six.int2byte(4),
        'hash_':   0x21286eaeb5bbf3bb3f7d3495e545ecd61c7f45fe44aef7134996feb7daa76e0a,
    },
    {
        b'':       six.int2byte(1),
        b'abc':    six.int2byte(2),
        b'abcdef': six.int2byte(4),
        'hash_':   0x4dfc92218e29086a192d0ef65935a47a850ac5a5b3790d97c47c905bee55f1d8,
    },
    {
        b'abcxyz': six.int2byte(8),
        'hash_':   0xfff045a1793e673d10a62348d4036cdf868c4c5637cffd3edfb13f35f793307d,
    },
    {
        b'':       six.int2byte(1),
        b'abcxyz': six.int2byte(8),
        'hash_':   0x47febbfd9f086b183a606a16b68120f4aa83ee55d939fb0eaaed83841fbfd0db,
    },
    {
        b'abc':    six.int2byte(2),
        b'abcxyz': six.int2byte(8),
        'hash_':   0x7c5c06324dfe4a8179c48ecad83c562a2e6fc1cef169b50864aaf694c5faef00,
    },
    {
        b'':       six.int2byte(1),
        b'abc':    six.int2byte(2),
        b'abcxyz': six.int2byte(8),
        'hash_':   0xd8ddc61b4aae44cce2ce5704872600bdb814de3e1d8146c1f983c44a5bad3481,
    },
    {
        b'abcdef': six.int2byte(4),
        b'abcxyz': six.int2byte(8),
        'hash_':   0xa087ef69c216ab4b6c83fcb5afcec482ff8f8a1712e4c853e969f0c70342e2e2,
    },
    {
        b'':       six.int2byte(1),
        b'abcdef': six.int2byte(4),
        b'abcxyz': six.int2byte(8),
        'hash_':   0x793cb6b433ae8eb85f0b1b2f44546b7c8b37c17c50d1642130020bf6618484e2,
    },
    {
        b'abc':    six.int2byte(2),
        b'abcdef': six.int2byte(4),
        b'abcxyz': six.int2byte(8),
        'hash_':   0x9f841bcaef04c09bec17e0657744fcc53246c6b1d735f0ff232769eba7aaf47e,
    },
    {
        b'':       six.int2byte(1),
        b'abc':    six.int2byte(2),
        b'abcdef': six.int2byte(4),
        b'abcxyz': six.int2byte(8),
        'hash_':   0xf4127860ac4c624216f006ffc7b65b6f0885406fea1aae0c99a8f8841a3a1cab,
    },
]

class TestPatriciaNodeScenarios(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_init_mapping(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = PatriciaNode()
            pn.update(kwargs)
            self.assertEqual(pn.hash, hash_, kwargs)

    class test_init_iterable(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = PatriciaNode()
            pn.update(six.iteritems(kwargs))
            self.assertEqual(pn.hash, hash_, kwargs)

    class test_bool(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = PatriciaNode()
            pn.update(kwargs)
            self.assertEqual(bool(pn), bool(kwargs))

class TestPatriciaNodeScenarios2(unittest2.TestCase):
    def test_lt(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = PatriciaNode()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = PatriciaNode()
                pn2.update(items2)
                self.assertEqual(pn < pn2, cmp(sorted(items), sorted(items2)) < 0)

    def test_le(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = PatriciaNode()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = PatriciaNode()
                pn2.update(items2)
                self.assertEqual(pn <= pn2, cmp(sorted(items), sorted(items2)) <= 0)

    def test_eq(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = PatriciaNode()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = PatriciaNode()
                pn2.update(items2)
                self.assertEqual(pn == pn2, cmp(sorted(items), sorted(items2)) == 0)

    def test_ne(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = PatriciaNode()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = PatriciaNode()
                pn2.update(items2)
                self.assertEqual(pn != pn2, cmp(sorted(items), sorted(items2)) != 0)

    def test_ge(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = PatriciaNode()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = PatriciaNode()
                pn2.update(items2)
                self.assertEqual(pn >= pn2, cmp(sorted(items), sorted(items2)) >= 0)

    def test_gt(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = PatriciaNode()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = PatriciaNode()
                pn2.update(items2)
                self.assertEqual(pn > pn2, cmp(sorted(items), sorted(items2)) > 0)

class TestPatriciaNodeScenarios3(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_len(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = PatriciaNode()
            pn.update(kwargs)
            self.assertEqual(len(pn), len(kwargs))

    class test_size(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = PatriciaNode()
            pn.update(kwargs)
            self.assertEqual(pn.size, len(kwargs))

    class test_length(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = PatriciaNode()
            pn.update(kwargs)
            self.assertEqual(pn.length, len(kwargs))

    class test_iter(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in items), iter(pn)))
            pn2 = PatriciaNode()
            pn2.update(reversed(items))
            self.assertFalse(icmp((k for k,v in items), iter(pn2)))

    class test_reversed(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in reversed(items)), reversed(pn)))
            pn2 = PatriciaNode()
            pn2.update(reversed(items))
            self.assertFalse(icmp((k for k,v in reversed(items)), reversed(pn2)))

    class test_items(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp(items, iter(pn.items())))
    class test_iteritems(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp(items, pn.iteritems()))
            self.assertFalse(icmp(items, six.iteritems(pn)))

    class test_reversed_items(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp(reversed(items), iter(pn.reversed_items())))
    class test_reversed_iteritems(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp(reversed(items), pn.reversed_iteritems()))

    class test_keys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in items), iter(pn.keys())))
    class test_iterkeys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in items), pn.iterkeys()))
            self.assertFalse(icmp((k for k,v in items), six.iterkeys(pn)))

    class test_reversed_keys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp(reversed([k for k,v in items]), iter(pn.reversed_keys())))
    class test_reversed_iterkeys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp(reversed([k for k,v in items]), pn.reversed_iterkeys()))

    class test_values(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp((v for k,v in items), iter(pn.values())))
    class test_itervalues(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp((v for k,v in items), pn.itervalues()))
            self.assertFalse(icmp((v for k,v in items), six.itervalues(pn)))

    class test_reversed_values(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp(reversed([v for k,v in items]), iter(pn.reversed_values())))
    class test_reversed_itervalues(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = PatriciaNode()
            pn.update(items)
            self.assertFalse(icmp(reversed([v for k,v in items]), pn.reversed_itervalues()))

class TestPatriciaNodeScenarios4(unittest2.TestCase):
    def test_contains(self):
        for flags in xrange(16):
            pn = PatriciaNode()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                if flags & ord(value):
                    self.assertIn(key, pn)
                else:
                    self.assertNotIn(key, pn)

    def test_has_key(self):
        for flags in xrange(16):
            pn = PatriciaNode()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                self.assertTrue(pn.has_key(key) == bool(flags & ord(value)))

class TestPatriciaNodeScenarios5(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_getitem(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = PatriciaNode()
            pn.update(kwargs)
            for key,value in six.iteritems(kwargs):
                self.assertEqual(pn[key], kwargs[key])
            with self.assertRaises(KeyError):
                pn['123']

    class test_get(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = PatriciaNode()
            pn.update(kwargs)
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                if key in kwargs:
                    self.assertEqual(pn.get(key), value)
                    self.assertEqual(pn.get(key, SENTINAL), value)
                else:
                    self.assertIs(pn.get(key), None)
                    self.assertIs(pn.get(key, SENTINAL), SENTINAL)

class TestPatriciaNodeScenarios6(unittest2.TestCase):
    def test_update(self):
        for flags in xrange(16):
            pn = PatriciaNode()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for idx,scenario in enumerate(SCENARIOS):
                items = [(k,v) for k,v in six.iteritems(scenario) if k != 'hash_']
                pn2 = PatriciaNode()
                pn2.update(pn)
                self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'])
                pn2.update(items)
                self.assertEqual(pn2.hash, SCENARIOS[flags|idx]['hash_'])

                pn3 = PatriciaNode()
                pn3.update(pn)
                self.assertEqual(pn3.hash, SCENARIOS[flags]['hash_'])
                pn3.update(iter(items))
                self.assertEqual(pn3.hash, SCENARIOS[flags|idx]['hash_'])

                pn4 = PatriciaNode()
                pn4.update(pn)
                self.assertEqual(pn4.hash, SCENARIOS[flags]['hash_'])
                pn4.update(**dict(items))
                self.assertEqual(pn4.hash, SCENARIOS[flags|idx]['hash_'])

    def test_setitem(self):
        for flags in xrange(16):
            pn = PatriciaNode()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pn2 = PatriciaNode()
                pn2.update(pn)
                self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'])
                pn2[key] = value
                self.assertEqual(pn2.hash, SCENARIOS[flags | ord(value)]['hash_'])
                with self.assertRaises(TypeError):
                    pn2[key] = None
                with self.assertRaises(TypeError):
                    pn2[key] = 0
                with self.assertRaises(TypeError):
                    pn2[key] = 0x56944c5d3f98413ef45cf54545538103cc9f298e0575820ad3591376e2e0f65d

    def test_setdefault(self):
        for flags in xrange(16):
            pn = PatriciaNode()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pn2 = PatriciaNode()
                pn2.update(pn)
                if flags & ord(value):
                    pn2.setdefault(key, six.int2byte(ord(value) + 1))
                    self.assertIn(key, pn2)
                    self.assertEqual(pn2[key], value)
                    self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'])
                else:
                    pn2.setdefault(key, value)
                    self.assertIn(key, pn2)
                    self.assertEqual(pn2[key], value)
                    self.assertEqual(pn2.hash, SCENARIOS[flags | ord(value)]['hash_'])

    def test_delete(self):
        for flags in xrange(16):
            pn = PatriciaNode()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for idx,scenario in enumerate(SCENARIOS):
                items = [(k,v) for k,v in six.iteritems(scenario) if k != 'hash_']
                pn2 = PatriciaNode()
                pn2.update(pn)
                self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'])
                pn3 = PatriciaNode()
                pn3.update(pn)
                self.assertEqual(pn3.hash, SCENARIOS[flags]['hash_'])
                for (k,v) in items:
                    if k in SCENARIOS[flags]:
                        pn2.delete([k])
                        pn3.delete(iter([k]))
                    else:
                        with self.assertRaises(KeyError):
                            pn2.delete([k])
                        with self.assertRaises(KeyError):
                            pn3.delete(iter([k]))
                self.assertEqual(pn2.hash, SCENARIOS[flags & ~idx]['hash_'])
                self.assertEqual(pn3.hash, SCENARIOS[flags & ~idx]['hash_'])

    def test_delitem(self):
        for flags in xrange(16):
            pn = PatriciaNode()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pn2 = PatriciaNode()
                pn2.update(pn)
                self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'])
                if key in pn2:
                    del pn2[key]
                else:
                    with self.assertRaises(KeyError):
                        del pn2[key]
                if pn2.hash != SCENARIOS[flags & ~ord(value)]['hash_']:
                    import ipdb
                    ipdb.set_trace()
                self.assertEqual(pn2.hash, SCENARIOS[flags & ~ord(value)]['hash_'])

#
# End of File
#
