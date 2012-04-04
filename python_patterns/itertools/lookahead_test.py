#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.itertools.lookahead_test ----------------------------===
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

"""Provides unittest cases for the `lookahead()` generator."""

# Python standard library, unit-testing
from unittest2 import TestCase

# Python patterns, lookahead generator
from python_patterns.itertools import lookahead

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

SCENARIOS = [
  # Test string iterables...
  dict(iterable='',         tuples=[]),
  dict(iterable='a',        tuples=[('a',None)]),
  dict(iterable='ab',       tuples=[('a','b'),('b',None)]),
  dict(iterable='abc',      tuples=[('a','b'),('b','c'),('c',None)]),
  # Test array iterables...
  dict(iterable=[],         tuples=[]),
  dict(iterable=[1],        tuples=[(1,None)]),
  dict(iterable=[1,2],      tuples=[(1,2),(2,None)]),
  dict(iterable=[1,2,3],    tuples=[(1,2),(2,3),(3,None)]),
  # Test tuple iterables...
  dict(iterable=(),         tuples=[]),
  dict(iterable=(1,),       tuples=[(1,None)]),
  dict(iterable=(1,'a'),    tuples=[(1,'a'),('a',None)]),
  dict(iterable=(1,'a',{}), tuples=[(1,'a'),('a',{}),({},None)]),
  # Test list of None values (edge case)...
  dict(iterable=[None]*3,   tuples=[(None,None),(None,None),(None,None)]),
  # Test single parameter form (lookahead)...
  dict(iterable=[1,2,3], args=(0,), tuples=[(1,),(2,),(3,)]),
  dict(iterable=[1,2,3], args=(1,), tuples=[(1,2),(2,3),(3,None)]),
  dict(iterable=[1,2,3], args=(2,), tuples=[(1,2,3),(2,3,None),(3,None,None)]),
  dict(iterable=[1,2,3], args=(3,), tuples=[(1,2,3,None),(2,3,None,None),(3,None,None,None)]),
  # Test twin parameter form (lookbehind, lookahead)...
  dict(iterable=[1,2,3], args=(0,0), tuples=[(1,),(2,),(3,)]),
  dict(iterable=[1,2,3], args=(0,1), tuples=[(1,2),(2,3),(3,None)]),
  dict(iterable=[1,2,3], args=(0,2), tuples=[(1,2,3),(2,3,None),(3,None,None)]),
  dict(iterable=[1,2,3], args=(0,3), tuples=[(1,2,3,None),(2,3,None,None),(3,None,None,None)]),
  dict(iterable=[1,2,3], args=(1,0), tuples=[(None,1,),(1,2,),(2,3,)]),
  dict(iterable=[1,2,3], args=(1,1), tuples=[(None,1,2),(1,2,3),(2,3,None)]),
  dict(iterable=[1,2,3], args=(1,2), tuples=[(None,1,2,3),(1,2,3,None),(2,3,None,None)]),
  dict(iterable=[1,2,3], args=(1,3), tuples=[(None,1,2,3,None),(1,2,3,None,None),(2,3,None,None,None)]),
  dict(iterable=[1,2,3], args=(2,0), tuples=[(None,None,1,),(None,1,2,),(1,2,3,)]),
  dict(iterable=[1,2,3], args=(2,1), tuples=[(None,None,1,2),(None,1,2,3),(1,2,3,None)]),
  dict(iterable=[1,2,3], args=(2,2), tuples=[(None,None,1,2,3),(None,1,2,3,None),(1,2,3,None,None)]),
  dict(iterable=[1,2,3], args=(2,3), tuples=[(None,None,1,2,3,None),(None,1,2,3,None,None),(1,2,3,None,None,None)]),
  dict(iterable=[1,2,3], args=(3,0), tuples=[(None,None,None,1,),(None,None,1,2,),(None,1,2,3,)]),
  dict(iterable=[1,2,3], args=(3,1), tuples=[(None,None,None,1,2),(None,None,1,2,3),(None,1,2,3,None)]),
  dict(iterable=[1,2,3], args=(3,2), tuples=[(None,None,None,1,2,3),(None,None,1,2,3,None),(None,1,2,3,None,None)]),
  dict(iterable=[1,2,3], args=(3,3), tuples=[(None,None,None,1,2,3,None),(None,None,1,2,3,None,None),(None,1,2,3,None,None,None)]),
]

class TestBaseEncode(TestCase):
  """Test the behavior of `lookahead()` from within a variety of illustrative
  scenarios."""
  __metaclass__ = ScenarioMeta
  class test_lookahead(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, iterable, tuples, args=(), kwargs={}):
      self.assertEqual(list(lookahead(iterable, *args, **kwargs)), tuples)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
