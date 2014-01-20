# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

# Python 2 and 3 compatibility utilities
import six

import gmpy2

# Python standard library, unit-testing
import unittest2
# Scenario unit-testing
from scenariotest import ScenarioMeta, ScenarioTest

from bitcoin.authtree import *
from bitcoin.tools import Bits, StringIO, icmp

# ===----------------------------------------------------------------------===

class TestAuthTreeLink(unittest2.TestCase):
    def test_init(self):
        pn = MemoryPatriciaAuthTree()
        pl = AuthTreeLink(Bits(b'0b0'), pn)
        self.assertEqual(pl.prefix, Bits(bytes=b'\x00', length=1))
        self.assertEqual(pl.node, pn)
        self.assertFalse(pl.pruned)
        pl2 = AuthTreeLink(Bits(bytes=b'\x80', length=1), MemoryPatriciaAuthTree())
        self.assertEqual(pl2.prefix.uint, 0x01)
        self.assertEqual(pl2.node, pn)
        self.assertFalse(pl2.pruned)
        pl3 = AuthTreeLink(Bits(bytes=b'\x80'), MemoryPatriciaAuthTree())
        self.assertEqual(pl3.prefix.uint, 0x80)
        self.assertEqual(pl3.node, pn)
        self.assertFalse(pl3.pruned)
        pl4 = AuthTreeLink(b'\x80', MemoryPatriciaAuthTree())
        self.assertEqual(pl4.prefix.uint, 0x80)
        self.assertEqual(pl4.node, pn)
        self.assertFalse(pl4.pruned)
        pl5 = AuthTreeLink(b'\x80', MemoryPatriciaAuthTree())
        self.assertEqual(pl5.prefix.uint, 0x80)
        self.assertEqual(pl5.node, pn)
        self.assertFalse(pl5.pruned)
        pl6 = AuthTreeLink(b'\x80', hash=0, size=1)
        self.assertEqual(pl6.prefix.uint, 0x80)
        self.assertEqual(pl6.hash, 0)
        self.assertIs(pl6.node, None)
        self.assertTrue(pl6.pruned)
        pl7 = AuthTreeLink(b'\x80', 0, size=1)
        self.assertEqual(pl7.prefix.uint, 0x80)
        self.assertEqual(pl7.hash, 0)
        self.assertIs(pl7.node, None)
        self.assertTrue(pl7.pruned)

    def test_eq(self):
        pn = MemoryPatriciaAuthTree()
        self.assertEqual(
            AuthTreeLink(b'', MemoryPatriciaAuthTree()),
            AuthTreeLink(b'', MemoryPatriciaAuthTree()))
        self.assertNotEqual(
            AuthTreeLink(b'abc', MemoryPatriciaAuthTree()),
            AuthTreeLink(b'', MemoryPatriciaAuthTree()))
        self.assertEqual(
            AuthTreeLink(b'abc', MemoryPatriciaAuthTree()),
            AuthTreeLink(b'abc', MemoryPatriciaAuthTree()))
        self.assertNotEqual(
            AuthTreeLink(b'abc', MemoryPatriciaAuthTree()),
            AuthTreeLink(b'abc', MemoryPatriciaAuthTree(value=b'')))
        self.assertEqual(
            AuthTreeLink(b'abc', MemoryPatriciaAuthTree(value=b'')),
            AuthTreeLink(b'abc', MemoryPatriciaAuthTree(value=b'')))

# ===----------------------------------------------------------------------===

class TestAuthTreeNode(object):
    def test_init(self):
        pn = self.AuthTreeNode()
        self.assertIs(pn.value, None)
        self.assertEqual(icmp(pn.children, iter([])), 0)
        self.assertEqual(pn.hash, self.hashes[0])
        pn2 = self.AuthTreeNode(value=b'123')
        self.assertEqual(pn2.value, b'123')
        self.assertEqual(icmp(pn2.children, iter([])), 0)
        self.assertEqual(pn2.hash, self.hashes[1])
        pl = AuthTreeLink(b'abc', pn2)
        pn3 = self.AuthTreeNode(children=[pl])
        self.assertIs(pn3.value, None)
        self.assertEqual(icmp(pn3.children, iter([pl])), 0)
        self.assertEqual(pn3.hash, self.hashes[2])
        pn4 = self.AuthTreeNode(children={b'abc': pn2})
        self.assertIs(pn4.value, None)
        self.assertEqual(icmp(pn4.children, iter([pl])), 0)
        self.assertEqual(pn4.hash, self.hashes[2])
        pn5 = self.AuthTreeNode(b'456', {b'abc': pn2})
        self.assertEqual(pn5.value, b'456')
        self.assertEqual(icmp(pn4.children, iter([pl])), 0)
        self.assertEqual(pn5.hash, self.hashes[3])

    def test_invalid_init_parameters(self):
        # An older version of AuthTree uses hashes for the `value` field. The
        # new code takes binary strings, and rejects integer values to make
        # finding bugs from the conversion process easier:
        with self.assertRaises(TypeError):
            pn = self.AuthTreeNode(0)
        with self.assertRaises(TypeError):
            pn = self.AuthTreeNode(
                value = 0x56944c5d3f98413ef45cf54545538103cc9f298e0575820ad3591376e2e0f65d)

