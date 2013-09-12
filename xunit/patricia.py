# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

# Python 2 and 3 compatibility utilities
import six

import gmpy2

# Python standard library, unit-testing
import unittest2
# Scenario unit-testing
from scenariotest import ScenarioMeta, ScenarioTest

from bitcoin.patricia import *
from bitcoin.tools import Bits, StringIO, icmp

# ===----------------------------------------------------------------------===

class TestPatriciaLink(unittest2.TestCase):
    def test_init(self):
        pn = MemoryPatriciaDict()
        pl = PatriciaLink(Bits(), pn)
        self.assertEqual(pl.prefix, Bits())
        self.assertEqual(pl.node, pn)
        pl2 = PatriciaLink(Bits(bytes=b'\x80', length=1), MemoryPatriciaDict())
        self.assertEqual(pl2.prefix.uint, 0x01)
        self.assertEqual(pl2.node, pn)
        pl3 = PatriciaLink(Bits(bytes=b'\x80'), MemoryPatriciaDict())
        self.assertEqual(pl3.prefix.uint, 0x80)
        self.assertEqual(pl3.node, pn)
        pl4 = PatriciaLink(b'\x80', MemoryPatriciaDict())
        self.assertEqual(pl4.prefix.uint, 0x80)
        self.assertEqual(pl4.node, pn)

    def test_eq(self):
        pn = MemoryPatriciaDict()
        self.assertEqual(
            PatriciaLink(b'', MemoryPatriciaDict()),
            PatriciaLink(b'', MemoryPatriciaDict()))
        self.assertNotEqual(
            PatriciaLink(b'abc', MemoryPatriciaDict()),
            PatriciaLink(b'', MemoryPatriciaDict()))
        self.assertEqual(
            PatriciaLink(b'abc', MemoryPatriciaDict()),
            PatriciaLink(b'abc', MemoryPatriciaDict()))
        self.assertNotEqual(
            PatriciaLink(b'abc', MemoryPatriciaDict()),
            PatriciaLink(b'abc', MemoryPatriciaDict(value=b'')))
        self.assertEqual(
            PatriciaLink(b'abc', MemoryPatriciaDict(value=b'')),
            PatriciaLink(b'abc', MemoryPatriciaDict(value=b'')))

# ===----------------------------------------------------------------------===

class TestPatriciaDict(unittest2.TestCase):
    def test_init(self):
        pn = MemoryPatriciaDict()
        self.assertIs(pn.value, None)
        self.assertEqual(icmp(pn.children, iter([])), 0)
        self.assertEqual(pn.hash,
            0x9a538906e6466ebd2617d321f71bc94e56056ce213d366773699e28158e00614)
        pn2 = MemoryPatriciaDict(value=b'123')
        self.assertEqual(pn2.value, b'123')
        self.assertEqual(icmp(pn2.children, iter([])), 0)
        self.assertEqual(pn2.hash,
            0x31d9ef51c7169e064ced0bf759d5b60f1067c12171414b30aae8359f8634a505)
        pl = PatriciaLink(b'abc', pn2)
        pn3 = MemoryPatriciaDict(children=[pl])
        self.assertIs(pn3.value, None)
        self.assertEqual(icmp(pn3.children, iter([pl])), 0)
        self.assertEqual(pn3.hash,
            0x54e70d605c1e8c043ecc062b5c2113958d5be9156bfb7ccdd78d152a716ea8f0)
        pn4 = MemoryPatriciaDict(children={b'abc': pn2})
        self.assertIs(pn4.value, None)
        self.assertEqual(icmp(pn4.children, iter([pl])), 0)
        self.assertEqual(pn4.hash,
            0x54e70d605c1e8c043ecc062b5c2113958d5be9156bfb7ccdd78d152a716ea8f0)
        pn5 = MemoryPatriciaDict(b'456', {b'abc': pn2})
        self.assertEqual(pn5.value, b'456')
        self.assertEqual(icmp(pn4.children, iter([pl])), 0)
        self.assertEqual(pn5.hash,
            0x2d9012770715c0d1b568d9a2a15a2e180fc654906b1a7570632cdc1eb60d6ad4)

    def test_invalid_init_parameters(self):
        # An older version of PatriciaDict uses hashes for the `value` field.
        # The new code takes binary strings, and rejects integer values to make
        # finding bugs from the conversion process easier:
        with self.assertRaises(TypeError):
            pn = MemoryPatriciaDict(0)
        with self.assertRaises(TypeError):
            pn = MemoryPatriciaDict(
                value = 0x56944c5d3f98413ef45cf54545538103cc9f298e0575820ad3591376e2e0f65d)

