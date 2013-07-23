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
        pl = PatriciaLink()
        self.assertEqual(pl.prefix, b'')
        self.assertEqual(pl.hash, 0)
        pl2 = PatriciaLink(prefix=b'abc')
        self.assertEqual(pl2.prefix, b'abc')
        self.assertEqual(pl2.hash, 0)
        pl3 = PatriciaLink(hash=123)
        self.assertEqual(pl3.prefix, b'')
        self.assertEqual(pl3.hash, 123)
        pl4 = PatriciaLink(b'\x01', 12345678901234567890)
        self.assertEqual(pl4.prefix, b'\x01')
        self.assertEqual(pl4.hash, 12345678901234567890L)

    def test_eq(self):
        pl = PatriciaLink()
        pl2 = PatriciaLink()
        self.assertTrue(pl == pl2)
        pl.prefix = b'abc'
        self.assertFalse(pl == pl2)
        pl2.prefix = b'abc'
        self.assertTrue(pl == pl2)
        pl2.hash = 123
        self.assertFalse(pl == pl2)
        pl.hash = 123
        self.assertTrue(pl == pl2)

SCENARIOS = [
    dict(prefix=b'',    hash_=  0, str_='\x00'   +    '\x00'*32),
    dict(prefix=b'abc', hash_=123, str_='\x03abc'+'{'+'\x00'*31),
]

class TestPatriciaLinkSerialization(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, prefix, hash_, str_):
            pl = PatriciaLink(prefix=prefix, hash=hash_)
            self.assertEqual(pl.serialize(), str_)
    class test_deserialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, prefix, hash_, str_):
            pl = PatriciaLink.deserialize(StringIO(str_))
            self.assertEqual(pl.prefix, prefix)
            self.assertEqual(pl.hash, hash_)

# ===----------------------------------------------------------------------===

class TestPatriciaNode(unittest2.TestCase):
    def test_init(self):
        pn = PatriciaNode()
        self.assertEqual(pn.flags, 0)
        self.assertEqual(pn.value, None)
        self.assertEqual(list(pn.children), [])
        self.assertEqual(pn.hash,
            0x905c0ed9955a5c67b7edc8881fe862fddce009a2294ef8f4ba03834b4aeb7f40)
        pn2 = PatriciaNode(flags=PatriciaNode.HAS_VALUE, value=123)
        self.assertEqual(pn2.flags, PatriciaNode.HAS_VALUE)
        self.assertEqual(pn2.value, 123)
        self.assertEqual(list(pn2.children), [])
        self.assertEqual(pn2.hash,
            0xca0bc612fa3efc2e6b01e8808549c4a99e133d7f1921fee8ade570f73f8974a5)
        pl = PatriciaLink(prefix='abc', hash=
            0xca0bc612fa3efc2e6b01e8808549c4a99e133d7f1921fee8ade570f73f8974a5)
        pn3 = PatriciaNode(children=[pl])
        self.assertEqual(pn.flags, 0)
        self.assertEqual(pn.value, None)
        self.assertEqual(list(pn3.children), [pl])
        self.assertEqual(pn3.hash,
            0x22e7316f8e5b6f7cdc6fa87d7b89914bedb43fac39bde19f5874056948a55ead)
        pn4 = PatriciaNode(children={b'abc': pn2})
        self.assertEqual(pn.flags, 0)
        self.assertEqual(pn.value, None)
        self.assertEqual(list(pn4.children), [pl])
        self.assertEqual(pn4.hash,
            0x22e7316f8e5b6f7cdc6fa87d7b89914bedb43fac39bde19f5874056948a55ead)
        pn5 = PatriciaNode(PatriciaNode.HAS_VALUE, {b'abc': pn2}, 456)
        self.assertEqual(pn5.flags, PatriciaNode.HAS_VALUE)
        self.assertEqual(pn5.value, 456)
        self.assertEqual(list(pn4.children), [pl])
        self.assertEqual(pn5.hash,
            0x2f7bc4b0af5e97ad8bf5fd07f526c612a23bcea17dd773a1c73654b6a5ea3a89)

    def test_children_clear(self):
        pn = PatriciaNode(flags=PatriciaNode.HAS_VALUE, value=123)
        pn2 = PatriciaNode(PatriciaNode.HAS_VALUE, {b'abc': pn}, 123)
        self.assertNotEqual(pn, pn2)
        self.assertEqual(pn2.hash,
            0x462d170c8f53c13cb0f01cdd09542f498ce28a17dbabc82354cf214bedab2425)
        pn2.children_clear()
        self.assertEqual(pn, pn2)
        self.assertEqual(pn2.hash,
            0xca0bc612fa3efc2e6b01e8808549c4a99e133d7f1921fee8ade570f73f8974a5)

