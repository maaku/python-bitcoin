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

# Scenario unit-testing
from scenariotest import ScenarioMeta, ScenarioTest

from bitcoin.hash import *

# ===----------------------------------------------------------------------===

HASH160 = [
    dict(data  = b'',
         hash_ = 0xcb9f3b7c6fb1cf2c13a40637c189bdd066a272b4),
    dict(data  = b'abc',
         hash_ = 0x33dce478a942391c98a36aa5d74424148ce91bbb),
    dict(data  = ('BGeK/bD+VUgnGWfxpnEwtxBc1qgo4DkJpnli4OofYd62Sfa8P0zvOMTzVQTlHsES3lw4Tfe6C41X'
                  'ikxwK2vxHV8=').decode('base64'),
         hash_ = 0x188fb8eb50fbf0f6eb995342d527bf5cb107e962),
]

class TestHash160(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_hash160(ScenarioTest):
        scenarios = HASH160
        def __test__(self, data, hash_):
            self.assertEqual(hash160(data).intdigest(), hash_)

# ===----------------------------------------------------------------------===

HASH256 = [
    dict(data  = b'',
         hash_ = 0x56944c5d3f98413ef45cf54545538103cc9f298e0575820ad3591376e2e0f65d),
    dict(data  = b'abc',
         hash_ = 0x58636c3ec08c12d55aedda056d602d5bcca72d8df6a69b519b72d32dc2428b4f),
    dict(data  = ('AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAO6Pt/Xp7ErJ6xyw+Z3aPYX/IG8OI'
                  'ilEyOp+4qkseXkopq19J//8AHR2sK3w=').decode('base64'),
         hash_ = 0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f),
]

class TestHash256(unittest2.TestCase):
    __metaclass__ = ScenarioMeta
    class test_hash256(ScenarioTest):
        scenarios = HASH256
        def __test__(self, data, hash_):
            self.assertEqual(hash256(data).intdigest(), hash_)

#
# End of File
#
