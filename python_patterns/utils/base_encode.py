#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.utils.base_encode -----------------------------------===
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
    for i, c in enumerate(reversed(string)):
      ret += (length ** i) * reverse_base[c]
  return ret

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
