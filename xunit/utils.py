# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

from bitcoin.utils import *

TARGET_FROM_COMPACT = [
    dict(bits=0x1d00ffff,
         target=0x00000000FFFF0000000000000000000000000000000000000000000000000000L),
    dict(bits=0x1b0404cb,
         target=0x00000000000404CB000000000000000000000000000000000000000000000000L),
]

class TestCompactTarget(unittest2.TestCase):
    "Test target_from_compact API under a variety of scenarios."
    __metaclass__ = ScenarioMeta
    class test_hash_from_compact(ScenarioTest):
        scenarios = TARGET_FROM_COMPACT
        def __test__(self, bits, target):
            self.assertEqual(target_from_compact(bits), target)

#
# End of File
#
