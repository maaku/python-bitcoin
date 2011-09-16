#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.utils.base_encode -----------------------------------===
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

ALPHABET_LIST = u"abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ALPHABET_DICT = dict((c, i) for i, c in enumerate(ALPHABET_LIST))
ALPHABET_LENGTH = len(ALPHABET_LIST)

def base_encode(num, base=None, little_endian=False):
  """Encodes the passed-in number into a textual representation using the
  passed-in alphabet, or a default alphabet of 55 easily distinguishable
  characters.

    num
      The number to encode.

    base
      A string containing the list of base characters to be used, in order
      (default: "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789").

    little_endian
      Boolean value specifying whether the output should be little-endian or
      big-endian (default: False).
  """
  if num < 0:
    raise ValueError, "cannot base encode negative number: %d" % num
  if base is None:
    base   = ALPHABET_LIST
    length = ALPHABET_LENGTH
  else:
    base   = unicode(base)
    length = len(base)
  ret = ''
  if num == 0:
    return base[0]
  while num != 0:
    if little_endian:
      ret = ret + base[num % length]
    else:
      ret = base[num % length] + ret
    num /= length
  return ret

def base_decode(string, base=None, little_endian=False):
  """Decodes the passed-in string (presumably created with base_encode) from a
  textual representation to a number.

    string
      The encoded number.

    base
      A string containing the list of base characters to be used, in order
      (default: "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789").

    little_endian
      Boolean value specifying whether the output should be little-endian or
      big-endian (default: False).
  """
  if base is None:
    reverse_base = ALPHABET_DICT
    length       = ALPHABET_LENGTH
  else:
    reverse_base = dict((c, i) for i, c in enumerate(unicode(base)))
    length       = len(base)
  ret = 0
  if little_endian:
    for i, c in enumerate(string):
      ret += (length ** i) * reverse_base[c]
  else:
    for i, c in enumerate(string[::-1]):
      ret += (length ** i) * reverse_base[c]
  return ret

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
