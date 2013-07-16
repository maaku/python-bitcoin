# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

__all__ = [
    'compress_amount',
    'decompress_amount',
]

# ===----------------------------------------------------------------------===

def compress_amount(n):
    """Compress 64-bit integer values, preferring a smaller size for whole
    numbers (base-10), so as to achieve run-length encoding gains on real-world
    data. The basic algorithm:
        * if the amount is 0, return 0
        * divide the amount (in base units) by the largest power of 10
          possible; call the exponent e (e is max 9)
        * if e<9, the last digit of the resulting number cannot be 0; store it
          as d, and drop it (divide by 10); regardless, call the result n
        * output 1 + 10*(9*n + d - 1) + e
        * if e==9, we only know the resulting number is not zero, so output
          1 + 10*(n - 1) + 9
    (this is decodable, as d is in [1-9] and e is in [0-9])"""
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
    """Undo the value compression performed by x=compress_amount(n). The input
    x matches one of the following patterns:
        x = 0
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

#
# End of File
#
