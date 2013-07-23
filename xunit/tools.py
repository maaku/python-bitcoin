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

from bitcoin.tools import *

# ===----------------------------------------------------------------------===

COMPRESS_AMOUNT_POINTS = [
    dict(n =                0, x =         0),
    dict(n =                1, x =       0x1),
    dict(n =          1000000, x =       0x7),
    dict(n =        100000000, x =       0x9),
    dict(n =       5000000000, x =      0x32),
    dict(n = 2100000000000000, x = 0x1406f40),
]

COMPRESS_AMOUNT_INTERVALS = [
    dict(start =          1, stop =           100000, step =          1),
    dict(start =    1000000, stop =      10000000000, step =    1000000),
    dict(start =  100000000, stop =    1000000000000, step =  100000000),
    dict(start = 5000000000, stop = 2100000000000000, step = 5000000000),
]

class TestCompressAmount(unittest2.TestCase):
    "Test compression and decompression of amounts."
    __metaclass__ = ScenarioMeta
    class test_compress_point(ScenarioTest):
        scenarios = COMPRESS_AMOUNT_POINTS
        def __test__(self, n, x):
            self.assertEqual(compress_amount(n), x)
    class test_decompress_point(ScenarioTest):
        scenarios = COMPRESS_AMOUNT_POINTS
        def __test__(self, n, x):
            self.assertEqual(decompress_amount(x), n)
    class test_interval(ScenarioTest):
        scenarios = COMPRESS_AMOUNT_INTERVALS
        def __test__(self, start, stop, step):
            for n in xrange(start, stop, step):
                self.assertEqual(decompress_amount(compress_amount(n)), n, u"n=%d"%n)

# ===----------------------------------------------------------------------===

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
