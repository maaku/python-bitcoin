# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

try:
    from gmpy2 import mpz, mpq
except ImportError:
    mpz = long
    from fractions import Fraction as mpq

try:
    from cdecimal import Decimal as mpd, Context as mpd_context
except ImportError:
    from decimal import Decimal as mpd, Context as mpd_context

from gmpy2 import mpfr as mpf, context as mpf_context

# ===----------------------------------------------------------------------===

from gmpy2 import RoundToNearest as RoundNearest
from gmpy2 import RoundToZero    as RoundTowardZero
from gmpy2 import RoundAwayZero  as RoundAwayFromZero
from gmpy2 import RoundUp        as RoundTowardPositive
from gmpy2 import RoundDown      as RoundTowardNegative

# ===----------------------------------------------------------------------===

def round_absolute(value, mode=RoundNearest, magnitude=0, base=10):
    raise NotImplementedError

def round_relative(value, mode=RoundNearest, precision=0, base=10):
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

# End of File
