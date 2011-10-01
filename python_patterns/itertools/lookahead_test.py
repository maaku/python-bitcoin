#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.itertools.lookahead_test ----------------------------===
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
