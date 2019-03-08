# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

from six.moves import xrange

# Python standard library, unit-testing
import unittest

# Scenario unit-testing
from scenariotest import ScenarioMeta, ScenarioTest

# Python bitcoin, iterator compare
from bitcoin.tools import icmp

from bitcoin.merkle import *

# ===----------------------------------------------------------------------===

MERKLE = [
    dict(list_=[], root=0),
    dict(list_=[0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b],
         root=0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b),
    dict(list_=[0x50671f9e3b0719fcd23b2976eedf6e0a6f19ae7a8f023c3e66b9b1fbe207a006,
                0x603b9dbb388987175f8ddbdae9a8ad77a999e63b356e6172b331905387b515f7,
                0xec258956c3069ea974a569fbacd320fd183d65fa6d4c318ad4e55da6260c0f3d],
         root=0x5d438b61fa23d20bfac0a6eaf5c426e2abdd48637c7dd70a620b0b7ab7cd6092),
    dict(list_=[0x9156235baa55ea841c4384faa543004fd5a56661d22dfbc2bbd5313c85044e08,
                0xc6f50393c676f1f3b669c93f62c3f0e46349f6d2aff13ed8976bd649382ff6fc,
                0x4817fad15ce7604ae5a478888a29b4ade8000596a0e9267747b1d4f0bd1a6def,
                0x16952eba67618e90857d530a63477ea09dd89575ac00c114e20e8068b4e0297c],
         root=0xb1cd750f2a242deeaf3b452aa69a4a46f9f66e866c07eda22677f1287688bb1e),
    dict(list_=[0x9156235baa55ea841c4384faa543004fd5a56661d22dfbc2bbd5313c85044e08,
                0xc6f50393c676f1f3b669c93f62c3f0e46349f6d2aff13ed8976bd649382ff6fc,
                0x4817fad15ce7604ae5a478888a29b4ade8000596a0e9267747b1d4f0bd1a6def,
                0x16952eba67618e90857d530a63477ea09dd89575ac00c114e20e8068b4e0297c],
         root=0xb1cd750f2a242deeaf3b452aa69a4a46f9f66e866c07eda22677f1287688bb1e),
    dict(list_=[0x9c2e4d8fe97d881430de4e754b4205b9c27ce96715231cffc4337340cb110280,
                0x0c08173828583fc6ecd6ecdbcca7b6939c49c242ad5107e39deb7b0a5996b903,
                0x80903da4e6bbdf96e8ff6fc3966b0cfd355c7e860bdd1caa8e4722d9230e40ac,
                0x5a9eab9148389395eff050ddf00220d722123ca8736c862bf200316389b3f611,
                0xb2928391f8a477a27749a556b7386f4da4391e98df1c76459ba7f4ac2ee1a8f7],
         root=0xaf42142cf6dcc361144bfaeaa0041bbba927f8d7f6998c35ba6623ab7e2cd5b7),
]

class TestMerkle(unittest.TestCase):
    "Test merkle API under a variety of scenarios."
    __metaclass__ = ScenarioMeta
    class test_merkle(ScenarioTest):
        scenarios = MERKLE
        def __test__(self, list_, root):
            self.assertEqual(merkle(list_), root)

NESTED_MERKLE = [
    dict(list_=[0x67050eeb5f95abf57449d92629dcf69f80c26247e207ad006a862d1e4e6498ff,
                [0x9c2e4d8fe97d881430de4e754b4205b9c27ce96715231cffc4337340cb110280,
                 [0x0c08173828583fc6ecd6ecdbcca7b6939c49c242ad5107e39deb7b0a5996b903],
                 0x80903da4e6bbdf96e8ff6fc3966b0cfd355c7e860bdd1caa8e4722d9230e40ac],
                0x5a9eab9148389395eff050ddf00220d722123ca8736c862bf200316389b3f611,
                0xb2928391f8a477a27749a556b7386f4da4391e98df1c76459ba7f4ac2ee1a8f7,
                [0x93f620df2bb7d859378709f71b820725ef54d985e86662c51027ccfd18d66208,
                 [0x68b6acce6948c45ed26e193c33443b4aedc1c25e6f96e29a3d939a774f8b74d1,
                  0xa8e26fa85a95a531ebd98b4454d17790430cc4a11ce157e2ad051f7c3c128ce8],
                 0x9823a2989686ae381368f8f461f09a146f65b9a60c33592ca9613bcebe9abce0],
                [0xbf5d3affb73efd2ec6c36ad3112dd933efed63c4e1cbffcfa88e2759c144f2d8,
                 0x39361160903c6695c6804b7157c7bd10013e9ba89b1f954243bc8e3990b08db9],
                0x6632753d6ca30fea890f37fc150eaed8d068acf596acb2251b8fafd72db977d3],
         root=0x681ac33995f3421e8302a55cf929b9d84031cf5f5bb6ec5898435b6dbdb5455f),
]

