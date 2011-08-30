#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.unittest.scenario_test ------------------------------===
# Copyright © 2011, RokuSigma Inc. (Mark Friedenbach <mark@roku-sigma.com>)
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
