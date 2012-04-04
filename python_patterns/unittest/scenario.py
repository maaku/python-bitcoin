#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.unittest.scenario -----------------------------------===
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
##

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
