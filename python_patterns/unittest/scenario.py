#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.unittest.scenario -----------------------------------===
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

##
# This testing helper-class was taken from a gist written by github user
# ‘bigjason’. It combines a prototypical test case with a list of dictionaries
# (each a dict of keyword arguments) and transforms the two into a series of
# unittest-compatible test cases. The advantage of this approach is that an
# identical test can be applied to multiple scenarios with minimal repetition
# of code, while still having each scenario tested independently and reported
# to the user by the test runner.
#
# Example of useage can be found in the file scenario_test.py, or on
# bigjason's blog post which introduced the concept:
#
#   <http://www.bigjason.com/blog/scenario-testing-python-unittest/>
#
# The original code this was based off of can be found on GitHub:
#
#   <https://gist.github.com/856821/8966346d8e50866eae928ababa86acea6504bcee>
#
# FIXME: The copyright/license status of this code is not clear. I've asked
#        bigjason to clarify the situation by adding a copyright header to the
#        gist. The copyright header of this file (and scenario_test.py) will
#        have to be updated when that information is available. If he fails to
#        do so, this code will have to be removed and cleanroom re-written
#        from scratch.

class ScenarioMeta(type):
  def __new__(cls, name, bases, attrs):
    new_attrs = {}

    for name, val in filter(lambda n: isinstance(n[1], ScenarioTestMeta), attrs.iteritems()):
      for id, params in enumerate(val.scenarios if not callable(val.scenarios) else val.scenarios()):
        if type(params) in (tuple, list):
            params, id = params
        # create a unittest discoverable name
        test_name = "test_%s_%s" % (val.__name__, id)
        # Wrap the scenario in a closure and assign the discoverable name.
        new_attrs[test_name] = cls._wrap_test(params, val.__test__)
    attrs.update(new_attrs)
    return super(ScenarioMeta, cls).__new__(cls, name, bases, attrs)

  @staticmethod
  def _wrap_test(kwargs, meth):
    def wrapper(self):
      meth(self, **kwargs)
    return wrapper

class ScenarioTestMeta(type):
  def __new__(cls, name, bases, attrs):
    test_meth = attrs.pop("__test__", None)
    if test_meth:
      # Now that the __test__ method is pulled off the base it can be wrapped
      # as static and rebound. This allows it to be re-composed to the parent
      # test case.
      attrs["__test__"] = staticmethod(test_meth)

    return super(ScenarioTestMeta, cls).__new__(cls, name, bases, attrs)

class ScenarioTest(object):
  __metaclass__ = ScenarioTestMeta
  scenarios = ()

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
