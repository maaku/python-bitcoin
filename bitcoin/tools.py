# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
"Miscellaneous types and utility codes used in other parts of python-bitcoin."

# ===----------------------------------------------------------------------===

# This would be cStringIO onn Python 2.7, if we re-enable support for
# python2.
from io import BytesIO

# ===----------------------------------------------------------------------===

# Conditionally remove the following if we re-enable support for
# python2.
long = int

# ===----------------------------------------------------------------------===

# blist provides a list-like type with better asymptotic performance and
# similar performance on small lists
try:
    from blist import blist as list, btuple as tuple
except:
    from sys import modules
    mod_dict = modules[__name__].__dict__
    mod_dict['list'] = list
    mod_dict['tuple'] = tuple
    del modules, mod_dict

# ===----------------------------------------------------------------------===

def compress_amount(n):
    """\
    Compress 64-bit integer values, preferring a smaller size for whole
    numbers (base-10), so as to achieve run-length encoding gains on real-
    world data. The basic algorithm:
        * If the amount is 0, return 0
        * Divide the amount (in base units) evenly by the largest power of 10
          possible; call the exponent e (e is max 9)
        * If e<9, the last digit of the resulting number cannot be 0; store it
          as d, and drop it (divide by 10); regardless, call the result n
        * Output 1 + 10*(9*n + d - 1) + e
        * If e==9, we only know the resulting number is not zero, so output
          1 + 10*(n - 1) + 9.
    (This is decodable, as d is in [1-9] and e is in [0-9].)"""
    if not n: return 0
    e = 0
    while (n % 10) == 0 and e < 9:
        n = n // 10
        e = e + 1
    if e < 9:
        n, d = divmod(n, 10);
        return 1 + (n*9 + d - 1)*10 + e
    else:
        return 1 + (n - 1)*10 + 9

def decompress_amount(x):
    """\
    Undo the value compression performed by x=compress_amount(n). The input
    x matches one of the following patterns:
        x = n = 0
        x = 1+10*(9*n + d - 1) + e
        x = 1+10*(n - 1) + 9"""
    if not x: return 0;
    x = x - 1;

    # x = 10*(9*n + d - 1) + e
    x, e = divmod(x, 10);
    n = 0;
    if e < 9:
        # x = 9*n + d - 1
        x, d = divmod(x, 9)
        d = d + 1
        # x = n
        n = x*10 + d
    else:
        n = x + 1
    return n * 10**e

# ===----------------------------------------------------------------------===

from .serialize import BigInteger as _BigInteger
def compact_from_target(target):
    """\
    The “compact” format is a representation of a whole number N using an
    unsigned 32bit number similar to a floating point format. Conversion
    necessarily involves truncation if the target is greater than 2^23-1.

    The most significant 8 bits are the unsigned exponent of base 256.
    This exponent can be thought of as "number of bytes of N".
    The lower 23 bits are the mantissa.
    Bit number 24 (0x800000) represents the sign of N.
    N = (-1^sign) * mantissa * 256^(exponent-3)

    Satoshi's original implementation used BN_bn2mpi() and BN_mpi2bn().
    MPI uses the most significant bit of the first byte as sign.
    Thus 0x1234560000 is compact (0x05123456)
    and  0xc0de000000 is compact (0x0600c0de)
    (0x05c0de00) would be -0x40de000000

    Bitcoin only uses this “compact” format for encoding difficulty
    targets in the block header, which are unsigned 256bit quantities.
    Thus, all the complexities of the sign bit and using base 256 are
    probably an implementation accident.

    This implementation directly uses shifts instead of going
    through an intermediate MPI representation."""
    bn = _BigInteger(target).serialize()
    size = len(bn)
    if size <= 3:
        word = target << 8 * (3 - size)
    else:
        word = target >> 8 * (size - 3)
    if word & 0x00800000:
        word >>= 8
        size += 1
    word |= size << 24
    if target < 0:
        word |= 0x00800000
    return word

def target_from_compact(bits):
    """\
    Extract a full target from its compact representation, undoing the
    transformation x=compact_from_target(t). See compact_from_target() for
    more information on this 32-bit floating point format."""
    size = bits >> 24
    word = bits & 0x007fffff
    if size < 3:
        word >>= 8 * (3 - size)
    else:
        word <<= 8 * (size - 3)
    if bits & 0x00800000:
        word = -word
    return word

# ===----------------------------------------------------------------------===

def cmp(a, b):
    "Returs -1 if a<b, 0 if a==b, and 1 if a>b.  Removed in python3."
    return (a>b)-(a<b)

def icmp(a, b):
    "Like cmp(), but for any iterator."
    for xa in a:
        try:
            xb = next(b)
            d = cmp(xa, xb)
            if d: return d
        except StopIteration:
            return 1
    try:
        next(b)
        return -1
    except StopIteration:
        return 0

# ===----------------------------------------------------------------------===

# Provides a utility for constructing generators out of an iterable that yield
# look-ahead (and/or “look-behind”) tuples.
from lookahead import lookahead

# ===----------------------------------------------------------------------===

# Simple construction, analysis and modification of binary data.
# Modified to use icmp for relational operators, to support various use cases
# within python-bitcoin.
import bitstring
bitstring.Bits.__lt__ = lambda self, other: icmp(iter(self), iter(other)) <  0
bitstring.Bits.__le__ = lambda self, other: icmp(iter(self), iter(other)) <= 0
bitstring.Bits.__ge__ = lambda self, other: icmp(iter(self), iter(other)) >= 0
bitstring.Bits.__gt__ = lambda self, other: icmp(iter(self), iter(other)) >  0
from bitstring import Bits
del bitstring

# ===----------------------------------------------------------------------===

def SteppedGeometric(initial, interval):
    def _func(height):
        return mpq(initial, 2**(height//interval));
    return _func

def LinearArithmetic(initial, cutoff):
    def _func(height):
        if height < cutoff:
            return mpq(initial * (cutoff-height), cutoff);
        return 0
    return _func

def SquareCutoff(initial, cutoff):
    def _func(height):
        if height < cutoff:
            return initial
        return 0
    return _func

def Constant(initial):
    def _func(height):
        return initial
    return _func

# End of File