SCENARIOS = [
    dict(flags = 0, children = [], value = None,
         str_  = '\x00\x00',
         hash_ = 0x905c0ed9955a5c67b7edc8881fe862fddce009a2294ef8f4ba03834b4aeb7f40),
]

class TestPatriciaLinkSerialization(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, flags, children, value, str_, hash_):
            pn = PatriciaNode(flags, children, value)
            self.assertEqual(pn.serialize(), str_)
            self.assertEqual(pn.hash, hash_)
    class test_deserialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, flags, children, value, str_, hash_):
            pn = PatriciaNode.deserialize(StringIO(str_))
            self.assertEqual(pn.flags, flags)
            self.assertEqual(list(pn.children), children)
            self.assertEqual(pn.value, value)
            self.assertEqual(pn.hash, hash_)

# ===----------------------------------------------------------------------===

ADDRESS_TO_VALUE = {
    b'':       1,
    b'abc':    2,
    b'abcdef': 4,
    b'abcxyz': 8}
VALUE_TO_ADDRESS = dict(
    (v,k) for k,v in six.iteritems(ADDRESS_TO_VALUE))

SCENARIOS = [
    {
        'hash_':   0x905c0ed9955a5c67b7edc8881fe862fddce009a2294ef8f4ba03834b4aeb7f40,
    },
    {
        b'':       1,
        'hash_':   0xc30f427122cc07de7a58eaf32d4c776c994466bdcc0d2c8c3e554eed637b4e85,
    },
    {
        b'abc':    2,
        'hash_':   0xe1b2f2b9ab90c51f3c4b8c7dd6219b700d5ea1fe9455f1656e9a5f9fd17a6805,
    },
    {
        b'':       1,
        b'abc':    2,
        'hash_':   0x8e15d89142ae1fe00d6815cd31cbad9b663ace5e95eb48c1f08c160eea60b4fd,
    },
    {
        b'abcdef': 4,
        'hash_':   0x291f6d8c77634293c9f462b9c1864a4377fd1a22ef2b9294f2ea842870310f1d,
    },
    {
        b'':       1,
        b'abcdef': 4,
        'hash_':   0xa01b7adfabb9f125f7d358a876071d0352cb667f26800e37c0f9fdb7c842f445,
    },

    {
        b'abc':    2,
        b'abcdef': 4,
        'hash_':   0x1650887f156e982f62c7090b771dd5783418e3ed665ccd9675cb14580549ac4d,
    },
    {
        b'':       1,
        b'abc':    2,
        b'abcdef': 4,
        'hash_':   0xc0f7bd54fd6fb5d230d86a71fdb53ebd76659016602efde3d9c6b4089b02bc27,
    },
    {
        b'abcxyz': 8,
        'hash_':   0xbcd0f62ab44b53ed1b81743e18d9519d86526af2a95de93fe0078865bfb6aca9,
    },
    {
        b'':       1,
        b'abcxyz': 8,
        'hash_':   0xa041b1ca0069fc172c2113ddda9368b0b669066471f9322c9c186d4df019257f,
    },
    {
        b'abc':    2,
        b'abcxyz': 8,
        'hash_':   0x4c02ecde5f642056a5e32aaf93c2ad51e0ee6c77cbac6e2e0014c0de0f038f16,
    },
    {
        b'':       1,
        b'abc':    2,
        b'abcxyz': 8,
        'hash_':   0x0e17b07f0f1587c9310cd9fccafa8f732a178809bd319f995bc7bbf8caadc052,
    },
    {
        b'abcdef': 4,
        b'abcxyz': 8,
        'hash_':   0x9e13f0340135b60e4cfda1976b484a638fa74b435be2ab69ecf908332329d1a8,
    },
    {
        b'':       1,
        b'abcdef': 4,
        b'abcxyz': 8,
        'hash_':   0x89151732bd6fe0e003fcc395341646530d4ca0c9413b6abe7d9b034212ec6468,
    },
    {
        b'abc':    2,
        b'abcdef': 4,
        b'abcxyz': 8,
        'hash_':   0x223d74d441e6db4d307295054a7ed836cd99586cbf131f714128b440b7792e3e,
    },
    {
        b'':       1,
        b'abc':    2,
        b'abcdef': 4,
        b'abcxyz': 8,
        'hash_':   0x5d12bf723aafaeb306f957a9d0820ee1f167a90ed6c57e5aeaf522dcfc4f938a,
    },
]