SCENARIOS = [
    dict(value = None, children = [],
         str_  = '\x00',
         hash_ = 0x9a538906e6466ebd2617d321f71bc94e56056ce213d366773699e28158e00614),
]

class TestPatriciaDictSerialization(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, value, children, str_, hash_):
            pn = MemoryPatriciaDict(value, children)
            self.assertEqual(pn.serialize(), str_)
            self.assertEqual(pn.hash, hash_)
    class test_deserialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, value, children, str_, hash_):
            pn = MemoryPatriciaDict.deserialize(StringIO(str_))
            self.assertEqual(pn.value, value)
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
        'hash_':   0x9a538906e6466ebd2617d321f71bc94e56056ce213d366773699e28158e00614,
    },
    {
        b'':       six.int2byte(1),
        'hash_':   0x6a609a8df822a0f386ae1fb8c2ddf21d5d89ee2d8c33ecb26b93e20f25395b4e,
    },
    {
        b'abc':    six.int2byte(2),
        'hash_':   0xa5b7211b16b848bc9a7fd6b31942ac193203b8f04ad2e843e432d55d5a99826f,
    },
    {
        b'':       six.int2byte(1),
        b'abc':    six.int2byte(2),
        'hash_':   0x414ce0b39054c83c974c2cbfe9b41d9a1a66b131df4b4aaba293af0dd7f0d021,
    },
    {
        b'abcdef': six.int2byte(4),
        'hash_':   0x80650b95a10eda2685ff704a9f4223cf63984f69d299820674a9c681b80cad9c,
    },
    {
        b'':       six.int2byte(1),
        b'abcdef': six.int2byte(4),
        'hash_':   0xbd46cd17793d0665770531a900287824c7e5121ddb8a06af1bc0acdcae0ef80e,
    },

    {
        b'abc':    six.int2byte(2),
        b'abcdef': six.int2byte(4),
        'hash_':   0xf4826935a0dfe20a424337e5b8bbb819b46c90611bd151ad0fcd678256642a05,
    },
    {
        b'':       six.int2byte(1),
        b'abc':    six.int2byte(2),
        b'abcdef': six.int2byte(4),
        'hash_':   0x8c5fcd09790166f8ee1eb9006f8bd0a52d1bcf7c67a080bba97b9462ebe9f896,
    },
    {
        b'abcxyz': six.int2byte(8),
        'hash_':   0x93dedf0cb45949caeb5d51ccc7546230fa95cdd2c151b8fa56be25dba208ab3a,
    },
    {
        b'':       six.int2byte(1),
        b'abcxyz': six.int2byte(8),
        'hash_':   0xd3a22d638ced5fa69af7e0f95037648d314a35fbbbf931053ad0b047217d8ede,
    },
    {
        b'abc':    six.int2byte(2),
        b'abcxyz': six.int2byte(8),
        'hash_':   0xe535258f1a8ef031b6efb28b2240af5599729da915bf67ad9f316cd14dc04bb7,
    },
    {
        b'':       six.int2byte(1),
        b'abc':    six.int2byte(2),
        b'abcxyz': six.int2byte(8),
        'hash_':   0xc63f716e0a0a0dc1eeedb18974dfec42cb3c4c3defe0592d99abee18843070f7,
    },
    {
        b'abcdef': six.int2byte(4),
        b'abcxyz': six.int2byte(8),
        'hash_':   0x8f4ea8888cd8cd396a0a2087ff73fed868bf68227fb7fac681e420c9816bcd36,
    },
    {
        b'':       six.int2byte(1),
        b'abcdef': six.int2byte(4),
        b'abcxyz': six.int2byte(8),
        'hash_':   0x98aa1556d463e0df4f393a04beafacd9029dc59875ec73830433b8f630d79a13,
    },
    {
        b'abc':    six.int2byte(2),
        b'abcdef': six.int2byte(4),
        b'abcxyz': six.int2byte(8),
        'hash_':   0xf23395a33591a3552aee22131cb7356ce3a30d3e59d76650720e12f00ed7b6a9,
    },
    {
        b'':       six.int2byte(1),
        b'abc':    six.int2byte(2),
        b'abcdef': six.int2byte(4),
        b'abcxyz': six.int2byte(8),
        'hash_':   0x7077c51e84687c14128fa0b83c49f7a53cd490318623e5652eee9a289183b13b,
    },
]

