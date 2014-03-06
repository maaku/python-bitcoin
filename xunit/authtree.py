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

leaf_value = BaseAuthTreeNode(b'123')
SCENARIOS = [
    dict(value = None, children = [],
         str_  = b'\x00\x00',
         composable = 0xc7cf090a63780b417eb8c55da3daf05791308a0fc393ee7bc685f224d296a296,
         patricia   = 0xc7cf090a63780b417eb8c55da3daf05791308a0fc393ee7bc685f224d296a296),
    dict(value = b'abc', children = [],
         str_  = b'\x10' b'\x00' b'\x03abc',
         composable = 0xeef6ab09ad94027c945d4b1a8639fbd8121dc011f9b760266dbc1cdaf264c6f0,
         patricia   = 0xeef6ab09ad94027c945d4b1a8639fbd8121dc011f9b760266dbc1cdaf264c6f0),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b0'), leaf_value)],
         str_  = b'\x11' b'\x00' b'\x03abc' b'\x10\x00\x03123',
         composable = 0x2de27c2b22e22ed819a2529e5e85bf5d6c22a82f6538cc18b8e132b2613c7a8c,
         patricia   = 0x2de27c2b22e22ed819a2529e5e85bf5d6c22a82f6538cc18b8e132b2613c7a8c),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b00'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x02' b'\x10\x00\x03123',
         composable = 0x9224bded71ceb9f6465bbb7815cd8c16b1e14372b4b071786dbf165dfdfba846,
         patricia   = 0x55ac8af8a66b1e0225a0478c5cf740cf9150bc5727536553a0b35ef26ca62680),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b010'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x05' b'\x10\x00\x03123',
         composable = 0x8933af0fece6cbc838e3e9eee1541ba5c0bb8ee649d9401713946a0972c477f8,
         patricia   = 0x52c07a38409849d11fbc4360d5782ed535138c9119b7e9e902fa8ce5c5b357eeL),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b0110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x0b' b'\x10\x00\x03123',
         composable = 0xe56397a7e9dd56bfc7ff4d60238a56a4e9b24dbcccd84aada29ffb1223f83283,
         patricia   = 0xed658e1b90cc93ce6a8b43e8d8107fc07572f3330b72ca0e78f915a265256f53),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b00110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x16' b'\x10\x00\x03123',
         composable = 0x2cb6333537a47209536cb49f23896de195bdbe65cbaa5663cacea73dcce8706d,
         patricia   = 0xd5b27799e24e78c1fc5eae04826d306f6d028ba8131455e20d588d317ccc9e25),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b000110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x2c' b'\x10\x00\x03123',
         composable = 0xe12e8313eb5b70c719ca29cc560e94ac4052a41579dd465fc841e6dc88cd402f,
         patricia   = 0xe096400c775f344925830d1f2c081e74657fbb0b2ff3e2890e18408189859d54),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b0000110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\x58' b'\x10\x00\x03123',
         composable = 0xe32c8f118131648b1aea09f6b8296ceccb6a50e224f64a0658f366b474ac00ea,
         patricia   = 0x0cdc1b89c8198a8410362553fe93baa6b5b37e23cbbd89bd4ff2273bf59eb760),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b01000110'), leaf_value)],
         str_  = b'\x12' b'\x00' b'\x03abc' b'\xb1' b'\x10\x00\x03123',
         composable = 0x69c54564804ec98b6429c1eb67ad8c4b8d1a2a45979b701f19431233328dd078,
         patricia   = 0xc97515754ee3eeae2e3363dd776bc1a60fe119c32795d9b00c2c874fa9d96e90),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b011000110'), leaf_value)],
         str_  = b'\x13' b'\x00' b'\x03abc' b'\x00\x63' b'\x10\x00\x03123',
         composable = 0x6e44e08e81053f37e7469d48052eae814a19923749c386578662152f65fe2700,
         patricia   = 0xa99550e50076d293f00ce51f64fa406602a3ff79c748bdc9328a913ec4f603dd),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b0111000110'), leaf_value)],
         str_  = b'\x13' b'\x00' b'\x03abc' b'\x01\xc7\x00' b'\x10\x00\x03123',
         composable = 0x49beda66746d36f67e8e3b5e8d0defa3241a4ee91d4a0924a6e9ef30d74a4b6d,
         patricia   = 0xa9988c44ba6c433e42a8f841a138e227c9b50f8bd47a7404a1d45c3c62ed5c19),
    dict(value = b'abc', children = [AuthTreeLink(Bits('0b01111000110'), leaf_value)],
         str_  = b'\x13' b'\x00' b'\x03abc' b'\x02\x8f\x01' b'\x10\x00\x03123',
         composable = 0xe98e9650fbf4952f0d902fac577014a0a7c3b40cb150b913fda1ab215ed374d4,
         patricia   = 0x5bb1036c96459140ee2fa4bb39986c060afed0e2667bf795a5977b5d0186d784),
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
        'composable': 0x7423966829f7667518468c3ec2fab595a6e3f19df71dd1ff7a09a702eecd5ac1,
        'patricia':   0x1bfb76e7b62866a9f784b9df34f6849250a4d36c86cdb9fc105e1328213ae285,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        'composable': 0x9c63e1779fea474dac4af43474e2584037f0d55bd9502eff7e2de2a5767230a0,
        'patricia':   0x24ec71997cfeefab42a55e88701263010ff9f3f096af0437d735a9a6b9cacb21,
    },
    {
        b'abcdef':    six.int2byte(4),
        'composable': 0xbf18452c7c607af93adbe43c8e744370b734a92d821ae4a5fa4d1913f604c502,
        'patricia':   0xbbd291152279791f85e15c6e1b858039495899c724a73220c25f2fd72a99de2f,
    },
    {
        b'':          six.int2byte(1),
        b'abcdef':    six.int2byte(4),
        'composable': 0x8ead775666349d198ee351ca7ae3f8611f4dab245e2cd6e5d9dc4904679a3f47,
        'patricia':   0xd7a0b54767763cf66a5294f3dda67d029e8847acfa40c789f2d8ef4d38f48117,
    },

    {
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        'composable': 0x8466f60df5348ba0a7f231ebcb12d5f79d3da7d5cc48f31814a592d672bf19ab,
        'patricia':   0x4d1963d96a9da4ddd30142f608e3ddc78472df04be69ac51c01bca0922010c8f,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        'composable': 0x5c6636db2a644ca001b89a2baba14e001882498bd8286cc20ce8bd95883c8b39,
        'patricia':   0x7f5959b64e412f279f3cfbae4b32369db0efea5c8bb74d9471b0760730aeb788,
    },
    {
        b'abcxyz':    six.int2byte(8),
        'composable': 0x2f9064e19b69d9595b0029a0ab74a0709f9de2b7d425f47484d72974624c8afc,
        'patricia':   0xb2fea1b9cc600997cc3dbbf8b4c2a1af83857eefc472294d18dadb8b764d392b,
    },
    {
        b'':          six.int2byte(1),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x77e520c968cf71569ddf6b3341efae43979c1a03ca43874e85b2a2299728678c,
        'patricia':   0x930026f51f2f0d2bd8edd4c8bf012b724e9391530a0133ea41471e456c6eaaf0,
    },
    {
        b'abc':       six.int2byte(2),
        b'abcxyz':    six.int2byte(8),
        'composable': 0xa4c405c724a59a6a2991f938473e8402ed79cbe6a601a21a6b9729572355ade0,
        'patricia':   0x3603ce839a34a29b00e99f3e7552ed69455289b3b898a869d83fa547f61c5891,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x246596d170928b312743d48d5490a52e32b256d02a80200cd8a239aefd10dd82,
        'patricia':   0xf21c6f60039cecdbaa8a9dea8ac07881818ace376c059729ad1277c46f4942be,
    },
    {
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x6ae4c45260bea63d2b9c164b44f3ce9420806921b614f33da0575e18fa1d6480,
        'patricia':   0xf14eb00f679391d08090d764aefc30cc8c571062fce7e955ee8844716319d961,
    },
    {
        b'':          six.int2byte(1),
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0xc08bc4ff0524f09f72f77956217e81f218bf98f3627bb5e153999b62e8584b5b,
        'patricia':   0xcb372c57024b250201df096da2bddfd2f5bd1c08c7a6e41a662356315437c1b1,
    },
    {
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0x21374e1e1d1b6e140b64e78f5264f2a9316679b06ba003a15562e02a2ede283e,
        'patricia':   0x78783ba6e76ca4313c5db2007df76fd0225318c90491975b737a40a6bdc4dab0,
    },
    {
        b'':          six.int2byte(1),
        b'abc':       six.int2byte(2),
        b'abcdef':    six.int2byte(4),
        b'abcxyz':    six.int2byte(8),
        'composable': 0xc2a2b24313b41e340b5010d623822ae1dc0dbf2f398ad9ad16ab3d2720c2d46f,
        'patricia':   0x48623cc83da0e05c30878058d657c06242d122efd778ff6dca48af67a2c9d263,
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
