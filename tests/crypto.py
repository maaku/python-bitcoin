#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === bitcoin.crypto_test -------------------------------------------------===
# Copyright © 2012 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
# ===----------------------------------------------------------------------===

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

from bitcoin.crypto import merkle

MERKLE_LIST = [
    dict(list_=[], root=0),
    dict(list_=[0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33bL],
         root=0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33bL),
    dict(list_=[0x50671f9e3b0719fcd23b2976eedf6e0a6f19ae7a8f023c3e66b9b1fbe207a006L,
                0x603b9dbb388987175f8ddbdae9a8ad77a999e63b356e6172b331905387b515f7L,
                0xec258956c3069ea974a569fbacd320fd183d65fa6d4c318ad4e55da6260c0f3dL],
         root=0x5d438b61fa23d20bfac0a6eaf5c426e2abdd48637c7dd70a620b0b7ab7cd6092L),
    dict(list_=[0x9156235baa55ea841c4384faa543004fd5a56661d22dfbc2bbd5313c85044e08L,
                0xc6f50393c676f1f3b669c93f62c3f0e46349f6d2aff13ed8976bd649382ff6fcL,
                0x4817fad15ce7604ae5a478888a29b4ade8000596a0e9267747b1d4f0bd1a6defL,
                0x16952eba67618e90857d530a63477ea09dd89575ac00c114e20e8068b4e0297cL],
         root=0xb1cd750f2a242deeaf3b452aa69a4a46f9f66e866c07eda22677f1287688bb1eL),
]

class TestMerkle(unittest2.TestCase):
    "Test merkle API under a variety of scenarios."
    __metaclass__ = ScenarioMeta
    class test_merkle_root(ScenarioTest):
        scenarios = MERKLE_LIST
        def __test__(self, list_, root):
            self.assertEqual(merkle(list_), root)

NESTED_MERKLE = [
    dict(list_=[0x67050eeb5f95abf57449d92629dcf69f80c26247e207ad006a862d1e4e6498ffL,
                [0x9c2e4d8fe97d881430de4e754b4205b9c27ce96715231cffc4337340cb110280L,
                 [0x0c08173828583fc6ecd6ecdbcca7b6939c49c242ad5107e39deb7b0a5996b903L],
                 0x80903da4e6bbdf96e8ff6fc3966b0cfd355c7e860bdd1caa8e4722d9230e40acL],
                0x5a9eab9148389395eff050ddf00220d722123ca8736c862bf200316389b3f611L,
                0xb2928391f8a477a27749a556b7386f4da4391e98df1c76459ba7f4ac2ee1a8f7L,
                [0x93f620df2bb7d859378709f71b820725ef54d985e86662c51027ccfd18d66208L,
                 [0x68b6acce6948c45ed26e193c33443b4aedc1c25e6f96e29a3d939a774f8b74d1L,
                  0xa8e26fa85a95a531ebd98b4454d17790430cc4a11ce157e2ad051f7c3c128ce8L],
                 0x9823a2989686ae381368f8f461f09a146f65b9a60c33592ca9613bcebe9abce0L],
                [0xbf5d3affb73efd2ec6c36ad3112dd933efed63c4e1cbffcfa88e2759c144f2d8L,
                 0x39361160903c6695c6804b7157c7bd10013e9ba89b1f954243bc8e3990b08db9L],
                0x6632753d6ca30fea890f37fc150eaed8d068acf596acb2251b8fafd72db977d3L],
         root=0x681ac33995f3421e8302a55cf929b9d84031cf5f5bb6ec5898435b6dbdb5455fL),
]

class TestNestedMerkle(unittest2.TestCase):
    "Test merkle API using explicit (version=2) Merkle trees."
    __metaclass__ = ScenarioMeta
    class test_merkle_root(ScenarioTest):
        scenarios = NESTED_MERKLE
        def __test__(self, list_, root):
            self.assertEqual(merkle(list_), root)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
