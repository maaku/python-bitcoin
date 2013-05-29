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

BASE58_CODEC = [
    dict(data='', result=''),
    dict(data=chr(0), result='1'),
    dict(data=chr(0)+('1f8b1340c286881bcc449c37569ae320b013785d'+'48427760').decode('hex'),
         result='13snZ4ZyCzaL7358SmgvHGC9AxskqumNxP'),
    # src/test/data/base58_encode_decode.json:
    dict(data='61'.decode('hex'), result='2g'),
    dict(data='626262'.decode('hex'), result='a3gV'),
    dict(data='636363'.decode('hex'), result='aPEr'),
    dict(data='516b6fcd0f'.decode('hex'), result='ABnLTmg'),
    dict(data='bf4f89001e670274dd'.decode('hex'), result='3SEo3LWLoPntC'),
    dict(data='572e4794'.decode('hex'), result='3EFU7m'),
    dict(data='ecac89cad93923c02321'.decode('hex'), result='EJDM8drfXA6uyA'),
    dict(data='10c8511e'.decode('hex'), result='Rt5zm'),
    dict(data='00000000000000000000'.decode('hex'), result='1111111111'),
    dict(data='73696d706c792061206c6f6e6720737472696e67'.decode('hex'),
         result='2cFupjhnEsSn59qHXstmK2ffpLv2'),
    dict(data='00eb15231dfceb60925886b67d065299925915aeb172c06647'.decode('hex'),
         result='1NS17iag9jJgTHD1VXjvLCEnZuQ3rJDE9L'),
]

class TestCodecBase58(unittest2.TestCase):
    "Test encoding and decoding of base58 values."
    __metaclass__ = ScenarioMeta
    class test_serialize(ScenarioTest):
        scenarios = BASE58_CODEC
        def __test__(self, data, result):
            self.assertEqual(data.encode('base58'), result)
    class test_deserialize(ScenarioTest):
        scenarios = BASE58_CODEC
        def __test__(self, data, result):
            self.assertEqual(result.decode('base58'), data)

#
# End of File
#