class TestPatriciaDictScenarios(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_init_mapping(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaDict()
            pn.update(kwargs)
            self.assertEqual(pn.hash, hash_, kwargs)

    class test_init_iterable(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaDict()
            pn.update(six.iteritems(kwargs))
            self.assertEqual(pn.hash, hash_, kwargs)

    class test_bool(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaDict()
            pn.update(kwargs)
            self.assertEqual(bool(pn), bool(kwargs))

class TestPatriciaDictScenarios2(unittest2.TestCase):
    def test_lt(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaDict()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaDict()
                pn2.update(items2)
                self.assertEqual(pn < pn2, cmp(sorted(items), sorted(items2)) < 0)

    def test_le(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaDict()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaDict()
                pn2.update(items2)
                self.assertEqual(pn <= pn2, cmp(sorted(items), sorted(items2)) <= 0)

    def test_eq(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaDict()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaDict()
                pn2.update(items2)
                self.assertEqual(pn == pn2, cmp(sorted(items), sorted(items2)) == 0)

    def test_ne(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaDict()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaDict()
                pn2.update(items2)
                self.assertEqual(pn != pn2, cmp(sorted(items), sorted(items2)) != 0)

    def test_ge(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaDict()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaDict()
                pn2.update(items2)
                self.assertEqual(pn >= pn2, cmp(sorted(items), sorted(items2)) >= 0)

    def test_gt(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaDict()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaDict()
                pn2.update(items2)
                self.assertEqual(pn > pn2, cmp(sorted(items), sorted(items2)) > 0)

class TestPatriciaDictScenarios3(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_len(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaDict()
            pn.update(kwargs)
            self.assertEqual(len(pn), len(kwargs))

    class test_size(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaDict()
            pn.update(kwargs)
            self.assertEqual(pn.size, len(kwargs))

    class test_length(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaDict()
            pn.update(kwargs)
            self.assertEqual(pn.length, len(kwargs))

    class test_iter(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in items), iter(pn)))
            pn2 = MemoryPatriciaDict()
            pn2.update(reversed(items))
            self.assertFalse(icmp((k for k,v in items), iter(pn2)))

    class test_reversed(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in reversed(items)), reversed(pn)))
            pn2 = MemoryPatriciaDict()
            pn2.update(reversed(items))
            self.assertFalse(icmp((k for k,v in reversed(items)), reversed(pn2)))

    class test_items(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp(items, iter(pn.items())))
    class test_iteritems(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp(items, pn.iteritems()))
            self.assertFalse(icmp(items, six.iteritems(pn)))

    class test_reversed_items(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp(reversed(items), iter(pn.reversed_items())))
    class test_reversed_iteritems(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp(reversed(items), pn.reversed_iteritems()))

    class test_keys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in items), iter(pn.keys())))
    class test_iterkeys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in items), pn.iterkeys()))
            self.assertFalse(icmp((k for k,v in items), six.iterkeys(pn)))

    class test_reversed_keys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp(reversed([k for k,v in items]), iter(pn.reversed_keys())))
    class test_reversed_iterkeys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp(reversed([k for k,v in items]), pn.reversed_iterkeys()))

    class test_values(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp((v for k,v in items), iter(pn.values())))
    class test_itervalues(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp((v for k,v in items), pn.itervalues()))
            self.assertFalse(icmp((v for k,v in items), six.itervalues(pn)))

    class test_reversed_values(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp(reversed([v for k,v in items]), iter(pn.reversed_values())))
    class test_reversed_itervalues(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaDict()
            pn.update(items)
            self.assertFalse(icmp(reversed([v for k,v in items]), pn.reversed_itervalues()))

class TestPatriciaDictScenarios4(unittest2.TestCase):
    def test_contains(self):
        for flags in xrange(16):
            pn = MemoryPatriciaDict()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                if flags & ord(value):
                    self.assertIn(key, pn)
                else:
                    self.assertNotIn(key, pn)

    def test_has_key(self):
        for flags in xrange(16):
            pn = MemoryPatriciaDict()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                self.assertTrue(pn.has_key(key) == bool(flags & ord(value)))

class TestPatriciaDictScenarios5(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_getitem(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaDict()
            pn.update(kwargs)
            for key,value in six.iteritems(kwargs):
                self.assertEqual(pn[key], kwargs[key])
            with self.assertRaises(KeyError):
                pn['123']

    class test_get(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaDict()
            pn.update(kwargs)
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                if key in kwargs:
                    self.assertEqual(pn.get(key), value)
                    self.assertEqual(pn.get(key, SENTINAL), value)
                else:
                    self.assertIs(pn.get(key), None)
                    self.assertIs(pn.get(key, SENTINAL), SENTINAL)

class TestPatriciaDictScenarios6(unittest2.TestCase):
    def test_update(self):
        for flags in xrange(16):
            pn = MemoryPatriciaDict()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for idx,scenario in enumerate(SCENARIOS):
                items = [(k,v) for k,v in six.iteritems(scenario) if k != 'hash_']
                pn2 = MemoryPatriciaDict()
                pn2.update(pn)
                self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'])
                self.assertEqual(pn2.size, gmpy2.popcount(flags))
                self.assertEqual(pn2.length, gmpy2.popcount(flags))
                pn2.update(items)
                self.assertEqual(pn2.hash, SCENARIOS[flags|idx]['hash_'])
                self.assertEqual(pn2.size, gmpy2.popcount(flags|idx))
                self.assertEqual(pn2.length, gmpy2.popcount(flags|idx))

                pn3 = MemoryPatriciaDict()
                pn3.update(pn)
                self.assertEqual(pn3.hash, SCENARIOS[flags]['hash_'])
                self.assertEqual(pn3.size, gmpy2.popcount(flags))
                self.assertEqual(pn3.length, gmpy2.popcount(flags))
                pn3.update(iter(items))
                self.assertEqual(pn3.hash, SCENARIOS[flags|idx]['hash_'])
                self.assertEqual(pn3.size, gmpy2.popcount(flags|idx))
                self.assertEqual(pn3.length, gmpy2.popcount(flags|idx))

                pn4 = MemoryPatriciaDict()
                pn4.update(pn)
                self.assertEqual(pn4.hash, SCENARIOS[flags]['hash_'])
                self.assertEqual(pn4.size, gmpy2.popcount(flags))
                self.assertEqual(pn4.length, gmpy2.popcount(flags))
                pn4.update(**dict(items))
                self.assertEqual(pn4.hash, SCENARIOS[flags|idx]['hash_'])
                self.assertEqual(pn4.size, gmpy2.popcount(flags|idx))
                self.assertEqual(pn4.length, gmpy2.popcount(flags|idx))

    def test_setitem(self):
        for flags in xrange(16):
            pn = MemoryPatriciaDict()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pn2 = MemoryPatriciaDict()
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
            pn = MemoryPatriciaDict()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pn2 = MemoryPatriciaDict()
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
            pn = MemoryPatriciaDict()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for idx,scenario in enumerate(SCENARIOS):
                items = [(k,v) for k,v in six.iteritems(scenario) if k != 'hash_']
                pn2 = MemoryPatriciaDict()
                pn2.update(pn)
                self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'])
                self.assertEqual(pn2.size, gmpy2.popcount(flags))
                self.assertEqual(pn2.length, gmpy2.popcount(flags))
                pn3 = MemoryPatriciaDict()
                pn3.update(pn)
                self.assertEqual(pn3.hash, SCENARIOS[flags]['hash_'])
                self.assertEqual(pn3.size, gmpy2.popcount(flags))
                self.assertEqual(pn3.length, gmpy2.popcount(flags))
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
                self.assertEqual(pn2.size, gmpy2.popcount(flags & ~idx))
                self.assertEqual(pn2.length, gmpy2.popcount(flags & ~idx))
                self.assertEqual(pn3.hash, SCENARIOS[flags & ~idx]['hash_'])
                self.assertEqual(pn3.size, gmpy2.popcount(flags & ~idx))
                self.assertEqual(pn3.length, gmpy2.popcount(flags & ~idx))

    def test_delitem(self):
        for flags in xrange(16):
            pn = MemoryPatriciaDict()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pn2 = MemoryPatriciaDict()
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
