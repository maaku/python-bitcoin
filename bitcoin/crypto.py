# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import hashlib
from itertools import count, izip
import numbers

from python_patterns.utils.decorators import Property

from .serialize import serialize_hash, deserialize_hash
from .tools import StringIO

__all__ = [
    'hash256',
    'hash160',
    'merkle',
    'SECP256k1',
    'Secret',
    'InvalidSecretError',
    'Signature',
    'CompactSignature',
    'SigningKey',
    'VerifyingKey'
]

# ===----------------------------------------------------------------------===

from copy import deepcopy

class _HashAlgorithm(object):
    def intdigest(self):
        "Returns the accumulated input interpreted as a little-endian integer."
        return deserialize_hash(StringIO(self.digest()), self.digest_size)

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
        self._input = ''.join([self._input]+map(str,list(args)))

    @Property
    def block_size():
        """`block_size` doesn't really have any meaning for the no-op/pass-
        through hash algorithm. Specifying `1` is effectively saying as
        much."""
        def fget(self):
            return 1
        return locals()

    @Property
    def digest_size():
        """In a pass-through hash, the “digest size” is necessarily variable
        and not known until the input is finalized. Returning the current size
        of the input (which will become [a prefix of] the digest) is the best
        that we can do."""
        def fget(self):
            return len(self._input)
        return locals()

    @Property
    def name():
        """The defined canonical name of the the no-op/pass-through hash
        algorithm is the empty string `str('')`."""
        def fget(self):
            return ''
        return locals()

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

    @Property
    def block_size():
        """Returns the block size (in bytes) of the hash algorithm. Computational
        cost and memory requirements are predictable if data is given to the hash
        object in unit increments of the block size."""
        def fget(self):
            return self._hobj.block_size
        return locals()

    @Property
    def digest_size():
        "Returns the size (in bytes) of the resulting digest."
        def fget(self):
            if getattr(self, '_fobj', None) is not None:
                return self._fobj.digest_size
            else:
                return hashlib.new(self._algorithms[-1]).digest_size
        return locals()

    @Property
    def name():
        def fget(self):
            return self._algorithms
        return locals()

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

    @Property
    def digest_size():
        "Returns the size (in bytes) of the resulting digest."
        def fget(self):
            return self.new().digest_size
        return locals()

    @Property
    def block_size():
        """Returns the block size (in bytes) of the hash algorithm.
        Computational cost and memory requirements are predictable if data is
        given to the hash object in unit increments of the block size."""
        def fget(self):
            return self.new().block_size
        return locals()

    @Property
    def name():
        "The defined canonical name of the the hash algorithm."
        def fget(self):
            return ':'.join(map(lambda n:n.encode('utf-8'), self))
        return locals()

# (sha256 . ripemd160) is used for Bitcoin addresses, as the 20-byte ripemd160
# hash can save significant space.
hash160 = _HashAlgorithmInterface(('sha256', 'ripemd160'))

# (sha256 . sha256), “double-SHA256” is used as the proof-of-work function,
# the Merkle-tree compressor, and to generate transaction hash values for
# identification.
hash256 = _HashAlgorithmInterface(('sha256', 'sha256'))

# ===----------------------------------------------------------------------===

from blist import blist

def _merkle_hash256(*args):
    """The default transform provided to merkle(), which calculates the hash
    of its parameters, serializes and joins them together, then performs a
    has256 of the resulting string. There are two special cases: no arguments,
    which results in 0, and a single argument, whose hash value is returned
    unmodified."""
    # Return zero-hash is no arguments are provided (the hash of an empty
    # Merkle tree is defined to be zero).
    if not args:
        return 0
    # This helper function extracts and returns the hash value of a parameter.
    # Note that if the parameter is itself a Merkle tree or iterable, this
    # results in a recursive call to merkle().
    def _to_hash(h):
        if isinstance(h, numbers.Integral):
            return h
        if hasattr(h, 'hash'):
            return h.hash
        return merkle(h)
    # As a special case, a tree of length 1 is simply ungrouped - that single
    # hash value is returned to the user as-is.
    if len(args) == 1:
        return _to_hash(args[0])
    # Otherwise we are given two parameters, the hash values of which we
    # serialize, concatenate, and return the hash of.
    return hash256(b''.join(map(lambda h:serialize_hash(h, 32),
                                map(_to_hash, args)))).intdigest()

def merkle(hashes, func=_merkle_hash256):
    """Convert an iterable of hashes or hashable objects into a binary tree,
    construct the interior values using a passed-in constructor or compression
    function, and return the root value of the tree. The default compressor is
    the hash256 function, resulting in root-hash for the entire tree."""
    # We use append to duplicate the final item in the iterable of hashes, so
    # we need hashes to be a list-like object, regardless of what we were
    # passed.
    hashes = blist(iter(hashes))
    # If the passed-in iterable is empty, allow the constructor to choose our
    # return value:
    if not hashes:
        return func()
    # We must make sure the constructor/compressor is called for the case of
    # a single item as well, in which case the loop below is not entered.
    if len(hashes) == 1:
        return func(*hashes)
    # Build up successive layers of the binary hash tree, starting from the
    # bottom. We've reached the root node when the list has been reduced to
    # one element.
    while len(hashes) > 1:
        # For reasons lost to time, Satoshi decided that any traversal though
        # a bitcoin hash tree will have the same number steps. This is because
        # the last element is repeated when there is an odd number of elements
        # in level, resulting in the right portion of the binary tree being
        # extended into a full tower.
        hashes.append(hashes[-1])
        # By creating an iterator and then duplicating it, we cause two items
        # to be pulled out of the hashes array each time through the generator.
        # The last element is ignored if there is an odd number of elements
        # (meaning there was originally an even number, because of the append
        # operation above).
        hashes = blist(func(l,r) for l,r in izip(*(iter(hashes),)*2))
    # Return the root node of the Merkle tree to the caller.
    return hashes[0]

# ===----------------------------------------------------------------------===

from .errors import InvalidSecretError

try:
    from .ecdsa_openssl import (
        SECP256k1, Secret,
        Signature, CompactSignature,
        SigningKey, VerifyingKey)
except:
    from .ecdsa_generic import (
        SECP256k1, Secret,
        Signature, CompactSignature,
        SigningKey, VerifyingKey)

#
# End of File
#
