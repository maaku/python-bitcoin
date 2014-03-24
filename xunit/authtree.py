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
        pl = pn.link_class(Bits(b'0b0'), pn)
        self.assertEqual(pl.prefix, Bits(bytes=b'\x00', length=1))
        self.assertEqual(pl.node, pn)
        self.assertFalse(pl.pruned)
        pl2 = pn.link_class(Bits(bytes=b'\x80', length=1), MemoryPatriciaAuthTree())
        self.assertEqual(pl2.prefix.uint, 0x01)
        self.assertEqual(pl2.node, pn)
        self.assertFalse(pl2.pruned)
        pl3 = pn.link_class(Bits(bytes=b'\x80'), MemoryPatriciaAuthTree())
        self.assertEqual(pl3.prefix.uint, 0x80)
        self.assertEqual(pl3.node, pn)
        self.assertFalse(pl3.pruned)
        pl4 = pn.link_class(b'\x80', MemoryPatriciaAuthTree())
        self.assertEqual(pl4.prefix.uint, 0x80)
        self.assertEqual(pl4.node, pn)
        self.assertFalse(pl4.pruned)
        pl5 = pn.link_class(b'\x80', MemoryPatriciaAuthTree())
        self.assertEqual(pl5.prefix.uint, 0x80)
        self.assertEqual(pl5.node, pn)
        self.assertFalse(pl5.pruned)
        pl6 = pn.link_class(b'\x80', hash=0, size=1)
        self.assertEqual(pl6.prefix.uint, 0x80)
        self.assertEqual(pl6.hash, 0)
        self.assertIs(pl6.node, None)
        self.assertTrue(pl6.pruned)
        pl7 = pn.link_class(b'\x80', 0, size=1)
        self.assertEqual(pl7.prefix.uint, 0x80)
        self.assertEqual(pl7.hash, 0)
        self.assertIs(pl7.node, None)
        self.assertTrue(pl7.pruned)

    def test_eq(self):
        pn = MemoryPatriciaAuthTree()
        self.assertEqual(
            pn.link_class(b'', MemoryPatriciaAuthTree()),
            pn.link_class(b'', MemoryPatriciaAuthTree()))
        self.assertNotEqual(
            pn.link_class(b'abc', MemoryPatriciaAuthTree()),
            pn.link_class(b'', MemoryPatriciaAuthTree()))
        self.assertEqual(
            pn.link_class(b'abc', MemoryPatriciaAuthTree()),
            pn.link_class(b'abc', MemoryPatriciaAuthTree()))
        self.assertNotEqual(
            pn.link_class(b'abc', MemoryPatriciaAuthTree()),
            pn.link_class(b'abc', MemoryPatriciaAuthTree(value=b'')))
        self.assertEqual(
            pn.link_class(b'abc', MemoryPatriciaAuthTree(value=b'')),
            pn.link_class(b'abc', MemoryPatriciaAuthTree(value=b'')))

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
        pl = self.AuthTreeNode.link_class(b'abc', pn2)
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

