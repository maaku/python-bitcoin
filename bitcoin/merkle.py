# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import numbers

from .serialize import (
    serialize_hash, deserialize_hash,
    serialize_list, deserialize_list)

# ===----------------------------------------------------------------------===

from itertools import izip
from .crypto import hash256
from .tools import list

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
    hashes = list(iter(hashes))
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
        hashes = list(func(l,r) for l,r in izip(*(iter(hashes),)*2))
    # Return the root node of the Merkle tree to the caller.
    return hashes[0]

# ===----------------------------------------------------------------------===

from .mixins import HashableMixin, SerializableMixin

SENTINAL = object()

# A Merkle-tree is a strange beast. It is a collection that behaves like a
# sequence initially, then like a sorted mapping if/when it is pruned later.
# We are therefore obligated to implement portions of both the Sequence and
# Mapping interfaces.
#
# Since (1) it is often the case that full lists and pruned inclusion proofs
# are used in different contexts, and (2) the original bitcoin Merkle-tree
# didn't support pruning, and the “partial Merkle-tree” serialization came
# later, we split these two modes of operaiton into two classes.
#
# The MerkleList is an unpruned Merkle-tree, and the MerkleProof is its
# (possibly) pruned equivalent. They have different serialization formats,
# but hash the same (if the underlying list is the same).
#
# To support both classes, a generic Merkle-tree structure is used. It is
# called the MerkleNode class, representing alternatively either a single node
# of the Merkle-tree structure, or the subtree rooted at that node.

