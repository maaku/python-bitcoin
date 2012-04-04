#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.itertools.lookahead ---------------------------------===
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

"""Provides `lookahead()`, a convenient utility for looping through an
iterable container with a fixed number of look-ahead and/or “look-behind”
values."""

def lookahead(iterable, *args, **kwargs):
  """Constructs a generator over the iterable yielding look-ahead (and/or
  “look-behind”) tuples. One tuple will be generated for each element value
  accessible from the iterator, containing that element and the number of
  elements specified just prior to and immediately after. When no such element
  exists, the `None` is used instead.
  
  If one were to think of `iterator` as a list, this is would be similar to
  appending `[None]*lookahead` and prepending `[None]*lookbehind`, then
  iterating over and returning a sliding window of length `lookbehind+1+
  lookahead` (except of course that instead of generating the such a list,
  this implementation generates (and caches) lookahead values only as needed).

  `lookahead()` may be called with 1, 2, or 3 parameters:

    lookahead(iterable)
      Defaults to lookahead=1, lookbehind=0
    lookahead(iterable, lookahead)
      Defaults to lookbehind=0
    lookahead(iterable, lookbehind, lookahead)
      Notice that lookahead is now the 3rd parameter!

  Example semantics:

    lookahead(iterable):       yield (item, next)
    lookahead(iterable, 2):    yield (item, next, next+1)
    lookahead(iterable, 1, 2): yield (prev, item, next, next+1)
    lookahead(iterable, p, n):
      yeild (prev, ..., prev+p-1, item, next, ..., next+n-1)
  """
  # Deal with our funny parameter handling (2 optional positional parameters,
  # with the *2nd* optional parameter taking precendence if only one is
  # specified):
  if len(args) == 0:
    num_prev, num_next = 0, 1
  elif len(args) == 1:
    num_prev, num_next = 0, args[0]
  elif len(args) == 2:
    num_prev, num_next = args[0], args[1]
  else:
    raise TypeError, "%s() takes 1, 2, or 3 arguments (%d given)" % \
      (lookahead.__name__, len(args))

  # Construct an iterator over iterable
  iterator = iter(iterable)

  # Set the lookbehind positions to `None` and generate the first element.
  # This will immediately raise StopIteration in the trivial case:
  lst = [None]*num_prev + [iterator.next()]

  # Prime the needed lookahead values:
  for x in xrange(num_next):
    try:
      lst.append(iterator.next())
    except StopIteration:
      lst.append(None)
      num_next -= 1

  # Yield the current tuple, then shift the list and generate a new item:
  for item in iterator:
    yield tuple(lst)
    lst = lst[1:] + [item]

  # Yield the last full tuple, then continue with `None` for each lookahead
  # position:
  for x in xrange(num_next+1):
    yield tuple(lst)
    lst = lst[1:] + [None]

  # Done!
  raise StopIteration

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
