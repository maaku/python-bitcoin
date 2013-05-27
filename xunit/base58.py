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

import bitcoin.base58

BASE58 = [
    dict(data='', result=''),
    dict(data=chr(0), result='1'),
    dict(data=chr(0)+('1f8b1340c286881bcc449c37569ae320b013785d'+'48427760').decode('hex'),
         result='13snZ4ZyCzaL7358SmgvHGC9AxskqumNxP'),
]

class TestCodecBase58(unittest2.TestCase):
    "Test encoding and decoding of base58 values."
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = BASE58
        def __test__(self, data, result):
            self.assertEqual(data.encode('base58'), result)
    class test_deserialize(ScenarioTest):
        scenarios = BASE58
        def __test__(self, data, result):
            self.assertEqual(result.decode('base58'), data)

#
# End of File
#
