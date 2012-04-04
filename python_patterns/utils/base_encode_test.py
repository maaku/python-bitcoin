#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.utils.base_encode_test ------------------------------===
# Copyright © 2011-2012, RokuSigma Inc. and contributors. See AUTHORS for more
# details.
#
# Some rights reserved.
#
# Redistribution and use in source and binary forms of the software as well as
# documentation, with or without modification, are permitted provided that the
# following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * The names of the copyright holders or contributors may not be used to
#    endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND
# DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