class TestNestedMerkle(unittest.TestCase):
    "Test merkle API using explicit (version=2) Merkle trees."
    __metaclass__ = ScenarioMeta
    class test_nested_merkle_root(ScenarioTest):
        scenarios = NESTED_MERKLE
        def __test__(self, list_, root):
            self.assertEqual(merkle(list_), root)

# ===----------------------------------------------------------------------===

MERKLE_NODE = [
    # size: 0 - ()
    dict(args=(), kwargs={}, size=0, length=0, root=0, items=()),
    # size: 1 - (0) ()
    dict(args=(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,),
         kwargs={}, size=1, length=1,
         root=0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),)),
    dict(args=(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,),
         kwargs={'length': 0}, size=1, length=0,
         root=0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
         items=()),
    # size: 2 - (0,1) (0) (1) ()
    dict(args=(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
               0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
         kwargs={}, size=2, length=2,
         root=0xd15009bc67687122cfe2c8c48af6913d984f447391686c1a0a31ffac3f035b01,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a))),
    dict(args=(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
               0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
         kwargs={'prune': MerkleNode.RIGHT_NODE}, size=2, length=1,
         root=0xd15009bc67687122cfe2c8c48af6913d984f447391686c1a0a31ffac3f035b01,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),)),
    dict(args=(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
               0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
         kwargs={'prune': MerkleNode.LEFT_NODE}, size=2, length=1,
         root=0xd15009bc67687122cfe2c8c48af6913d984f447391686c1a0a31ffac3f035b01,
         items=((1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),)),
    dict(args=(0xd15009bc67687122cfe2c8c48af6913d984f447391686c1a0a31ffac3f035b01,),
         kwargs={'size': 2}, size=2, length=0,
         root=0xd15009bc67687122cfe2c8c48af6913d984f447391686c1a0a31ffac3f035b01,
         items=()),
    # size: 3 - (0,1,2) (0,1) (0,2) (1,2) (0) (1) (2) ()
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          size=1)),
         kwargs={}, size=3, length=3,
         root=0xd4002b196e527f58e3c2e84fe7f9713d028ab45760ac700d880f6a9193c174f8,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
                (2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
               0x52bece593e18e33360d4f2352a4bcbcba2ff52faf99e17a196a8d6d8ad25667b),
         kwargs={'size':3}, size=3, length=2,
         root=0xd4002b196e527f58e3c2e84fe7f9713d028ab45760ac700d880f6a9193c174f8,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.RIGHT_NODE),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          size=1)),
         kwargs={}, size=3, length=2,
         root=0xd4002b196e527f58e3c2e84fe7f9713d028ab45760ac700d880f6a9193c174f8,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.LEFT_NODE),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          size=1)),
         kwargs={}, size=3, length=2,
         root=0xd4002b196e527f58e3c2e84fe7f9713d028ab45760ac700d880f6a9193c174f8,
         items=((1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
                (2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.RIGHT_NODE),
               0x52bece593e18e33360d4f2352a4bcbcba2ff52faf99e17a196a8d6d8ad25667b),
         kwargs={'size':3}, size=3, length=1,
         root=0xd4002b196e527f58e3c2e84fe7f9713d028ab45760ac700d880f6a9193c174f8,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),)),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.LEFT_NODE),
               0x52bece593e18e33360d4f2352a4bcbcba2ff52faf99e17a196a8d6d8ad25667b),
         kwargs={'size':3}, size=3, length=1,
         root=0xd4002b196e527f58e3c2e84fe7f9713d028ab45760ac700d880f6a9193c174f8,
         items=((1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),)),
    dict(args=(MerkleNode(0xd15009bc67687122cfe2c8c48af6913d984f447391686c1a0a31ffac3f035b01,
                          size=2),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          size=1)),
         kwargs={}, size=3, length=1,
         root=0xd4002b196e527f58e3c2e84fe7f9713d028ab45760ac700d880f6a9193c174f8,
         items=((2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf),)),
    dict(args=(0xd4002b196e527f58e3c2e84fe7f9713d028ab45760ac700d880f6a9193c174f8,),
         kwargs={'size': 3}, size=3, length=0,
         root=0xd4002b196e527f58e3c2e84fe7f9713d028ab45760ac700d880f6a9193c174f8,
         items=()),
    # size: 4 - (0,1,2,3) (0,1,2) (0,1,3) (0,2,3) (1,2,3) (0,1) (0,2) (0,3) (1,2) (1,3) (2,3) (0) (1) (2) (3) ()
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3)),
         kwargs={}, size=4, length=4,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
                (2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf),
                (3, 0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3,
                          prune=MerkleNode.RIGHT_NODE)),
         kwargs={}, size=4, length=3,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
                (2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3,
                          prune=MerkleNode.LEFT_NODE)),
         kwargs={}, size=4, length=3,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
                (3, 0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.RIGHT_NODE),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3)),
         kwargs={}, size=4, length=3,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf),
                (3, 0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.LEFT_NODE),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3)),
         kwargs={}, size=4, length=3,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
                (2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf),
                (3, 0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
               0x4b5e71b3f7b1d9aefe6095f2cbb5b8906092f10cbb2f5a2a1a46b3f90c178b9c),
         kwargs={'size': 4}, size=4, length=2,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.RIGHT_NODE),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3,
                          prune=MerkleNode.RIGHT_NODE)),
         kwargs={}, size=4, length=2,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.RIGHT_NODE),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3,
                          prune=MerkleNode.LEFT_NODE)),
         kwargs={}, size=4, length=2,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),
                (3, 0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.LEFT_NODE),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3,
                          prune=MerkleNode.RIGHT_NODE)),
         kwargs={}, size=4, length=2,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
                (2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.LEFT_NODE),
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3,
                          prune=MerkleNode.LEFT_NODE)),
         kwargs={}, size=4, length=2,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),
                (3, 0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3))),
    dict(args=(0xd15009bc67687122cfe2c8c48af6913d984f447391686c1a0a31ffac3f035b01,
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3)),
         kwargs={'size': 4}, size=4, length=2,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf),
                (3, 0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3))),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.RIGHT_NODE),
               0x4b5e71b3f7b1d9aefe6095f2cbb5b8906092f10cbb2f5a2a1a46b3f90c178b9c),
         kwargs={'size': 4}, size=4, length=1,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((0, 0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091),)),
    dict(args=(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                          0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a,
                          prune=MerkleNode.LEFT_NODE),
               0x4b5e71b3f7b1d9aefe6095f2cbb5b8906092f10cbb2f5a2a1a46b3f90c178b9c),
         kwargs={'size': 4}, size=4, length=1,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((1, 0xed5c9cf14730b62c8fa6b3b832ef434d7e6cbf8d287f7da2069843539ba5de8a),)),
    dict(args=(0xd15009bc67687122cfe2c8c48af6913d984f447391686c1a0a31ffac3f035b01,
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3,
                          prune=MerkleNode.RIGHT_NODE)),
         kwargs={'size': 4}, size=4, length=1,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((2, 0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf),)),
    dict(args=(0xd15009bc67687122cfe2c8c48af6913d984f447391686c1a0a31ffac3f035b01,
               MerkleNode(0xf6e10859842607b0fb3b862c22570cf3f6b9e13a19fabc270089c0ee8973acbf,
                          0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3,
                          prune=MerkleNode.LEFT_NODE)),
         kwargs={'size': 4}, size=4, length=1,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=((3, 0x5228cfc7bff1116626f3e67e651c6f7a7b11d5cdaf2743e35c757ae61125d3c3),)),
    dict(args=(0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,),
         kwargs={'size': 4}, size=4, length=0,
         root=0x6098ac067e8b806407a49a11b3060c3b5384ef688eb7ceeedee1eddd81baee75,
         items=()),
    # size: 14, sparse proof
    dict(args=(0x4429e0ce202f421a594d5759f415a81b9dea2ce32f078d11117258eca4fff3de,
               MerkleNode(MerkleNode(0xc08194bd2818a44e9a3684439a27d5d46e00eb938b01c6a1671f03bf498a3193,
                                     MerkleNode(0xe538cf8c7af1478ba250545d1ab713c095c19436b9c6f07581c0918b02190fd5,
                                                0x91e634b012a7ffed4a5522994d603a20ab9f667dc2bb7895904d2a33650e8cca,
                                                prune=MerkleNode.RIGHT_NODE),
                                     size=4),
                          0x3193f206ff1f5a617f87ca4933fbd2df32330121dec08418ab9917de603cd940,
                          size=5)),
         kwargs={'size': 14}, size=14, length=1,
         root=0xdacbf23f685bb16b7cce74fe088256349dd5f8cefad090bbe55aa88b3b8f7163,
         items=((10, 0xe538cf8c7af1478ba250545d1ab713c095c19436b9c6f07581c0918b02190fd5),)),
]

