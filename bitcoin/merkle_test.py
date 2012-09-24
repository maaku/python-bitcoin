#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === bitcoin.merkle_test -------------------------------------------------===
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

from .merkle import merkle_list

MERKLE_LIST = [
    dict(list_=[], merkle=0),
    dict(list_=[0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33bL],
         merkle=0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33bL),
    dict(list_=[0x50671f9e3b0719fcd23b2976eedf6e0a6f19ae7a8f023c3e66b9b1fbe207a006L,
                0x603b9dbb388987175f8ddbdae9a8ad77a999e63b356e6172b331905387b515f7L,
                0xec258956c3069ea974a569fbacd320fd183d65fa6d4c318ad4e55da6260c0f3dL],
         merkle=0x5d438b61fa23d20bfac0a6eaf5c426e2abdd48637c7dd70a620b0b7ab7cd6092L),
    dict(list_=[0x9156235baa55ea841c4384faa543004fd5a56661d22dfbc2bbd5313c85044e08L,
                0xc6f50393c676f1f3b669c93f62c3f0e46349f6d2aff13ed8976bd649382ff6fcL,
                0x4817fad15ce7604ae5a478888a29b4ade8000596a0e9267747b1d4f0bd1a6defL,
                0x16952eba67618e90857d530a63477ea09dd89575ac00c114e20e8068b4e0297cL],
         merkle=0xb1cd750f2a242deeaf3b452aa69a4a46f9f66e866c07eda22677f1287688bb1eL),
]

class TestMerkleList(unittest2.TestCase):
    "Test merkle_list API under a variety of scenarios."
    __metaclass__ = ScenarioMeta
    class test_merkle_root(ScenarioTest):
        scenarios = MERKLE_LIST
        def __test__(self, list_, merkle):
            self.assertEqual(merkle_list(list_), merkle)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