leaf_value = BaseAuthTreeNode(b'123')
SCENARIOS = [
    dict(value = None, children = [],
         str_  = b'\x00\x00',
         composable = 0x52e48cb2ad44028bb41e99d3d7727b866589b6b1314c6055bea5dad3520252cd,
         patricia   = 0x52e48cb2ad44028bb41e99d3d7727b866589b6b1314c6055bea5dad3520252cd),
    dict(value = b'abc', children = [],
         str_  = b'\x10' b'\x00' b'\x03abc',
         composable = 0x5fd655e94e5f3d638a651e172efe8a6a94667cc5e6b187f0d66be17affc3f5e0,
         patricia   = 0x5fd655e94e5f3d638a651e172efe8a6a94667cc5e6b187f0d66be17affc3f5e0),
    dict(value = b'abc', children = [(Bits('0b0'), leaf_value)],
         str_  = b'\x11' b'\x00' b'\x03abc' b'\x10\x00\x03123',
         composable = 0xf23372d0378733fe5086b0304ce912cc7ce5af8a011b8bc427f280f6e0a5a943,
         patricia   = 0xf23372d0378733fe5086b0304ce912cc7ce5af8a011b8bc427f280f6e0a5a943),
    dict(value = b'abc', children = [(Bits('0b00'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x02' b'\x10\x00\x03123',
         composable = 0xae58714f66551df9c417007d77ac907843c62f64a05ee2b7e0344626ef7b9db1,
         patricia   = 0x86dff1db1951234bfa86a4fde66ba911d88e7a844e97a02758a9c99e3cce1514),
    dict(value = b'abc', children = [(Bits('0b010'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x05' b'\x10\x00\x03123',
         composable = 0x8ac3e3326269dcd08a85c1b4be9ecb4bf7545e2ab309cb6aff651cee862d4251,
         patricia   = 0x8d9d0b874b05464271c07cf2e8764e7baf7c628f5be4aa4f82d1022f8ec395c2),
    dict(value = b'abc', children = [(Bits('0b0110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x0b' b'\x10\x00\x03123',
         composable = 0xcb4be3823588a7b0126144a244e91b55945348630424d694ac18c29dc8f7550e,
         patricia   = 0xa9b63c7d6ea52a23787a339cb34b92e0f8d1038def61ac14ec27d627cfed71a9),
    dict(value = b'abc', children = [(Bits('0b00110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x16' b'\x10\x00\x03123',
         composable = 0xe43c1cd1144f76dfbea82cb76e26dbcc0e04a7755b6cc44a4f2d65d395fa86bf,
         patricia   = 0xb67a24f81cfd4ca37506c3db0b866afea7e0963fb784c59719a54660764fd74b),
    dict(value = b'abc', children = [(Bits('0b000110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x2c' b'\x10\x00\x03123',
         composable = 0xe17828dc92628f16ba8d5105ecb24448dc1477e77a6c2052a3f3e1bf36688302,
         patricia   = 0x35617903d38e48653db888d5907523a4ee4e0c9511811933f10646583b9f0efe),
    dict(value = b'abc', children = [(Bits('0b0000110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x58' b'\x10\x00\x03123',
         composable = 0x00803a18b8174345145c15d8efe2101e6ece15b55ee08120c1c6db11e4858060,
         patricia   = 0x181a6888a0244d89cfc94ecbf1e3cfcb11e4d4144ac4001f5dd848cb57f43a6a),
    dict(value = b'abc', children = [(Bits('0b01000110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\xb1' b'\x10\x00\x03123',
         composable = 0xea754c58e68a0daa20f537079bf1570aa00f43978940a7e025ddb96ccefae5dd,
         patricia   = 0x8f52170491d87eb683708e4692b8f9daba48407b76b0c333db3dca8666375a71),
    dict(value = b'abc', children = [(Bits('0b011000110'), leaf_value)],
         str_  = b'\x13' b'\x00' b'\x03abc' b'\x00\x63' b'\x10\x00\x03123',
         composable = 0x3162fe463ca9c55d4895a7f2e978321052224c8c8ba2563dc9d7c9e269c202b4,
         patricia   = 0xdc8eb223bab048c78c9de85071cca69ea8d42cabf2ea80f3fac6d83960f1f39d),
    dict(value = b'abc', children = [(Bits('0b0111000110'), leaf_value)],
         str_  = b'\x13' b'\x00' b'\x03abc' b'\x01\xc7\x00' b'\x10\x00\x03123',
         composable = 0x33d27158e8e914cd043d7edc108feb4a06af47d72a7d73fff5f39d8d881a2165,
         patricia   = 0xf2838f63bcc6c9fe7494297b330d319ff724ec0ba2050ab3815e74f3cc55dc36),
    dict(value = b'abc', children = [(Bits('0b01111000110'), leaf_value)],
         str_  = b'\x13' b'\x00' b'\x03abc' b'\x02\x8f\x01' b'\x10\x00\x03123',
         composable = 0x0f93efbbdddbb674cf73c4aa8e836cac5ece6092e2869195c00cf7b93f667228,
         patricia   = 0xb847ed45db28e2a6d6a476928b458ec3eaa66c689e92dc73e07b0fff7c8221fb),
#    dict(value = b'abc', children = [AuthTreeLink(Bits('0b00000011110001101111'
#             '1110000000111111000001111000110111111100000001111110000011110001'
#             '1011111110000000111111000001111000110111111100000001111110000011'
#             '1100011011111110000000111111000001111000110111111100000001111110'
#             '0000111100011011111110000000111111000001111000110'), leaf_value)],
#         str_  = ''.join([b'\x13', b'\x00', b'\x03abc', b'\x7d', ('e0b13fe007'
#                          '8ffd013f78ec0ff8c1637fc00f1efb037ef0d81ff083c7fe80'
#                          '1f3c06').decode('hex'), b'\x10\x00\x03123']),
#         composable = 0x01253f713e8cc758fd91af0afd3e70db02403c434acd499937b72f5147bb8539,
#         patricia   = 0x16fb5f0c6a7fd9433b54c5d785530e48290a411689c2bde03462c3c4acfe3f00),
#    dict(value = b'abc', children = [AuthTreeLink(Bits('0b01000001111000110111'
#             '1111000000011111100000111100011011111110000000111111000001111000'
#             '1101111111000000011111100000111100011011111110000000111111000001'
#             '1110001101111111000000011111100000111100011011111110000000111111'
#             '00000111100011011111110000000111111000001111000110'), leaf_value)],
#        str_  = ''.join([b'\x13', b'\x00', b'\x03abc', b'\x7d', ('c1'
#                          '637fc00f1efb037ef0d81ff083c7fe801f3cf607fce0b13fe0'
#                          '078ffd013f780c').decode('hex'), b'\x10\x00\x03123']),
#         composable = 0x4fd900c25468458091d01be352fbabf08038648e549786a4cfff4faa9bc1e277,
#         patricia   = 0x273448b6c7830e881a4c599ba9ede939bca7c613800a242b4986a9d6939bf3ec),
]

class TestAuthTreeSerialization(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, value, children, str_, composable, patricia):
            pn = MemoryComposableAuthTree(value,
                [ComposableAuthTreeLink(*args) for args in children])
            self.assertEqual(pn.serialize(), str_)
            self.assertEqual(pn.hash, composable)
            pn2 = MemoryPatriciaAuthTree(value,
                [PatriciaAuthTreeLink(*args) for args in children])
            self.assertEqual(pn2.serialize(), str_)
            self.assertEqual(pn2.hash, patricia)
    class test_deserialize(ScenarioTest):
        scenarios = SCENARIOS
        def __test__(self, value, children, str_, composable, patricia):
            pn = MemoryComposableAuthTree.deserialize(StringIO(str_))
            self.assertEqual(pn.value, value)
            self.assertEqual(list((child.prefix, child.node) for child in pn.children), children)
            self.assertEqual(pn.hash, composable)
            pn2 = MemoryPatriciaAuthTree.deserialize(StringIO(str_))
            self.assertEqual(pn2.value, value)
            self.assertEqual(list((child.prefix, child.node) for child in pn2.children), children)
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
        'composable': 0x52e48cb2ad44028bb41e99d3d7727b866589b6b1314c6055bea5dad3520252cd,
        'patricia':   0x52e48cb2ad44028bb41e99d3d7727b866589b6b1314c6055bea5dad3520252cd,
    },
    {
        b'':          six.int2byte(1),
        'composable': 0x07d64a21a3870ec140e7e851531065b44d9b9d83e360bc42eac2e267cf98db93,
        'patricia':   0x07d64a21a3870ec140e7e851531065b44d9b9d83e360bc42eac2e267cf98db93,
    },
    {
        b'abc':       six.int2byte(2),
        'composable': 0x6420588b6b874078bb72ccd87de10c8ffe00a4de92b73b16ca7978410d0d94e7,
        'patricia':   0xba2e2a58b256ba4e40d6fc3ab3a6d217daf71f2f8c9b87bb6b582b68ea1dd8bc,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        'composable': 0xeca50f366d466839833e9da4c3b3e225a838a6119d5684ae9f806a7e2da02436,
        'patricia':   0x3e6eaf65f17de9df5f30cfe1d9077beee656bc033d1de56b2686d2b43a502cef,
    },
    {
        b'abcdef':    six.int2byte(4),
        'composable': 0x58c80ea87e9b69fc8565c39906c39a2e3b03b4aa5624257f35736c2908ce3afc,
        'patricia':   0x41030e65b2afed047c10ef82d999de4f4fa06bcf56719fbd88e01b1fa9c9ac6f,
    },
    {
        b'':          six.int2byte(1),
        b'abcdef':    six.int2byte(4),
        'composable': 0x233a451b0f345216936c14f3c5e9dcdaf3cb89b97b31f585dbd52c847690413e,
        'patricia':   0x0611c34f2c929224ce0fa3abc837e170816e49dba813ad0e8a8f71f95c7ca79a,
    },

    {
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        'composable': 0x44c74e7efd09ae5f57c59f16d3ac6cb7f83a744ede69f134031bb192a4b90652,
        'patricia':   0xe04c428b42bc9daba440bafc134ba9fd4e73ffbd593747b399453af21d1be6a9,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        'composable': 0xf83d03d75a3dc9241f5f9e0ceb9a7a5e00eb4213294d71eaa1708efbf7f9a180,
        'patricia':   0xa70dc987895722e54a39deff21cda97b18556fe36aa7abc4e3664e4a9a22514d,
    },
    {
        b'abcxyz':    six.int2byte(8),
        'composable': 0x3de84a5ec5f66c8c8a6233fdc42a9772d4df08140dc1ebea0dfca7a45d61a737,
        'patricia':   0x1d307af149a06996af998fd062a7db6b80fd932cf59576c4e70f5d5dff6cf44f,
    },
    {
        b'':          six.int2byte(1),
        b'abcxyz':    six.int2byte(8),
        'composable': 0xc4ed1bcce32adbc8ddb4a07fd50c04519d0059c437ded072708f92354ec3b90c,
        'patricia':   0x2d29d0fae66d75ee4722254db81ed5a2755bcabc5a057d159730b23ca467f4be,
    },
    {
        b'abc':       six.int2byte(2),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x3a6fe50b9161e05fad906254ea86e24bc71eb06570f757674ae6da815ab7c4d4,
        'patricia':   0x25de5daa3649d2f5bf7b16966372491bedfa21512979390f595f860a57fb9a6c,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        b'abcxyz':    six.int2byte(8),
        'composable': 0xb037f8033c5c49b9f0af01bcac55dca0c55c0c3062a9ec19ad71006c1c7b255b,
        'patricia':   0x7845ccce0229f69bcb8b16d28647ac7393dca4dbc493f0e296003c85e23c254b,
    },
    {
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x3c8cd8efee3380323cb3cf9f4eb96f36350fc82028391dc23261f2bfc6ff5baa,
        'patricia':   0x180d5e1369bc0b174243c591a5a75cf22b3783d9a790ee454a473aab4328ff36,
    },
    {
        b'':          six.int2byte(1),
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0xcfa0d32dbcf3deeab8e0160d9e8dc4c8bdbc5231914e80517cc82e9d19b82e07,
        'patricia':   0xc7da4a76599f2bc2df2a3ce35a3e6f0ad9d5f144c825f2964dbf1224a9b6e671,
    },
    {
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0xc08f682925d4ab141ee77526eb8e36b2129b4e1f602d8a1e8607be34dbbe0836,
        'patricia':   0x42a9737cc038dc57e9142d8f245c37a29829a215163a92d7a367d6d717bbe872,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0xdddb1c7b3b226ff25f2720a6e0c2d1f033cacec0e07c992ec3a9baa24ab14444,
        'patricia':   0x4daa1268c408114b7b37d009316a1e496a5d4809dbd6e66c334c53d903fe8c43,
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