class TestMerkleNodeScenarios(unittest.TestCase):
    __metaclass__ = ScenarioMeta
    class test_merkle_node_init(ScenarioTest):
        scenarios = MERKLE_NODE
        def __test__(self, args, kwargs, size, length, root, items):
            mn = MerkleNode(*args, **kwargs)
            self.assertEqual(mn.size, size, (args, kwargs))
            self.assertEqual(mn.length, length)

    class test_merkle_node_hash(ScenarioTest):
        scenarios = MERKLE_NODE
        def __test__(self, args, kwargs, size, length, root, items):
            mn = MerkleNode(*args, **kwargs)
            self.assertEqual(mn.hash, root)

    class test_merkle_node_iter(ScenarioTest):
        scenarios = MERKLE_NODE
        def __test__(self, args, kwargs, size, length, root, items):
            mn = MerkleNode(*args, **kwargs)
            self.assertEqual(icmp(iter(mn), (hash_ for idx,hash_ in items)), 0)

    class test_merkle_node_reversed(ScenarioTest):
        scenarios = MERKLE_NODE
        def __test__(self, args, kwargs, size, length, root, items):
            mn = MerkleNode(*args, **kwargs)
            self.assertEqual(icmp(reversed(mn), (hash_ for idx,hash_ in reversed(items))), 0)