class MerkleNode(HashableMixin):
    __slots__ = 'left right size length prune _hash'.split()

    LEFT_NODE = False
    RIGHT_NODE = True

    def __init__(self, left=None, right=None, size=None,
                 length=None, prune=None, *args, **kwargs):
        # Empty list
        if left is None:
            if right is not None:
                raise TypeError(u"single element lists must use the left node")
            if any([size is not None and size != 0, length is not None and length != 0]):
                raise TypeError(u"without parameters, size/length must be zero")
            if prune is not None:
                raise TypeError(u"prune is meaningless with an empty list")
            size, length = 0, 0

        # Single element or fully pruned list
        elif right is None:
            if not isinstance(left, numbers.Integral):
                raise TypeError(u"single element node is only possible in a single element list")
            # If unspecified, we assume a size of 1, a single-element list, and
            # length is 1 for a list of size 1, 0 otherwise.
            size = max((size, 1))
            if length is None:
                length = (size==1 and prune is None) and 1 or 0
            if not (0 <= length <= 1):
                raise TypeError(u"impossible length for single element node: %d" % length)
            if prune not in (None,) + (length and () or (self.LEFT_NODE,)):
                raise TypeError(u"impossible length for single element node: %d" % length)
            if not length:
                prune = self.LEFT_NODE

        else:
            left_is_hash  = isinstance(left,  numbers.Integral)
            right_is_hash = isinstance(right, numbers.Integral)

            # Two-element leaf node. Possible options:
            #   hash, hash size=2 length=2
            #   hash, hash size=2 length=1 prune=LEFT_NODE
            #   hash, hash size=2 length=1 prune=RIGHT_NODE
            #   hash==hash size=1 length=1 prune=RIGHT_NODE
            if left_is_hash and right_is_hash:
                if size > 2:
                    raise TypeError(u"impossible for a leaf node to contain more than two elements")
                if size == 2 and length==1:
                    if prune not in (self.LEFT_NODE, self.RIGHT_NODE):
                        raise TypeError(u"must specify which branch is pruned")
                if size == 1:
                    if prune not in (None, self.RIGHT_NODE):
                        raise TypeError(u"unrecognized pruning choice for single element leaf node")
                    prune = self.RIGHT_NODE
                if size is None:
                    size = 2
                if length is None:
                    length = prune is None and 2 or 1

            # Left-pruned interior node
            elif left_is_hash and not right_is_hash:
                if size is None:
                    raise TypeError(u"size must be specified for pruned interior nodes")
                if length is not None and length != right.length:
                    raise TypeError(u"specified length does not match parameters")
                if prune not in (None, self.LEFT_NODE):
                    raise TypeError(u"illegal pruning choice for implicitly left-pruned interior node")
                length = right.length
                prune = self.LEFT_NODE

            # Right-pruned interior node
            elif not left_is_hash and right_is_hash:
                if size is None:
                    raise TypeError(u"size must be specified for pruned interior nodes")
                if not (left.size <= size <= 2*left.size):
                    raise TypeError(u"impossible size")
                if length is not None and length != left.length:
                    raise TypeError(u"specified length does not match parameters")
                if prune not in (None, self.RIGHT_NODE):
                    raise TypeError(u"illegal pruning choice for implicitly right-pruned interior node")
                length = left.length
                prune = self.RIGHT_NODE

            # Two-branch interior node
            else:
                if size is None:
                    size = left.size + right.size
                elif size != left.size + right.size:
                    raise TypeError(u"specified size does not match parameters")
                if length is None:
                    length = left.length + right.length
                elif length != left.length + right.length:
                    raise TypeError(u"specified length does not match parameters")
                if prune is not None:
                    raise TypeError(u"illegal pruning choice for non-pruned interior node")

        if length > size:
            raise TypeError(u"illegal length value, exceeds list size")

        super(MerkleNode, self).__init__(*args, **kwargs)
        self.left, self.right, self.size, self.length, self.prune = (
             left,      right,      size,      length,      prune)

    def hash__getter(self):
        left, right = (getattr(self.left,  'hash', self.left),
                       getattr(self.right, 'hash', self.right))
        if left is None:
            return 0
        if right is None:
            return left
        return hash256(b''.join([serialize_hash(left, 32),
                                 serialize_hash(right, 32)])).intdigest()

    def __hash__(self):
        "x.__hash__() <==> hash(x)"
        return self.hash

    def __nonzero__(self):
        "x.__nonzero__() <==> bool(x)"
        return bool(self.length)

    def __len__(self):
        "x.__len__() <==> len(x)"
        return self.length

    def items(self):
        "x.items() -> list of x's (key, value) pairs, as 2-tuples in sorted order"
        return sortedset(self.iteritems())
    def iteritems(self):
        "x.iteritems() -> an iterator over the (key, value) items of x in sorted order"
        left_is_hash = isinstance(self.left, numbers.Integral)
        right_is_hash = isinstance(self.right, numbers.Integral)
        if all([left_is_hash, right_is_hash]) or self.right is None:
            if all((self.size>=1, self.length, self.prune is not self.LEFT_NODE)):
                yield(0, self.left)
            if all((self.size>=2, self.length, self.prune is not self.RIGHT_NODE)):
                yield(1, self.right)
        if self.left is not None and not left_is_hash:
            for idx,hash_ in self.left.iteritems():
                yield(idx, hash_)
        if self.right is not None and not right_is_hash:
            offset = 2 ** ((self.size-1).bit_length() - 1)
            for idx,hash_ in self.right.iteritems():
                yield(offset+idx, hash_)

    def reversed_items(self):
        "x.reversed_items() -> list of x's (key, value) pairs, as 2-tuples in reversed order"
        return sortedset(self.reversed_items(), key=lambda x:-x[0])
    def reversed_iteritems(self):
        "x.reversed_iteritems() -> an iterator over the (key, value) items of x in reversed order"
        left_is_hash = isinstance(self.left, numbers.Integral)
        right_is_hash = isinstance(self.right, numbers.Integral)
        if all([left_is_hash, right_is_hash]) or self.right is None:
            if all((self.size>=2, self.length, self.prune is not self.RIGHT_NODE)):
                yield(1, self.right)
            if all((self.size>=1, self.length, self.prune is not self.LEFT_NODE)):
                yield(0, self.left)
        if self.right is not None and not right_is_hash:
            offset = 2 ** ((self.size-1).bit_length() - 1)
            for idx,hash_ in self.right.reversed_iteritems():
                yield(offset+idx, hash_)
        if self.left is not None and not left_is_hash:
            for idx,hash_ in self.left.reversed_iteritems():
                yield(idx, hash_)

    def keys(self):
        "x.keys() -> list of the keys of x in sorted order"
        return sortedset(self.iterkeys())
    def iterkeys(self):
        "x.iterkeys() -> an iterator over the keys of x in sorted order"
        for idx,hash_ in self.iteritems():
            yield idx

    def reversed_keys(self):
        "x.reversed_keys() -> list of the keys of x in reversed order"
        return sortedset(self.reversed_iterkeys(), key=lambda x:-x[0])
    def reversed_iterkeys(self):
        "x.reversed_iterkeys() -> an iterator over the keys of x in reversed order"
        for idx,hash_ in self.reversed_iteritems():
            yield idx

    def values(self):
        "x.values() -> list of the values of x sorted by key"
        return sortedset(self.itervalues())
    def itervalues(self):
        "x.itervalues() -> an iterator over the values of x sorted by key"
        for idx,hash_ in self.iteritems():
            yield hash_
    __iter__ = itervalues

    def reversed_values(self):
        "x.reversed_values() -> list of the values of x reverse-ordered by key"
        return sortedset(self.reversed_itervalues(), key=lambda x:-x[0])
    def reversed_itervalues(self):
        "x.reversed_itervalues() -> an iterator over the values of x reverse-ordered by key"
        for idx,hash_ in self.reversed_iteritems():
            yield hash_
    __reversed__ = reversed_itervalues

    def _get_by_index(self, index, path=None):
        """Returns the 2-tuple (node, idx) where node is either a terminal leaf
        node containing the value of that index in either it's left or right slot,
        or is the most specific node on the path which would contain the index if
        it were not pruned."""
        left_size = 2 ** ((self.size-1).bit_length() - 1)
        if index < 0 or self.size <= index:
            return (None, self, index)
        if index < left_size:
            if self.prune is self.LEFT_NODE:
                return (None, self, index)
            if isinstance(self.left, numbers.Integral):
                return (self.left, self, index)
            if path is not None:
                path.append((node, index, self.LEFT_NODE))
            return self.left._get_by_index(index, path)
        else:
            if self.prune is self.RIGHT_NODE:
                return (None, self, index)
            if isinstance(self.right, numbers.Integral):
                return (self.right, self, index)
            if path is not None:
                path.append((node, index, self.RIGHT_NODE))
            return self.right._get_by_index(index-left_size, path)

    def __contains__(self, index):
        "x.__contains__(y) <==> y in x"

    def __getitem__(self, index):
        "x.__getitem__(y) <==> x[y]"
        # FIXME: add support for slice objects
        value, node, offset = self._get_by_index(index)
        if value is None:
            raise IndexError(index)
        return value

    def __setitem__(self, index, value):
        "x.__setitem__(i, y) <==> x[i]=y"

    def __delitem__(self, index):
        "x.__delitem__(y) <==> del x[y]"

    def copy(self):
        "x.copy() -> a copy of x"

    def clear(self):
        "x.clear() -- remove all items from x"

    def append(self, value):
        "L.append(item) -- append item to end"

    def extend(self, iterable):
        "x.extend(iterable) -- extend list by appending elements from the iterable"

    def get(self, key, value=None):
        "x.get(k[,d]) -> x[k] if k in x, else d. d defaults to None."

    def pop(self, index=-1, value=SENTINAL):
        """L.pop([index]) -> item -- remove and return item at index (default last).
        Raises IndexError if list is empty or index is out of range."""

    def popitem(self):
        """x.popitem() -> (k, v), remove and return some (key, value) pair as a
        2-tuple; but raise KeyError if x is empty."""

    def setdefault(self, key, value):
        "x.setdefault(k[,d]) -> x.get(k,d), also set x[k]=d if k not in x"

    def update(self, other=None, **kwargs):
        """x.update(E, **F) -> None. update x from trie/dict/iterable E or F.
        If E has a .keys() method, does:     for k in E: x[k] = E[k]
        If E lacks .keys() method, does:     for (k, v) in E: x[k] = v
        In either case, this is followed by: for k in F: x[k] = F[k]"""

    def delete(self, keys):
        """x.delete(E) -> None. Same as `for k in E: del x[k]`"""

    def count(self, value):
        "x.count(value) -> integer -- return number of occurrences of value"

    def index(self, value, start=None, stop=None):
        """L.index(value, [start, [stop]]) -> integer -- return first index of value.
        Raises ValueError if the value is not present."""

    def remove(self, value):
        """L.remove(value) -- remove first occurrence of value.
        Raises ValueError if the value is not present."""

    def __add__(self, other):
        "x.__add__(y) <==> x+y"
    def __radd__(self, other):
        "x.__radd__(n) <==> n+x"
    def __iadd__(self, other):
        "x.__iadd__(y) <==> x+=y"

    def __mul__(self, other):
        "x.__mul__(n) <==> x*n"
    def __rmul__(self, other):
        "x.__rmul__(n) <==> n*x"
    def __imul__(self, other):
        "x.__imul__(y) <==> x*=y"

    def __eq__(self, other):
        "x.__eq__(y) <==> x==y"
        return self.hash == other.hash

    def __repr__(self):
        if self.left is None:
            return '%s()' % self.__class__.__name__

        if self.length == self.size:
            params_str = '[%s]' % ', '.join(
                '0x%064x' % hash_ for hash_ in self)
        else:
            params_str = '{%s}' % ', '.join(
                '%d: 0x%064x' % (idx,hash_) for idx,hash_ in self.iteritems())
            params_str += ', size=%d' % self.size

        return '%s(%s)' % (self.__class__.__name__, params_str)

class MerkleList(SerializableMixin):
    def __init__(self, *args, **kwargs):
        hashes = list(*args, **kwargs)
        super(MerkleList, self).__init__()
        for idx,hash_ in enumerate(hashes):
            hashes[idx] = getattr(hash_, 'hash', hash_)
        if not hashes:
            self._root = MerkleNode()
        elif len(hashes) == 1:
            self._root = MerkleNode(hashes[0])
        else:
            while len(hashes) > 1:
                next_hashes = list(MerkleNode(l,r) for l,r in izip(*(iter(hashes),)*2))
                if len(hashes) & 1:
                    left  = hashes[-1]
                    right = getattr(left, 'hash', left)
                    size  = getattr(left, 'size', 1)
                    next_hashes.append(MerkleNode(left, right, size=size))
                hashes = next_hashes
            self._root = hashes and hashes[0] or MerkleNode()

    @property
    def hash(self):
        return self._root.hash

    def serialize(self):
        raise NotImplementedError()
    @classmethod
    def deserialize(cls, file_):
        raise NotImplementedError()


#
# End of File
#
