#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === python_patterns.itertools.lookahead ---------------------------------===
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
