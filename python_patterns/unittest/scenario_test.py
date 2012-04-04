#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.unittest.scenario_test ------------------------------===
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

# NOTE: See notice about the origin and copyright status of this code in
#       scenario.py.
#
# FIXME: Remove above note about copyright and replace with appropriate
#        copyright declaration when that information is received.

import unittest2

import python_patterns.unittest.scenario

## Unit of code to test ##

def is_numeric(value_in):
  try:
    float(value_in)
    return True
  except Exception:
    return False

## Test Case ##

class TestIsNumeric(unittest2.TestCase):
  __metaclass__ = python_patterns.unittest.scenario.ScenarioMeta

  class is_numeric_basic(python_patterns.unittest.scenario.ScenarioTest):
    scenarios = [
      dict(val="1", expected=True),
      dict(val="-1", expected=True),
      dict(val=unicode("123" * 3), expected=True),
      dict(val="Bad String", expected=False),
      dict(val="Speaks Volumes", expected=False)
    ]
    scenarios += [(dict(val=unicode(x), expected=True),
                  "check_unicode_%s" % x) for x in range(-2, 3)]

    def __test__(self, val, expected):
      actual = is_numeric(val)
      if expected:
        self.assertTrue(actual)
      else:
        self.assertFalse(actual)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
