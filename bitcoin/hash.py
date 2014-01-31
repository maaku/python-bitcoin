# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

__all__ = (
    'hash160',
    'hash256',
)

import hashlib

from copy import deepcopy
from .serialize import LittleInteger
from .tools import StringIO, tuple

class _HashAlgorithm(object):
    def intdigest(self):
        "Returns the accumulated input interpreted as a little-endian integer."
        return LittleInteger.deserialize(StringIO(self.digest()), self.digest_size)

class _NopHashAlgorithm(_HashAlgorithm):
    """This class implements the special case of `_ChainedHashAlgorithm([])`,
    the “no-op/pass-through algorithm”. It is nothing more than a simple
    regurgitation of the input under the guise of a hashlib digest (what is
    passed into `update()` is `''.join()`'d together to form the digest)."""
    def __init__(self, string=None, *args, **kwargs):
        """Takes one optional parameter, `string`, providing the initial input
        as a convenient shorthand."""
        if string is None:
            string = ''
        super(_NopHashAlgorithm, self).__init__(*args, **kwargs)
        self._input = string

    def copy(self):
        "Return a clone of this no-op hash object."
        return deepcopy(self)

    def digest(self):
        "Returns the accumulated input as a byte array."
        return self._input

    def hexdigest(self):
        """Returns the accumulated input as a human-readable text string of
        hexadecimal digits."""
        return unicode(self._input.encode('hex'))

    def update(self, *args):
        "Appends any passed in byte arrays to the “digest”."
        self._input += b''.join(args)

    @property
    def block_size(self):
        """`block_size` doesn't really have any meaning for the no-op/pass-
        through hash algorithm. Specifying `1` is effectively saying as
        much."""
        return 1

    @property
    def digest_size(self):
        """In a pass-through hash, the “digest size” is necessarily variable
        and not known until the input is finalized. Returning the current size
        of the input (which will become [a prefix of] the digest) is the best
        that we can do."""
        return len(self._input)

    @property
    def name(self):
        """The defined canonical name of the the no-op/pass-through hash
        algorithm is the empty string `str('')`."""
        return ''

class _ChainedHashAlgorithm(_HashAlgorithm):
    """Implements a series of chained hash algorithms masquerading as single
    hashlib object. As input is added it is hashed with the first hash
    function, then when a digest is requested the subsequent algorithms are
    applied."""
    __slots__ = ('_algorithms', '_hobj', '_fobj')

    def __init__(self, algorithms, string=None, *args, **kwargs):
        """Takes one optional parameter, `string`, providing the initial input
        as a convenient shorthand."""
        if string is None: string = ''
        super(_ChainedHashAlgorithm, self).__init__(*args, **kwargs)
        self._algorithms = algorithms
        self._hobj = hashlib.new(algorithms[0], string)
        self._fobj = None

    def copy(self):
        "Return a clone of this hash object."
        other = _ChainedHashAlgorithm(self._algorithms)
        other._hobj = deepcopy(self._hobj)
        other._fobj = deepcopy(self._fobj)
        return other

    def _finalize(self):
        "Computes _fobj, the completed hash."
        hobj = self._hobj
        for hashname in self._algorithms[1:]:
            fobj = hashlib.new(hashname)
            fobj.update(hobj.digest())
            hobj = fobj
        self._fobj = hobj

    def digest(self):
        "Returns the hash of accumulated input as a byte array."
        if self._fobj is None:
            self._finalize()
        return self._fobj.digest()

    def hexdigest(self):
        """Returns the hash of accumulated input as a human-readable text
        string of hexadecimal digits."""
        if self._fobj is None:
            self._finalize()
        return self._fobj.hexdigest()

    def update(self, *args):
        "Appends any passed in byte arrays to the digest object."
        for string in args:
            self._hobj.update(string)
        self._fobj = None

    @property
    def block_size(self):
        """Returns the block size (in bytes) of the hash algorithm. Computational
        cost and memory requirements are predictable if data is given to the hash
        object in unit increments of the block size."""
        return self._hobj.block_size

    @property
    def digest_size(self):
        "Returns the size (in bytes) of the resulting digest."
        if getattr(self, '_fobj', None) is not None:
            return self._fobj.digest_size
        else:
            return hashlib.new(self._algorithms[-1]).digest_size

    @property
    def name(self):
        return self._algorithms

class _HashAlgorithmInterface(tuple):
    """Provides a class API similar to `HASH` objects from `hashlib` (e.g.,
    `hashlib.sha256()`)."""
    def new(self, string=None, *args, **kwargs):
        """Returns a `_ChainedHashAlgorithm` if the underlying tuple
        (specifying the list of algorithms) is not empty, otherwise a
        `_NopHashAlgorithm` instance is returned."""
        if len(self):
            hobj = _ChainedHashAlgorithm(self, *args, **kwargs)
        else:
            hobj = _NopHashAlgorithm(*args, **kwargs)
        if string is not None:
            hobj.update(string)
        return hobj
    __call__=new

    @property
    def digest_size(self):
        "Returns the size (in bytes) of the resulting digest."
        return self.new().digest_size

    @property
    def block_size(self):
        """Returns the block size (in bytes) of the hash algorithm.
        Computational cost and memory requirements are predictable if data is
        given to the hash object in unit increments of the block size."""
        return self.new().block_size

    @property
    def name(self):
        "The defined canonical name of the the hash algorithm."
        return ':'.join(map(lambda n:n.encode('utf-8'), self))

    def serialize(self, hash_):
        return LittleInteger(hash_).serialize(self.digest_size)
    def deserialize(self, file_):
        return LittleInteger.deserialize(file_, self.digest_size)

# (sha256 . ripemd160) is used for Bitcoin addresses, as the 20-byte ripemd160
# hash can save significant space.
hash160 = _HashAlgorithmInterface(('sha256', 'ripemd160'))

# (sha256 . sha256), “double-SHA256” is used as the proof-of-work function,
# the Merkle-tree compressor, and to generate transaction hash values for
# identification.
hash256 = _HashAlgorithmInterface(('sha256', 'sha256'))
