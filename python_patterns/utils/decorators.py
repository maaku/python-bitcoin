#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.utils.decorators ------------------------------------===
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

def Property(func):
  """
  Standard @Property idiom. It allows properties to be set in a more idiomatic
  but easier to read fashion, as demonstrated here:

  class SomeClass(object):
    @Property
    def property_name():
      '''docstring'''
      def fget(self):
        return self.field
      def fset(self, value):
        self.field = value
      def fdel(self):
        del self.field
      return locals()

  Don't forget the 'return locals()' at the end! For more information, refer
  to the following two blog posts:

  <http://adam.gomaa.us/blog/2008/aug/11/the-python-property-builtin/>

  <http://kbyanc.blogspot.com/2007/06/python-property-attribute-tricks.html>

  NOTE: “Property” has a capital P because “property” is already a Python
        built-in (which capital-P @Property is a wrapper around). Although it
        breaks convention to have a capitalized decorator, it would be even
        worse to call it something else.
  """
  return property(doc=func.__doc__, **func())

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