class TestComposableAuthTree(object):
    AuthTreeNode = MemoryComposableAuthTree
    hashes = (
        0xc7cf090a63780b417eb8c55da3daf05791308a0fc393ee7bc685f224d296a296,
        0xa6a357cc11c024e266fed4b3cecddc75f17161bb309ad35db4c1577b4882be3e,
        0xeebf6d83f16d17938f9e2850feaae2040ead54dabc3648897093f67645af7f7f,
        0xe138846eab6d3debd1be0b6fe54aec976aa67a09812d2a64194e317c7374d8a6,
    )

class TestPatriciaAuthTree(object):
    AuthTreeNode = MemoryPatriciaAuthTree
    hashes = (
        0xc7cf090a63780b417eb8c55da3daf05791308a0fc393ee7bc685f224d296a296,
        0xa6a357cc11c024e266fed4b3cecddc75f17161bb309ad35db4c1577b4882be3e,
        0xeebf6d83f16d17938f9e2850feaae2040ead54dabc3648897093f67645af7f7f,
        0xe138846eab6d3debd1be0b6fe54aec976aa67a09812d2a64194e317c7374d8a6,
    )

LeafValue = BaseAuthTreeNode(b'123')
SCENARIOS = [
    dict(value = None, children = [],
         str_  = b'\x00\x00',
         composable = 0xc7cf090a63780b417eb8c55da3daf05791308a0fc393ee7bc685f224d296a296,
         patricia   = 0xc7cf090a63780b417eb8c55da3daf05791308a0fc393ee7bc685f224d296a296),
    dict(value = b'abc', children = [],
         str_  = b'\x10' b'\x00' b'\x03abc',
         composable = 0xeef6ab09ad94027c945d4b1a8639fbd8121dc011f9b760266dbc1cdaf264c6f0,
         patricia   = 0xeef6ab09ad94027c945d4b1a8639fbd8121dc011f9b760266dbc1cdaf264c6f0),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b0'), LeafValue)],
         str_  = b'\x11' b'\x00' b'\x03abc' b'\x10\x00\x03123',
         composable = 0x975633aae083de21088dbf8a7dbe3aa8168328cc5a0a73d23f7cb322c7b71285,
         patricia   = 0x975633aae083de21088dbf8a7dbe3aa8168328cc5a0a73d23f7cb322c7b71285),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b00'), LeafValue)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x02' b'\x10\x00\x03123',
         composable = 0x1c2ac0ed8411a8f417a5bb71df8056897881a711c7165852edbe030952044517,
         patricia   = 0xc4838b989b4fcc143f80ca84939fdfabe52341331b0ac453525e2088d1a836e7),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b010'), LeafValue)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x05' b'\x10\x00\x03123',
         composable = 0x71676b3e767277e60dde5e581b4a0122084ded6e9fef63a1094308049f0d65ee,
         patricia   = 0x65b30d1f8f8a0177bf12999bf1c3a707ca12d0f5422bd02efb66660f142fc404),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b0110'), LeafValue)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x0b' b'\x10\x00\x03123',
         composable = 0xa5568b87400878cb39c7dbffd3480423f30fedcda96f15a04450fe4782c9618a,
         patricia   = 0xe3a2dc7f3fe90134cf511e2e4414c0e746f8ed019bd78c2327b8425c9f3b646f),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b00110'), LeafValue)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x16' b'\x10\x00\x03123',
         composable = 0x26d16966b86ee46d2864fdad339c7786010045149792a873325a3596aaa1dbfd,
         patricia   = 0x032bcc41c344af64ffe5fc60e77d2bdfa576c3652e7a91223f4f35582e6ff164),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b000110'), LeafValue)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x2c' b'\x10\x00\x03123',
         composable = 0xf1ba2c131c41f76d6a5436352fbd061e53ac599b580fa07a5e93ff1ca7109aa2,
         patricia   = 0x51dc23cf1b296dcfc9146953aaea08287ba9d0ef6ce1e4e9358f100ff152e629),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b0000110'), LeafValue)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x58' b'\x10\x00\x03123',
         composable = 0x431a48b6a22a833c7ad493d252dbedbd32ff67039bb32eec4c20ec0c96809a0b,
         patricia   = 0x64732dc431b19dd69e3a28e1abf7068674b97358e706f8d5319e8b08972ca9e4),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b01000110'), LeafValue)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\xb1' b'\x10\x00\x03123',
         composable = 0x303895b634a9f8d403b3b13e4354d9e6cd611c6b0032aec99ffee59667c09709,
         patricia   = 0x6e866502d8e4107487eefbd2c9a136dc9d90a19c62cffc1966ff758e20e1c3fc),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b011000110'), LeafValue)],
         str_  = b'\x13' b'\x00' b'\x03abc' b'\x00\x63' b'\x10\x00\x03123',
         composable = 0xbe821e7b0a795c4aed3b50ead015dd39a8107fd3cc009e90acf50c97f1a65ea8,
         patricia   = 0x54f927927fe7bc393a094e721afe61626d1cd89205a86f7ac12b69153e6d9eb9),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b0111000110'), LeafValue)],
         str_  = b'\x13' b'\x00' b'\x03abc' b'\x01\xc7\x00' b'\x10\x00\x03123',
         composable = 0x64950f66a9f4d03fb87d3450a40c14de767ebd2d3bd7d7c4088ab3527e26594a,
         patricia   = 0xd3f607542a36b461bca50cb9d8ce98d1e8dcb5bb2685aa45f142050038a1f387),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b01111000110'), LeafValue)],
         str_  = b'\x13' b'\x00' b'\x03abc' b'\x02\x8f\x01' b'\x10\x00\x03123',
         composable = 0xc226bc302f329f271d68d86ce06a51f18e841cf2e516e629a7435da85d1307b1,
         patricia   = 0xeec7b766a358e926ae4e9d2399c5751d9e2c1f6be5a4777cfdd202a899e91f78),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b00000011110001101111'
             '1110000000111111000001111000110111111100000001111110000011110001'
             '1011111110000000111111000001111000110111111100000001111110000011'
             '1100011011111110000000111111000001111000110111111100000001111110'
             '0000111100011011111110000000111111000001111000110'), LeafValue)],
         str_  = ''.join([b'\x13', b'\x00', b'\x03abc', b'\xfc', ('e0b13fe007'
                          '8ffd013f78ec0ff8c1637fc00f1efb037ef0d81ff083c7fe80'
                          '1f3c06').decode('hex'), b'\x10\x00\x03123']),
         composable = 0x01253f713e8cc758fd91af0afd3e70db02403c434acd499937b72f5147bb8539,
         patricia   = 0x16fb5f0c6a7fd9433b54c5d785530e48290a411689c2bde03462c3c4acfe3f00),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b01000001111000110111'
             '1111000000011111100000111100011011111110000000111111000001111000'
             '1101111111000000011111100000111100011011111110000000111111000001'
             '1110001101111111000000011111100000111100011011111110000000111111'
             '00000111100011011111110000000111111000001111000110'), LeafValue)],
         str_  = ''.join([b'\x13', b'\x00', b'\x03abc', b'\xfd\xfd\x00', ('c1'
                          '637fc00f1efb037ef0d81ff083c7fe801f3cf607fce0b13fe0'
                          '078ffd013f780c').decode('hex'), b'\x10\x00\x03123']),
         composable = 0x4fd900c25468458091d01be352fbabf08038648e549786a4cfff4faa9bc1e277,
         patricia   = 0x273448b6c7830e881a4c599ba9ede939bca7c613800a242b4986a9d6939bf3ec),
]

