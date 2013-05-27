# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

try:
    from gmpy2 import mpz, mpq
except ImportError:
    mpz = long
    from fractions import Fraction as mpq

try:
    from cdecimal import Decimal as mpd, Context as mpd_context
except ImportError:
    from decimal import Decimal as mpd, Context as mpd_context

from bigfloat import BigFloat as mpf, Context as mpf_context

# ===----------------------------------------------------------------------===

from bigfloat import ROUND_TIES_TO_EVEN
from bigfloat import ROUND_TOWARD_ZERO
from bigfloat import ROUND_AWAY_FROM_ZERO
from bigfloat import ROUND_TOWARD_POSITIVE
from bigfloat import ROUND_TOWARD_NEGATIVE

# ===----------------------------------------------------------------------===

def round_absolute(value, mode=ROUND_TIES_TO_EVEN, magnitude=0, base=10):
    raise NotImplementedError

def round_relative(value, mode=ROUND_TIES_TO_EVEN, precision=0, base=10):
    raise NotImplementedError

# ===----------------------------------------------------------------------===

def mpq_from_mpf(value):
    if hasattr(value, 'as_integer_ratio'):
        return mpq(*value.as_integer_ratio())
    raise NotImplementedError

def mpq_from_mpd(value):
    raise NotImplementedError

def mpf_from_mpz(value):
    return mpf(int(value))

#
# End of File
#