class TestPatriciaTrieScenarios(unittest2.TestCase):
    __metaclass__ = ScenarioMeta

    class test_init_mapping(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pt = PatriciaTrie(kwargs)
            self.assertEqual(pt.hash, hash_)

    class test_init_iterable(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pt = PatriciaTrie(six.iteritems(kwargs))
            self.assertEqual(pt.hash, hash_)

    class test_len(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pt = PatriciaTrie(kwargs)
            self.assertEqual(len(pt), len(kwargs))

    class test_getitem(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pt = PatriciaTrie(kwargs)
            for key,value in six.iteritems(kwargs):
                self.assertEqual(pt[key], kwargs[key])
            with self.assertRaises(KeyError):
                pt['123']

    class test_iter(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp((k for k,v in items), iter(pt)))
            pt2 = PatriciaTrie(reversed(items))
            self.assertFalse(icmp((k for k,v in items), iter(pt2)))

    class test_reversed(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp((k for k,v in reversed(items)), reversed(pt)))
            pt2 = PatriciaTrie(reversed(items))
            self.assertFalse(icmp((k for k,v in reversed(items)), reversed(pt2)))

    class test_clear(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pt = PatriciaTrie(kwargs)
            self.assertEqual(pt.hash, hash_)
            pt.clear()
            self.assertEqual(len(pt), 0)
            self.assertEqual(pt.hash, PatriciaTrie().hash)

    class test_copy(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pt = PatriciaTrie(kwargs)
            pt2 = pt.copy()
            for key in pt2:
                pt2[key] = pt2[key] + 1
            self.assertEqual(pt.hash, hash_)
            if kwargs:
                self.assertNotEqual(pt.hash, pt2.hash)
            pt2.clear()
            self.assertEqual(pt.hash, hash_)
            if kwargs:
                self.assertNotEqual(pt.hash, pt2.hash)

    class test_deepcopy(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pt = PatriciaTrie(kwargs)
            pt2 = pt.deepcopy()
            for key in pt2:
                pt2[key] = pt2[key] + 1
            self.assertEqual(pt.hash, hash_)
            if kwargs:
                self.assertNotEqual(pt.hash, pt2.hash)
            pt2.clear()
            self.assertEqual(pt.hash, hash_)
            if kwargs:
                self.assertNotEqual(pt.hash, pt2.hash)

    class test_get(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pt = PatriciaTrie(kwargs)
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                if key in kwargs:
                    self.assertEqual(pt.get(key, 0xff), value)
                else:
                    self.assertIs(pt.get(key), None)
                    self.assertEqual(pt.get(key, 0xff), 0xff)

    class test_items(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp(items, iter(pt.items())))
    class test_iteritems(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp(items, pt.iteritems()))
            self.assertFalse(icmp(items, six.iteritems(pt)))

    class test_reversed_items(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp(reversed(items), iter(pt.reversed_items())))
    class test_reversed_iteritems(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp(reversed(items), pt.reversed_iteritems()))

    class test_keys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp((k for k,v in items), iter(pt.keys())))
    class test_iterkeys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp((k for k,v in items), pt.iterkeys()))
            self.assertFalse(icmp((k for k,v in items), six.iterkeys(pt)))

    class test_reversed_keys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp(reversed([k for k,v in items]), iter(pt.reversed_keys())))
    class test_reversed_iterkeys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp(reversed([k for k,v in items]), pt.reversed_iterkeys()))

    class test_values(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp((v for k,v in items), iter(pt.values())))
    class test_itervalues(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp((v for k,v in items), pt.itervalues()))
            self.assertFalse(icmp((v for k,v in items), six.itervalues(pt)))

    class test_reversed_values(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp(reversed([v for k,v in items]), iter(pt.reversed_values())))
    class test_reversed_itervalues(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pt = PatriciaTrie(items)
            self.assertFalse(icmp(reversed([v for k,v in items]), pt.reversed_itervalues()))

class TestPatriciaTrie(unittest2.TestCase):
    def test_setitem(self):
        for flags in xrange(16):
            pt = PatriciaTrie((k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                            if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pt2 = pt.copy()
                self.assertEqual(pt2.hash, SCENARIOS[flags]['hash_'])
                pt2[key] = value
                self.assertEqual(pt2.hash, SCENARIOS[flags|value]['hash_'])

    def test_delitem(self):
        for flags in xrange(16):
            pt = PatriciaTrie((k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                            if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pt2 = pt.copy()
                self.assertEqual(pt2.hash, SCENARIOS[flags]['hash_'])
                if key in pt2:
                    del pt2[key]
                else:
                    with self.assertRaises(KeyError):
                        del pt2[key]
                self.assertEqual(pt2.hash, SCENARIOS[flags & ~value]['hash_'])

    def test_contains(self):
        for flags in xrange(16):
            pt = PatriciaTrie((k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                            if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                if flags&value:
                    self.assertIn(key, pt)
                else:
                    self.assertNotIn(key, pt)

    def test_has_key(self):
        for flags in xrange(16):
            pt = PatriciaTrie((k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                            if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                self.assertTrue(pt.has_key(key) == bool(flags&value))

    def test_pop(self):
        for flags in xrange(16):
            pt = PatriciaTrie((k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                            if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                if flags&value:
                    self.assertEqual(pt.pop(key), value)
                    flags = flags & ~value
                    self.assertEqual(pt.hash, SCENARIOS[flags]['hash_'])
                with self.assertRaises(KeyError):
                    pt.pop(key)
                self.assertEqual(pt.pop(key, value), value)

    def test_popitem(self):
        for flags in xrange(16):
            pt = PatriciaTrie((k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                            if k != 'hash_')
            while flags:
                key,value = pt.popitem()
                self.assertNotIn(key, pt)
                self.assertIn(key, SCENARIOS[flags])
                self.assertEqual(value, SCENARIOS[flags][key])
                flags = flags & ~value
                self.assertEqual(pt.hash, SCENARIOS[flags]['hash_'])
            with self.assertRaises(KeyError):
                pt.popitem()

    def test_setdefault(self):
        for flags in xrange(16):
            pt = PatriciaTrie((k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                            if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pt2 = pt.copy()
                if flags & value:
                    pt2.setdefault(key, value+1)
                    self.assertIn(key, pt2)
                    self.assertEqual(pt2[key], value)
                    self.assertEqual(pt2.hash, SCENARIOS[flags]['hash_'])
                else:
                    pt2.setdefault(key, value)
                    self.assertIn(key, pt2)
                    self.assertEqual(pt2[key], value)
                    self.assertEqual(pt2.hash, SCENARIOS[flags|value]['hash_'])

    def test_update(self):
        for flags in xrange(16):
            pt = PatriciaTrie((k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                            if k != 'hash_')
            for idx,scenario in enumerate(SCENARIOS):
                items = [(k,v) for k,v in six.iteritems(scenario)
                                       if k != 'hash_']
                pt2 = pt.copy()
                self.assertEqual(pt2.hash, SCENARIOS[flags]['hash_'])
                pt2.update(items)
                self.assertEqual(pt2.hash, SCENARIOS[flags|idx]['hash_'])

                pt3 = pt.copy()
                self.assertEqual(pt3.hash, SCENARIOS[flags]['hash_'])
                pt3.update(iter(items))
                self.assertEqual(pt3.hash, SCENARIOS[flags|idx]['hash_'])

                pt4 = pt.copy()
                self.assertEqual(pt4.hash, SCENARIOS[flags]['hash_'])
                pt4.update(**dict(items))
                self.assertEqual(pt4.hash, SCENARIOS[flags|idx]['hash_'])

    def test_delete(self):
        for flags in xrange(16):
            pt = PatriciaTrie((k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                            if k != 'hash_')
            for idx,scenario in enumerate(SCENARIOS):
                items = [(k,v) for k,v in six.iteritems(scenario)
                                       if k != 'hash_']
                pt2 = pt.copy()
                self.assertEqual(pt2.hash, SCENARIOS[flags]['hash_'])
                pt3 = pt.copy()
                self.assertEqual(pt3.hash, SCENARIOS[flags]['hash_'])
                for (k,v) in items:
                    if k in SCENARIOS[flags]:
                        pt2.delete([k])
                        pt3.delete(iter([k]))
                    else:
                        with self.assertRaises(KeyError):
                            pt2.delete([k])
                        with self.assertRaises(KeyError):
                            pt3.delete(iter([k]))
                self.assertEqual(pt2.hash, SCENARIOS[flags & ~idx]['hash_'])
                self.assertEqual(pt3.hash, SCENARIOS[flags & ~idx]['hash_'])

    def test_eq(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                   if k != 'hash_']
            pt = PatriciaTrie(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other])
                                        if k != 'hash_']
                pt2 = PatriciaTrie(items2)
                self.assertEqual(pt == pt2, cmp(sorted(items), sorted(items2)) == 0)

    def test_ne(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                   if k != 'hash_']
            pt = PatriciaTrie(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other])
                                        if k != 'hash_']
                pt2 = PatriciaTrie(items2)
                self.assertEqual(pt != pt2, cmp(sorted(items), sorted(items2)) != 0)

    def test_lt(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                   if k != 'hash_']
            pt = PatriciaTrie(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other])
                                        if k != 'hash_']
                pt2 = PatriciaTrie(items2)
                self.assertEqual(pt < pt2, cmp(sorted(items), sorted(items2)) < 0)

    def test_gt(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                   if k != 'hash_']
            pt = PatriciaTrie(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other])
                                        if k != 'hash_']
                pt2 = PatriciaTrie(items2)
                self.assertEqual(pt > pt2, cmp(sorted(items), sorted(items2)) > 0)

    def test_le(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                   if k != 'hash_']
            pt = PatriciaTrie(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other])
                                        if k != 'hash_']
                pt2 = PatriciaTrie(items2)
                self.assertEqual(pt <= pt2, cmp(sorted(items), sorted(items2)) <= 0)

    def test_ge(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags])
                                   if k != 'hash_']
            pt = PatriciaTrie(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other])
                                        if k != 'hash_']
                pt2 = PatriciaTrie(items2)
                self.assertEqual(pt >= pt2, cmp(sorted(items), sorted(items2)) >= 0)

#
# End of File
#