class TestAuthTreeSerialization(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, value, children, str_, composable, patricia):
            pn = MemoryComposableAuthTree(value, children)
            self.assertEqual(pn.serialize(), str_)
            self.assertEqual(pn.hash, composable)
            pn2 = MemoryPatriciaAuthTree(value, children)
            self.assertEqual(pn2.serialize(), str_)
            self.assertEqual(pn2.hash, patricia)
    class test_deserialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, value, children, str_, composable, patricia):
            pn = MemoryComposableAuthTree.deserialize(StringIO(str_))
            self.assertEqual(pn.value, value)
            self.assertEqual(list(pn.children), children)
            self.assertEqual(pn.hash, composable)
            pn2 = MemoryPatriciaAuthTree.deserialize(StringIO(str_))
            self.assertEqual(pn2.value, value)
            self.assertEqual(list(pn2.children), children)
            self.assertEqual(pn2.hash, patricia)

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
        'composable': 0xc7cf090a63780b417eb8c55da3daf05791308a0fc393ee7bc685f224d296a296,
        'patricia':   0xc7cf090a63780b417eb8c55da3daf05791308a0fc393ee7bc685f224d296a296,
    },
    {
        b'':          six.int2byte(1),
        'composable': 0x95d774894ed49b597ab5cfb2b836a553ab8f940087f98a4e1d542fffcd8de372,
        'patricia':   0x95d774894ed49b597ab5cfb2b836a553ab8f940087f98a4e1d542fffcd8de372,
    },
    {
        b'abc':       six.int2byte(2),
        'composable': 0x97fc634f49cba0e661a944c2557587140d2d00e88af1668ede4361a1d99b780b,
        'patricia':   0x666e0f256e50ddc013d734c3908d264b47e04ac293cbf37457d6aae52a83972c,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        'composable': 0x6710c6f285c895c85c57b027430345292fa058449bd65b33abfaeb82b35103cd,
        'patricia':   0xdac74fe879dd9dbea12d75841c2c017eab0cd4fe586744a0cf8b8593a08ce4a8,
    },
    {
        b'abcdef':    six.int2byte(4),
        'composable': 0xba928ccd92956bfd1aecc1a5df275d149e560c3496f3a156689ab12809c78450,
        'patricia':   0xd8bececa2be9dad56901f4142cf93dc075261c8cb11b0ab474b1ca25d8a64864,
    },
    {
        b'':          six.int2byte(1),
        b'abcdef':    six.int2byte(4),
        'composable': 0x674f77b8aec846105c9ccae62ad66735592831e39c26b3442ed51b3335ac5d04,
        'patricia':   0x9fa9b07ed1a1b1300cd81e901ab07710b3d59d5d964abfe232d50ee6e3578a75,
    },

    {
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        'composable': 0x8feaee237765272b565d4fa28de5afeccd9df7b5ca997e886034930de8f619b0,
        'patricia':   0xdae04c3c1c68d51c305af003feae7d157594fc014614d867bf5e96014f213ff4,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        'composable': 0xc2f4b0754b45d93a8a142432f1a498f517f39cfdd8ed505ad91387d27df5a679,
        'patricia':   0xb0c2d52ab45f307319a2791b66cf8b857621f698b5aaef2547777e36988d104f,
    },
    {
        b'abcxyz':    six.int2byte(8),
        'composable': 0xe131d907f228a3d82cd23f1be85bfaaf33075b853162915b28ac281a5d53bcfb,
        'patricia':   0x3bcc66c9adf2a3725f3c45eec4ce5b62c4665a1cbc3edfa6cb2867cf42353fcc,
    },
    {
        b'':          six.int2byte(1),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x35a8e10156c756ea051545636ce976c95565f58402f540bc5ade6aa0a931b09a,
        'patricia':   0x36a08abadf735db2462c2749113782db3de3d177e2d757ec124a12b9bd8f78aa,
    },
    {
        b'abc':       six.int2byte(2),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x2490584a8f8d6acf61351e7d71d685f1296826de1e5c7876bc68ea5bd49cf351,
        'patricia':   0x6bb0c99aabe40983718f8552894fd3714b1d6a5fc980affa51ba5ba5f901a5c7,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x310c2ffc92caf8e0a5ab753c1e1279302fcc15d021b176176c8670b95a425cb0,
        'patricia':   0x40888b247c02da3ad782861531164c4ae950f82031bd90fbff24743caab3d096,
    },
    {
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x6ebf0563121325772552ca548e9dc4012b5285ae08fb0b7cde1d32f51c12bec1,
        'patricia':   0x0baa6bdc542587f8da71b3c891fb66a02dd2665a4b214dad7fbcbad3e6762830,
    },
    {
        b'':          six.int2byte(1),
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0xe0d3cc65a15ef5c5ba7f74e9e91d80b9289b33684de72e558287a3f2fd28b1ef,
        'patricia':   0xa013f6fd8cf919d5692bc2b9931669bcd32496ee6243bee479201535b79e1cf4,
    },
    {
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x0f35591747a6f947e3bda4ec0d2d440bbdf9b6563982c7f291f8df68c2286da9,
        'patricia':   0xeb0f222af5d9fa880e77e4c141e14cda2236f9f7cc860dde9b0e928340d8d0eb,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x0cccd2b2e314cbad6570e449960a86fd183f91a402874f77ad5e8dd6e3027b42,
        'patricia':   0xcbd0f059e42abe2c1a2e930ee939ebb84299b2e81f279692fba617d8c655847c,
    },
]

