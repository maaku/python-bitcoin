#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === bitcoin.utils_test --------------------------------------------------===
# Copyright © 2012, RokuSigma Inc. and contributors as an unpublished work.
# See AUTHORS for details.
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

# ===----------------------------------------------------------------------===
# This file is based in part on code published as part of the pynode project.
# The original work is copyrighted by it's authors and licensed according to
# the terms of the MIT license (below); modifications since then are the
# property of RokuSigma Inc. and subject to the above-referenced
# confidentiality and non-disclosure agreements.
# ===----------------------------------------------------------------------===

# ===----------------------------------------------------------------------===
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ===----------------------------------------------------------------------===

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

from .utils import uint256_from_compact

UINT256_FROM_COMPACT = [
    dict(bits=0x1d00ffff,
         target=0x00000000FFFF0000000000000000000000000000000000000000000000000000L),
    dict(bits=0x1b0404cb,
         target=0x00000000000404CB000000000000000000000000000000000000000000000000L),
]

class TestMerkleList(unittest2.TestCase):
    "Test uint256_from_compact API under a variety of scenarios."
    __metaclass__ = ScenarioMeta
    class test_uint256_from_compact(ScenarioTest):
        scenarios = UINT256_FROM_COMPACT
        def __test__(self, bits, target):
            self.assertEqual(uint256_from_compact(bits), target)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
