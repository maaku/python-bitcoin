#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.utils.decorators ------------------------------------===
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

def Property(func):
  """
  Standard @Property idiom.  It allows properties to be set in a more
  idiomatic but easier to read fashion, as demonstrated here:

  class SomeClass(object):
    @Property
    def property_name():
      doc = "docstring"
      def fget(self):
        return self.field
      def fset(self, value):
        self.field = value
      def fdel(self):
        del self.field
      return locals()

  Don't forget the 'return locals()' at the end!  For more information, refer
  to the following blog post:

  <http://adam.gomaa.us/blog/2008/aug/11/the-python-property-builtin/>

  NOTE: “Property” has a capital P because “property” is already a Python
        built-in (which capital-P Property is a wrapper around). Although it
        breaks convention to have a capitalized decorator, it would be even
        worse to call it something else.
  """
  return property(**func())

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