class TestPatriciaDictScenarios(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_init_mapping(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, composable, patricia, **kwargs):
            pn = MemoryComposableAuthTree()
            pn.update(kwargs)
            self.assertEqual(pn.hash, composable, kwargs)
            pn2 = MemoryPatriciaAuthTree()
            pn2.update(kwargs)
            self.assertEqual(pn2.hash, patricia, kwargs)

    class test_init_iterable(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, composable, patricia, **kwargs):
            pn = MemoryComposableAuthTree()
            pn.update(six.iteritems(kwargs))
            self.assertEqual(pn.hash, composable, kwargs)
            pn2 = MemoryPatriciaAuthTree()
            pn2.update(six.iteritems(kwargs))
            self.assertEqual(pn2.hash, patricia, kwargs)

    class test_bool(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, composable, patricia, **kwargs):
            pn = MemoryComposableAuthTree()
            pn.update(kwargs)
            self.assertEqual(bool(pn), bool(kwargs), kwargs)
            pn2 = MemoryPatriciaAuthTree()
            pn2.update(kwargs)
            self.assertEqual(bool(pn2), bool(kwargs), kwargs)

class TestPatriciaDictScenarios2(object):
    def test_lt(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaAuthTree()
                pn2.update(items2)
                self.assertEqual(pn < pn2, cmp(sorted(items), sorted(items2)) < 0)

    def test_le(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaAuthTree()
                pn2.update(items2)
                self.assertEqual(pn <= pn2, cmp(sorted(items), sorted(items2)) <= 0)

    def test_eq(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaAuthTree()
                pn2.update(items2)
                self.assertEqual(pn == pn2, cmp(sorted(items), sorted(items2)) == 0)

    def test_ne(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaAuthTree()
                pn2.update(items2)
                self.assertEqual(pn != pn2, cmp(sorted(items), sorted(items2)) != 0)

    def test_ge(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaAuthTree()
                pn2.update(items2)
                self.assertEqual(pn >= pn2, cmp(sorted(items), sorted(items2)) >= 0)

    def test_gt(self):
        for flags in xrange(16):
            items = [(k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_']
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            for other in xrange(16):
                items2 = [(k,v) for k,v in six.iteritems(SCENARIOS[other]) if k != 'hash_']
                pn2 = MemoryPatriciaAuthTree()
                pn2.update(items2)
                self.assertEqual(pn > pn2, cmp(sorted(items), sorted(items2)) > 0)

class TestPatriciaDictScenarios3(object):
    __metaclass__ = ScenarioMeta
    class test_len(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaAuthTree()
            pn.update(kwargs)
            self.assertEqual(len(pn), len(kwargs))

    class test_size(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaAuthTree()
            pn.update(kwargs)
            self.assertEqual(pn.size, len(kwargs))

    class test_length(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaAuthTree()
            pn.update(kwargs)
            self.assertEqual(pn.length, len(kwargs))

    class test_iter(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in items), iter(pn)))
            pn2 = MemoryPatriciaAuthTree()
            pn2.update(reversed(items))
            self.assertFalse(icmp((k for k,v in items), iter(pn2)))

    class test_reversed(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in reversed(items)), reversed(pn)))
            pn2 = MemoryPatriciaAuthTree()
            pn2.update(reversed(items))
            self.assertFalse(icmp((k for k,v in reversed(items)), reversed(pn2)))

    class test_items(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp(items, iter(pn.items())))
    class test_iteritems(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp(items, pn.iteritems()))
            self.assertFalse(icmp(items, six.iteritems(pn)))

    class test_reversed_items(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp(reversed(items), iter(pn.reversed_items())))
    class test_reversed_iteritems(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp(reversed(items), pn.reversed_iteritems()))

    class test_keys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in items), iter(pn.keys())))
    class test_iterkeys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp((k for k,v in items), pn.iterkeys()))
            self.assertFalse(icmp((k for k,v in items), six.iterkeys(pn)))

    class test_reversed_keys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp(reversed([k for k,v in items]), iter(pn.reversed_keys())))
    class test_reversed_iterkeys(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp(reversed([k for k,v in items]), pn.reversed_iterkeys()))

    class test_values(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp((v for k,v in items), iter(pn.values())))
    class test_itervalues(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp((v for k,v in items), pn.itervalues()))
            self.assertFalse(icmp((v for k,v in items), six.itervalues(pn)))

    class test_reversed_values(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp(reversed([v for k,v in items]), iter(pn.reversed_values())))
    class test_reversed_itervalues(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            items = sorted((k,v) for k,v in six.iteritems(kwargs))
            pn = MemoryPatriciaAuthTree()
            pn.update(items)
            self.assertFalse(icmp(reversed([v for k,v in items]), pn.reversed_itervalues()))

class TestPatriciaDictScenarios4(object):
    def test_contains(self):
        for flags in xrange(16):
            pn = MemoryPatriciaAuthTree()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                if flags & ord(value):
                    self.assertIn(key, pn)
                else:
                    self.assertNotIn(key, pn)

    def test_has_key(self):
        for flags in xrange(16):
            pn = MemoryPatriciaAuthTree()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                self.assertTrue(pn.has_key(key) == bool(flags & ord(value)))

class TestPatriciaDictScenarios5(object):
    __metaclass__ = ScenarioMeta
    class test_getitem(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaAuthTree()
            pn.update(kwargs)
            for key,value in six.iteritems(kwargs):
                self.assertEqual(pn[key], kwargs[key])
            with self.assertRaises(KeyError):
                pn['123']

    class test_get(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pn = MemoryPatriciaAuthTree()
            pn.update(kwargs)
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                if key in kwargs:
                    self.assertEqual(pn.get(key), value)
                    self.assertEqual(pn.get(key, SENTINAL), value)
                else:
                    self.assertIs(pn.get(key), None)
                    self.assertIs(pn.get(key, SENTINAL), SENTINAL)

class TestPatriciaDictScenarios6(object):
    def test_update(self):
        for flags in xrange(16):
            pn = MemoryPatriciaAuthTree()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for idx,scenario in enumerate(SCENARIOS):
                items = [(k,v) for k,v in six.iteritems(scenario) if k != 'hash_']
                pn2 = MemoryPatriciaAuthTree()
                pn2.update(pn)
                self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'])
                self.assertEqual(pn2.size, gmpy2.popcount(flags))
                self.assertEqual(pn2.length, gmpy2.popcount(flags))
                pn2.update(items)
                self.assertEqual(pn2.hash, SCENARIOS[flags|idx]['hash_'])
                self.assertEqual(pn2.size, gmpy2.popcount(flags|idx))
                self.assertEqual(pn2.length, gmpy2.popcount(flags|idx))

                pn3 = MemoryPatriciaAuthTree()
                pn3.update(pn)
                self.assertEqual(pn3.hash, SCENARIOS[flags]['hash_'])
                self.assertEqual(pn3.size, gmpy2.popcount(flags))
                self.assertEqual(pn3.length, gmpy2.popcount(flags))
                pn3.update(iter(items))
                self.assertEqual(pn3.hash, SCENARIOS[flags|idx]['hash_'])
                self.assertEqual(pn3.size, gmpy2.popcount(flags|idx))
                self.assertEqual(pn3.length, gmpy2.popcount(flags|idx))

                pn4 = MemoryPatriciaAuthTree()
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
            pn = MemoryPatriciaAuthTree()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pn2 = MemoryPatriciaAuthTree()
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
            pn = MemoryPatriciaAuthTree()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pn2 = MemoryPatriciaAuthTree()
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

    def test_trim(self):
        for flags in xrange(16):
            pn = MemoryPatriciaAuthTree()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            pn2 = MemoryPatriciaAuthTree()
            pn2.update(pn)
            res = pn2.trim(['abc'])
            self.assertEqual(res, gmpy2.popcount(flags>>1))
            del pn2.hash
            self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'], flags)
            self.assertEqual(pn2.size, gmpy2.popcount(flags))
            self.assertEqual(pn2.length, gmpy2.popcount(flags&1))
            if pn2.children:
                self.assertEqual(pn2.children[0].size, gmpy2.popcount(flags) - (flags&1))
                self.assertEqual(pn2.children[0].length, 0)
                self.assertTrue(pn2.children[0].pruned)
            pn3 = MemoryPatriciaAuthTree()
            pn3.update(pn)
            res = pn3.trim([Bits(bytes='abc\x00', length=25)])
            self.assertEqual(res, gmpy2.popcount(flags>>2))
            del pn3.hash
            self.assertEqual(pn3.hash, SCENARIOS[flags]['hash_'])
            self.assertEqual(pn3.size, gmpy2.popcount(flags))
            self.assertEqual(pn3.length, gmpy2.popcount(flags&3))

    def test_prune(self):
        for flags in xrange(16):
            pn = MemoryPatriciaAuthTree()
            old_items = set((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            pn.update(old_items)
            for idx,scenario in enumerate(SCENARIOS):
                if idx|flags != flags or idx&flags != idx:
                    continue
                new_items = set((k,v) for k,v in six.iteritems(scenario) if k != 'hash_')
                pn2 = MemoryPatriciaAuthTree()
                pn2.update(pn)
                pn3 = MemoryPatriciaAuthTree()
                pn3.update(pn)
                pn4 = MemoryPatriciaAuthTree()
                pn4.update(pn)
                for d in (pn, pn2, pn3, pn4):
                    self.assertEqual(d.hash, SCENARIOS[flags]['hash_'])
                    self.assertEqual(d.size, gmpy2.popcount(flags))
                    self.assertEqual(d.length, gmpy2.popcount(flags))
                keys = set()
                for (k,v) in new_items:
                    pn2.prune([k])
                    pn3.prune(iter([k]))
                    keys.add(k)
                pn4.prune(keys)
                self.assertEqual(pn.hash, SCENARIOS[flags]['hash_'])
                self.assertEqual(pn.size, gmpy2.popcount(flags))
                self.assertEqual(pn.length, gmpy2.popcount(flags))
                for d in (pn2, pn3, pn4):
                    del d.hash
                    self.assertEqual(d.hash, SCENARIOS[flags]['hash_'])
                    self.assertEqual(d.size, gmpy2.popcount(flags))
                    self.assertEqual(d.length, gmpy2.popcount(flags) - len(new_items))
                    self.assertEqual(set(d.items()), old_items - new_items)
                    for key,value in old_items:
                        if key in keys:
                            with self.assertRaises(KeyError):
                                d.prune([key])
                        else:
                            self.assertEqual(d[key], value)

    def test_delete(self):
        for flags in xrange(16):
            pn = MemoryPatriciaAuthTree()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for idx,scenario in enumerate(SCENARIOS):
                items = [(k,v) for k,v in six.iteritems(scenario) if k != 'hash_']
                pn2 = MemoryPatriciaAuthTree()
                pn2.update(pn)
                self.assertEqual(pn2.hash, SCENARIOS[flags]['hash_'])
                self.assertEqual(pn2.size, gmpy2.popcount(flags))
                self.assertEqual(pn2.length, gmpy2.popcount(flags))
                pn3 = MemoryPatriciaAuthTree()
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
            pn = MemoryPatriciaAuthTree()
            pn.update((k,v) for k,v in six.iteritems(SCENARIOS[flags]) if k != 'hash_')
            for key,value in six.iteritems(ADDRESS_TO_VALUE):
                pn2 = MemoryPatriciaAuthTree()
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

    class test_copy(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, hash_, **kwargs):
            pt = PatriciaTrie(kwargs)
            pt2 = pt.copy()
            for key in pt2:
                pt2[key] = six.int2byte(ord(pt2[key]) + 1)
            self.assertEqual(pt.hash, hash_)
            if kwargs:
                self.assertNotEqual(pt.hash, pt2.hash)
            pt2.clear()
            self.assertEqual(pt.hash, hash_)
            if kwargs:
                self.assertNotEqual(pt.hash, pt2.hash)
