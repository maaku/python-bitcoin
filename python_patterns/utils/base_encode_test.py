#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.utils.base_encode_test ------------------------------===
# Copyright © 2011, RokuSigma Inc. (Mark Friedenbach <mark@roku-sigma.com>)
# as an unpublished work.
#
# RokuSigma Inc. (the “Company”) Confidential
#
# NOTICE: All information contained herein is, and remains the property of the
# Company. The intellectual and technical concepts contained herein are
# proprietary to the Company and may be covered by U.S. and Foreign Patents,
# patents in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from the
# Company. Access to the source code contained herein is hereby forbidden to
# anyone except current Company employees, managers or contractors who have
# executed Confidentiality and Non-disclosure agreements explicitly covering
# such access.
#
# The copyright notice above does not evidence any actual or intended
# publication or disclosure of this source code, which includes information
# that is confidential and/or proprietary, and is a trade secret, of the
# Company. ANY REPRODUCTION, MODIFICATION, DISTRIBUTION, PUBLIC PERFORMANCE,
# OR PUBLIC DISPLAY OF OR THROUGH USE OF THIS SOURCE CODE WITHOUT THE EXPRESS
# WRITTEN CONSENT OF THE COMPANY IS STRICTLY PROHIBITED, AND IN VIOLATION OF
# APPLICABLE LAWS AND INTERNATIONAL TREATIES. THE RECEIPT OR POSSESSION OF
# THIS SOURCE CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR IMPLY ANY
# RIGHTS TO REPRODUCE, DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE,
# USE, OR SELL ANYTHING THAT IT MAY DESCRIBE, IN WHOLE OR IN PART.
# ===----------------------------------------------------------------------===

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

# Python patterns, base encoding
from python_patterns.utils.base_encode import base_encode, base_decode

SCENARIOS = [
  dict(num=0, string='a'),
  dict(num=1, string='b'),
  dict(num=2, string='c'),
  dict(num=53, string='8'),
  dict(num=54, string='9'),
  dict(num=55, string='ba'),
  dict(num=56, string='bb'),
  dict(num=96**34, string='vvWPtAEc2P6nm6vrE9VAdeYabJH3KGPkSbW55PD'),
  dict(base="123", num=0, string='1'),
  dict(base="123", num=1, string='2'),
  dict(base="123", num=2, string='3'),
  dict(base="123", num=3, string='21'),
  dict(base="123", num=4, string='22'),
  dict(base=u"éü", num=0, string=u'é'),
  dict(base=u"éü", num=1, string=u'ü'),
  dict(base=u"éü", num=2, string=u'üé'),
  dict(num=100, string='bY', little_endian=False),
  dict(num=100, string='Yb', little_endian=True),
]

class TestBaseEncode(unittest2.TestCase):
  """Test encoding and decoding using a variety of standard scenarios."""
  __metaclass__ = ScenarioMeta
  class test_encode(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, num, string, base=None, little_endian=False):
      self.assertEqual(base_encode(num, base=base, little_endian=little_endian), string)
  class test_decode(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, num, string, base=None, little_endian=False):
      self.assertEqual(num, base_decode(string, base=base, little_endian=little_endian))

class TestNegativeNumberEncode(unittest2.TestCase):
  """Test that encoding a negative number results in a value error."""
  def test_negative_number(self):
    self.assertRaises(ValueError, base_encode, (-1))

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