class TestMerkleNode(unittest.TestCase):
    def test_init_invalid(self):
        # Empty list
        with self.assertRaises(TypeError):
            MerkleNode(right=0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091)
        with self.assertRaises(TypeError):
            MerkleNode(size=1)
        with self.assertRaises(TypeError):
            MerkleNode(length=1)
        with self.assertRaises(TypeError):
            MerkleNode(size=1, length=1)
        with self.assertRaises(TypeError):
            MerkleNode(prune=MerkleNode.LEFT_NODE)
        with self.assertRaises(TypeError):
            MerkleNode(prune=MerkleNode.RIGHT_NODE)

        # Single element or fully pruned list
        with self.assertRaises(TypeError):
            MerkleNode(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091))
        with self.assertRaises(TypeError):
            MerkleNode(MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                                  0x9185d9dd0d7d7fd062351fc9f892419c3b84a0ade87ab2a8afd5ce0a1cf495d8))
        with self.assertRaises(TypeError):
            MerkleNode(left=MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091))
        with self.assertRaises(TypeError):
            MerkleNode(left=MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                                       0x9185d9dd0d7d7fd062351fc9f892419c3b84a0ade87ab2a8afd5ce0a1cf495d8))
        with self.assertRaises(TypeError):
            MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091, length=2)
        with self.assertRaises(TypeError):
            MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091, size=2, length=2)

        mn = MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                        prune=None)
        self.assertEqual(mn.size, 1)
        self.assertEqual(mn.length, 1)
        self.assertIs(mn.prune, None)
        mn = MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                        length=0)
        self.assertEqual(mn.size, 1)
        self.assertEqual(mn.length, 0)
        self.assertIs(mn.prune, mn.LEFT_NODE)
        mn = MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                        prune=MerkleNode.LEFT_NODE)
        self.assertEqual(mn.size, 1)
        self.assertEqual(mn.length, 0)
        self.assertIs(mn.prune, mn.LEFT_NODE)
        with self.assertRaises(TypeError):
            MerkleNode(0x5880db25cc6daec28346dd784d1e632515c5e13997c055b05be6e9aeac918091,
                       prune=MerkleNode.RIGHT_NODE)

# ===----------------------------------------------------------------------===

class TestMerkleList(unittest.TestCase):
    __metaclass__ = ScenarioMeta
    class test_merkle_list(ScenarioTest):
        scenarios = MERKLE
        def __test__(self, list_, root):
            self.assertEqual(MerkleList(list_).hash, root)
