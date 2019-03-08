# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

# Python 2 and 3 compatibility utilities
import six

from .mixins import HashableMixin, SerializableMixin
from .serialize import FlatData, VarInt

from .tools import Bits, BytesIO, icmp, lookahead, list, tuple

__all__ = (
    'BaseAuthTreeLink',
    'ComposableAuthTreeLink',
    'PatriciaAuthTreeLink',
    'BaseAuthTreeNode',
    'BaseComposableAuthTree',
    'MemoryComposableAuthTree',
    'BasePatriciaAuthTree',
    'MemoryPatriciaAuthTree',
)

SENTINAL = object()

# ===----------------------------------------------------------------------===

import numbers

class BaseAuthTreeLink(HashableMixin):
    __slots__ = 'prefix node _hash _count _size'.split()

    def __init__(self, prefix, node=None, hash=None, count=None, size=None, *args, **kwargs):
        # Coerce the prefix from whatever type it is into a Bits
        # field. This allows passing binary strings or any type
        # understood by the Bits constructor.
        if not isinstance(prefix, Bits):
            if isinstance(prefix, six.binary_type):
                prefix = Bits(bytes=prefix)
            else:
                prefix = Bits(prefix)
        # It is permissible to provide just a node or its hash as the
        # 2nd positional argument.
        if isinstance(node, numbers.Integral):
            node, hash = hash, node
        # Count and size must be provided for pruned links, otherwise
        # it can of course be extracted from the node object.
        if hasattr(node, 'count'): count = node.count
        if hasattr(node, 'size'):  size  = node.size
        super(BaseAuthTreeLink, self).__init__(*args, **kwargs)
        self.prefix, self.node, self._hash, self._count, self._size = (
             prefix,      node,       hash,       count,       size)

    @property
    def pruned(self):
        "Returns True if the link does not point to a node object."
        return self.node is None

    @property
    def count(self):
        "The number of items, pruned or otherwise, contained by this branch."
        if getattr(self, '_count', None) is None:
            self._count = getattr(self.node, 'count', 0)
        return self._count

    @property
    def size(self):
        "The canonical serialized size of this branch."
        if getattr(self, '_size', None) is None:
            self._size = getattr(self.node, 'size', 0)
        return self._size

    @property
    def length(self):
        "The number of non-pruned items in this branch."
        if self.pruned:
            return 0
        return self.node.length

    from .hash import hash256 as compressor
    def hash__getter(self):
        if getattr(self, '_hash', None) is not None:
            return self._hash
        value = self._compute_hash()
        self.hash__setter(value)
        return value

    def _thunk_other(inner):
        def outer(self, other):
            def _prefix(node):
                return getattr(node, 'prefix', NotImplemented)
            def _node(node):
                return getattr(node, 'node', NotImplemented)
            def _hash(node):
                return getattr(node, 'hash', NotImplemented)
            def _icmp():
                return icmp(
                    (x(self)  for x in (_prefix, _node, _hash)),
                    (x(other) for x in (_prefix, _node, _hash)))
            return inner(self, icmp=_icmp)
        return outer
    __lt__ = _thunk_other(lambda self,icmp:icmp() <  0)
    __le__ = _thunk_other(lambda self,icmp:icmp() <= 0)
    __eq__ = _thunk_other(lambda self,icmp:icmp() == 0)
    __ne__ = _thunk_other(lambda self,icmp:icmp() != 0)
    __ge__ = _thunk_other(lambda self,icmp:icmp() >= 0)
    __gt__ = _thunk_other(lambda self,icmp:icmp() >  0)

    def __repr__(self):
        parts = []
        parts.append('prefix=%s' % repr(self.prefix))
        parts.append((self.pruned and 'hash' or 'node') + '=0x%064x' % (self.hash or 0))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(parts))

class ComposableAuthTreeLink(BaseAuthTreeLink):
    def _compute_hash(self):
        hash_ = getattr(self.node, 'hash', None)
        if hash_ is not None:
            hash_ = self.compressor.serialize(hash_)
            for bit in self.prefix[:-len(self.prefix):-1]:
                hash_ = self.compressor(b''.join([
                    self.compressor(bit and b'\x04\x00' or b'\x01\x00').digest(),
                    hash_])).digest()
            hash_ = self.compressor.deserialize(BytesIO(hash_))
        return hash_

class PatriciaAuthTreeLink(BaseAuthTreeLink):
    def _compute_hash(self):
        return getattr(self.node, 'hash', None)

# ===----------------------------------------------------------------------===

import operator
from bisect import bisect_left
from os.path import commonprefix
from struct import pack, unpack
class BaseAuthTreeNode(SerializableMixin, HashableMixin):
    """An ordered dictionary implemented with a hybrid
    level- and node-compressed prefix tree."""
    __slots__ = 'value children extra prune_value _hash size length'.split()

    OFFSET_LEFT  = 0
    OFFSET_RIGHT = 2
    HAS_VALUE    = 4
    HASH_MASK    = 0x1f
    PRUNE_LEFT   = 5
    PRUNE_RIGHT  = 6
    PRUNE_VALUE  = 7

    @classmethod
    def _get_attr_class(cls, attr):
        return getattr(cls, ''.join(['get_', attr, '_class']),
            lambda:getattr(cls, ''.join([attr, '_class']), six.binary_type))()

    @classmethod
    def _prepare(cls, elem, attr):
        if not isinstance(elem, six.binary_type):
            serialize = getattr(elem, 'serialize', None)
            if six.callable(serialize):
                return serialize()
            attr_class = cls._get_attr_class(attr)
            serialize = getattr(attr_class, 'serialize', None)
            if six.callable(serialize):
                return serialize(elem)
        return elem
    @classmethod
    def _prepare_key(cls, elem):
        elem = cls._prepare(elem, 'key')
        if isinstance(elem, six.binary_type):
            elem = Bits(bytes=elem)
        return elem
    _prepare_value = classmethod(lambda cls,elem:cls._prepare(elem, 'value'))

    @classmethod
    def _unpickle(cls, string, attr):
        attr_class = cls._get_attr_class(attr)
        deserialize = getattr(attr_class, 'deserialize', None)
        if six.callable(deserialize):
            return deserialize(BytesIO(string))
        else:
            return attr_class(string)
    @classmethod
    def _unpickle_key(cls, string):
        string = getattr(string, 'bytes', string)
        return cls._unpickle(string, 'key')
    _unpickle_value = classmethod(lambda cls,string:cls._unpickle(string, 'value'))

    def __init__(self, value=None, children=None, extra=b'',
                 prune_value=None, *args, **kwargs):
        if value is not None:
            if not isinstance(value, six.binary_type):
                raise TypeError(u"value must be a binary string, or None")
            if prune_value is None:
                prune_value = False
        else:
            assert prune_value is None

        if children is None:
            children = tuple()
        children = sorted(children)

        assert 0 <= len(children) <= 2
        for link in children:
            assert 0 < len(link.prefix)
        assert len(children) == len(set(l.prefix[0] for l in children))

        count = int(value is not None)
        length = count - int(prune_value is True)

        size = 1 # flags
        size += len(VarInt(len(extra)).serialize())
        size += len(FlatData(extra).serialize())
        if value is not None:
            size += len(VarInt(len(value)).serialize())
            size += len(FlatData(value).serialize())

        for link in children:
            count += link.count
            length += link.length
            len_ = len(link.prefix)
            if 2 <= len_ <= 8:
                size += 1
            elif 9 <= len_:
                size += len(VarInt(len_-9).serialize())
                size += int((len_ + 6) // 8)
            size += link.size

        super(BaseAuthTreeNode, self).__init__(*args, **kwargs)

        self.value, self.prune_value, self.extra, self.count, self.length, self.size = (
             value,      prune_value,      extra,      count,      length,      size)
        getattr(self, 'children_create', lambda:setattr(self, 'children', list()))()
        self.children.extend(sorted(children))

    @property
    def left(self):
        if self.children and self.children[0].prefix[0] is False:
            return self.children[0]
        else:
            return None

    @property
    def right(self):
        if len(self.children)==2:
            return self.children[1]
        elif len(self.children)==1 and self.children[0].prefix[0] is True:
            return self.children[0]
        else:
            return None

    @property
    def flags(self):
        flags = reduce(operator.or_, (
            int(self.value is not None)                       << self.HAS_VALUE,
            int(getattr(self.left,  'pruned', False) is True) << self.PRUNE_LEFT,
            int(getattr(self.right, 'pruned', False) is True) << self.PRUNE_RIGHT,
            int(        self.prune_value             is True) << self.PRUNE_VALUE,))
        def _compressed_length(len_):
            if   len_ == 1: return 1
            elif len_ <= 8: return 2
            else:           return 3
        if self.left is not None:
            flags |= _compressed_length(len(self.left.prefix))  << self.OFFSET_LEFT
        if self.right is not None:
            flags |= _compressed_length(len(self.right.prefix)) << self.OFFSET_RIGHT
        return flags

    def serialize(self, digest=False):
        def _serialize_branch(link):
            # Prefix
            len_ = len(link.prefix)
            if 2 <= len_ <= 8:
                parts.append(
                    six.int2byte(
                        (Bits((False,)*(8-len_)+(True,)) +
                         link.prefix[:0:-1]).uint))
            elif 9 <= len_:
                skiplist = link.prefix[1:] + Bits((False,) * ((1-len_)%8))
                parts.append(VarInt(len_-9).serialize())
                parts.append(skiplist[::-1].tobytes()[::-1])
            # Branch
            if not digest:
                if link.pruned:
                    parts.append(self.compressor.serialize(link.hash))
                else:
                    parts.append(link.node.serialize(digest=digest))
            # Metadata
            if digest or link.pruned:
                parts.append(VarInt(link.count).serialize())
                parts.append(VarInt(link.size).serialize())
        parts = []
        flags = self.flags
        if digest:
            flags &= self.HASH_MASK
        parts.append(pack('B', flags))
        parts.append(VarInt(len(self.extra)).serialize())
        parts.append(FlatData(self.extra).serialize())
        if self.value is not None:
            parts.append(VarInt(len(self.value)).serialize())
            parts.append(FlatData(self.value).serialize())
        for link in (self.left, self.right):
            if link is not None:
                _serialize_branch(link)
        return b''.join(parts)
    @classmethod
    def deserialize(cls, file_):
        link_class = getattr(cls, 'get_link_class',
            lambda: getattr(cls, 'link_class'))()
        initargs = {}
        flags = VarInt.deserialize(file_)
        initargs['children'] = list()
        len_ = VarInt.deserialize(file_)
        initargs['extra'] = FlatData.deserialize(file_, len_)
        if flags & (1 << cls.HAS_VALUE):
            len_ = VarInt.deserialize(file_)
            initargs['value'] = FlatData.deserialize(file_, len_)
            initargs['prune_value'] = bool(flags & (1 << cls.PRUNE_VALUE))
        def _deserialize_branch(attr, prefix, bitlength, prune):
            if not bitlength:
                return
            elif bitlength == 2:
                skiplist = file_.read(1)
                assert len(skiplist) == 1
                bitlength = ord(skiplist).bit_length()
                prefix += Bits(bytes=skiplist)[:-bitlength:-1]
            elif bitlength == 3:
                bitlength = VarInt.deserialize(file_) + 9
                bytelength = (bitlength + 6) // 8
                bytes_ = file_.read(bytelength)
                assert len(bytes_) == bytelength
                prefix += Bits(bytes=bytes_[::-1])[:-bitlength:-1]
            if prune:
                initargs['children'].append(link_class(prefix,
                    hash  = self.compressor.deserialize(file_),
                    count = VarInt.deserialize(file_),
                    size  = VarInt.deserialize(file_)))
            else:
                initargs['children'].append(link_class(prefix,
                    node  = cls.deserialize(file_)))
        _deserialize_branch('left', Bits('0b0'),
            (flags >> cls.OFFSET_LEFT)  & 3, bool(flags & (1 << cls.PRUNE_LEFT)),)
        _deserialize_branch('right', Bits('0b1'),
            (flags >> cls.OFFSET_RIGHT) & 3, bool(flags & (1 << cls.PRUNE_RIGHT)),)
        return cls(**initargs)

    from .hash import hash256 as compressor
    def __bytes__(self):
        parts = []
        parts.append(self.compressor.new(self.serialize(digest=True)).digest())
        left_hash  = getattr(self.left,  'hash', 0)
        right_hash = getattr(self.right, 'hash', 0)
        if 0 not in (left_hash, right_hash):
            parts.append(self.compressor.new(
                self.compressor.serialize(left_hash) +
                self.compressor.serialize(right_hash)).digest())
        else:
            parts.append(
                self.compressor.serialize(left_hash or right_hash))
        return b''.join(parts)

    def __hash__(self):
        "x.__hash__() <==> hash(x)"
        return self.hash

    def __repr__(self):
        parts = []
        if self.value is not None:
            parts.append('\'%s\'.decode(\'hex\')' % self.value.encode('hex'))
            if self.prune_value:
                parts.append('prune_value=True')
        parts.append('children=[%s]' % ', '.join(map(repr, self.children)))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(parts))

    def __nonzero__(self):
        "x.__nonzero__() <==> bool(x)"
        return bool(self.length)
    __bool__ = __nonzero__

    def _thunk_other(inner):
        def outer(self, other):
            def _hash():
                return getattr(other, 'hash', NotImplemented)
            def _icmp():
                if isinstance(other, BaseAuthTreeNode):
                    return icmp(self.iteritems(), other.iteritems())
                elif hasattr(other, 'keys'):
                    return icmp(self.iteritems(), sorted((x,other[x]) for x in other))
                else:
                    try:
                        return icmp(self.iteritems(), sorted(other))
                    except TypeError:
                        return NotImplemented
            return inner(self, _hash, _icmp)
        return outer
    @_thunk_other
    def __lt__(self, hash, icmp):
        "x.__lt__(o) <==> x < o"
        return icmp() < 0
    @_thunk_other
    def __le__(self, hash, icmp):
        "x.__le__(o) <==> x <0 o"
        return self.hash == hash() or icmp() <= 0
    @_thunk_other
    def __eq__(self, hash, icmp):
        "x.__eq__(o) <==> x == o"
        result = hash()
        if result is NotImplemented:
            result = icmp() == 0
        else:
            result = result == self.hash
        return result
    def __ne__(self, other):
        "x.__ne__(o) <==> x != o"
        return not (self == other)
    @_thunk_other
    def __ge__(self, hash, icmp):
        "x.__ge__(o) <==> x >= o"
        return self.hash == hash() or icmp() >= 0
    @_thunk_other
    def __gt__(self, hash, icmp):
        "x.__gt__(o) <==> x > o"
        return icmp() > 0

    def __len__(self):
        "x.__len__() <==> len(x)"
        return self.length

    def _forward_iterator(self):
        "Returns a forward iterator over the trie"
        path = [(self, 0, Bits())]
        while path:
            node, idx, prefix = path.pop()
            if idx==0 and node.value is not None and not node.prune_value:
                yield (self._unpickle_key(prefix), self._unpickle_value(node.value))
            if idx<len(node.children):
                path.append((node, idx+1, prefix))
                link = node.children[idx]
                if not link.pruned:
                    path.append((link.node, 0, prefix + link.prefix))

    def _reverse_iterator(self):
        "Returns a reverse/backwards iterator over the trie"
        path = [(self, len(self.children)-1, Bits())]
        while path:
            node, idx, prefix = path.pop()
            if idx<0 and node.value is not None and not node.prune_value:
                yield (self._unpickle_key(prefix), self._unpickle_value(node.value))
            if idx>=0:
                path.append((node, idx-1, prefix))
                link = node.children[idx]
                if not link.pruned:
                    node = link.node
                    path.append((node, len(node.children)-1, prefix + link.prefix))

    def items(self):
        "x.items() -> list of x's (key, value) pairs, as 2-tuples in sorted order"
        return [x for x in self.iteritems()]
    def iteritems(self):
        "x.iteritems() -> an iterator over the (key, value) items of x in sorted order"
        return self._forward_iterator()

    def reversed_items(self):
        "x.reversed_items() -> list of x's (key, value) pairs, as 2-tuples in reversed order"
        return [x for x in self.reversed_iteritems()]
    def reversed_iteritems(self):
        "x.reversed_iteritems() -> an iterator over the (key, value) items of x in reversed order"
        return self._reverse_iterator()

    def keys(self):
        "x.keys() -> list of the keys of x in sorted order"
        return [x for x in self.iterkeys()]
    def iterkeys(self):
        "x.iterkeys() -> an iterator over the keys of x in sorted order"
        for key,value in self.iteritems():
            yield key
    __iter__ = iterkeys

    def reversed_keys(self):
        "x.reversed_keys() -> list of the keys of x in reversed order"
        return [x for x in self.reversed_iterkeys()]
    def reversed_iterkeys(self):
        "x.reversed_iterkeys() -> an iterator over the keys of x in reversed order"
        for key,value in self.reversed_iteritems():
            yield key
    __reversed__ = reversed_iterkeys

    def values(self):
        "x.values() -> list of the values of x sorted by key"
        return [x for x in self.itervalues()]
    def itervalues(self):
        "x.itervalues() -> an iterator over the values of x sorted by key"
        for key,value in self.iteritems():
            yield value

    def reversed_values(self):
        "x.reversed_values() -> list of the values of x reverse-ordered by key"
        return [x for x in self.reversed_itervalues()]
    def reversed_itervalues(self):
        "x.reversed_itervalues() -> an iterator over the values of x reverse-ordered by key"
        for key,value in self.reversed_iteritems():
            yield value

    def _get_node_by_key(self, key, path=None):
        """Returns the 2-tuple (prefix, node) where node either contains the value
        corresponding to the key, or is the most specific prefix on the path which
        would contain the key if it were there. The key was found if prefix==key
        and the node.value is not None."""
        prefix, subkey, node = Bits(), key, self
        while prefix != key:
            for idx,link in enumerate(node.children):
                if subkey.startswith(link.prefix):
                    if link.pruned:
                        return (prefix, node)
                    subkey = subkey[len(link.prefix):]
                    prefix += link.prefix
                    if path is not None:
                        path.append((node, idx, link.prefix))
                    node = link.node
                    break
            else:
                break
        return (prefix, node)

    def __contains__(self, key):
        """x.__contains__(k) <==> k in x
        True if x has a key k, else False"""
        _key = self._prepare_key(key)
        prefix, node = self._get_node_by_key(_key)
        return prefix==_key and node.value is not None
    has_key = __contains__

    def __getitem__(self, key):
        "x.__getitem__(y) <==> x[y]"
        _key = self._prepare_key(key)
        prefix, node = self._get_node_by_key(_key)
        if prefix==_key and node.value is not None:
            return self._unpickle_value(node.value)
        else:
            raise KeyError(key)

    def get(self, key, value=None):
        "x.get(k[,d]) -> x[k] if k in x, else d. d defaults to None."
        _key = self._prepare_key(key)
        prefix, node = self._get_node_by_key(_key)
        if prefix==_key and node.value is not None:
            return self._unpickle_value(node.value)
        else:
            return value

    def _propogate(self, node, path):
        link_class = getattr(self, 'get_link_class',
            lambda: getattr(self, 'link_class'))()
        node_class = getattr(self, 'get_node_class',
            lambda: getattr(self, 'node_class', self.__class__))()
        while path:
            parent, idx, prefix = path.pop()
            if node.length:
                link = link_class(prefix=prefix, node=node)
            else:
                link = link_class(prefix=prefix, hash=node.hash, count=node.count, size=node.size)
            node = node_class(
                value       = parent.value,
                children    = (list(x for x in parent.children[:idx]) + list((link,)) +
                               list(x for x in parent.children[idx+1:])),
                prune_value = parent.prune_value)
        for attr in self.__slots__:
            setattr(self, attr, getattr(node, attr, None))

    def _update(self, key, value):
        key = self._prepare_key(key)
        value = self._prepare_value(value)

        link_class = getattr(self, 'get_link_class',
            lambda: getattr(self, 'link_class'))()
        node_class = getattr(self, 'get_node_class',
            lambda: getattr(self, 'node_class', self.__class__))()

        # TODO: Maybe remove this and rely on duck typing?
        if not (isinstance(key, Bits) and
                isinstance(value, six.binary_type)):
            raise TypeError(u"%s can only map bitstring -> binary type"
                % self.__class__.__name__)

        path = list()
        prefix, old_node = self._get_node_by_key(key, path=path)

        # The simplist case is if the path already exists in the trie, in
        # which case no modifications need to be done to the trie structure.
        if prefix == key:
            if old_node.value == value:
                return
            new_node = node_class(value=value, children=old_node.children)

        else:
            # Otherwise there are three possible code paths depending on
            # whether the remaining the insertion key is a substring of any
            # of the child links, if they have a prefix in common, or if
            # matches any existing child of the node or not.
            remaining_key = key[len(prefix):]
            idx = bisect_left(old_node.children, link_class(prefix=remaining_key[:1]))

            if idx in range(len(old_node.children)):
                common_prefix = commonprefix([old_node.children[idx].prefix, remaining_key])
            else:
                common_prefix = Bits()

            if common_prefix == remaining_key:
                inner_node = node_class(
                    value    = value,
                    children = (link_class(
                        prefix = old_node.children[idx].prefix[len(common_prefix):],
                        node   = old_node.children[idx].node,
                        hash   = old_node.children[idx]._hash,
                        count  = old_node.children[idx].count,
                        size   = old_node.children[idx].size),))
                new_node = node_class(
                    value       = old_node.value,
                    children    = (list(x for x in old_node.children[:idx]) +
                                   list((link_class(prefix=common_prefix, node=inner_node),)) +
                                   list(x for x in old_node.children[idx+1:])),
                    prune_value = old_node.prune_value)

            elif len(common_prefix):
                leaf_node = node_class(
                    value    = value,
                    children = ())
                inner_node = node_class(
                    value    = None,
                    children = (
                        link_class(
                            prefix = remaining_key[len(common_prefix):],
                            node   = leaf_node),
                        link_class(
                            prefix = old_node.children[idx].prefix[len(common_prefix):],
                            node   = old_node.children[idx].node,
                            hash   = old_node.children[idx]._hash,
                            count  = old_node.children[idx].count,
                            size   = old_node.children[idx].size),))
                new_node = node_class(
                    value       = old_node.value,
                    children    = (list(x for x in old_node.children[:idx]) +
                                   list((link_class(prefix=common_prefix, node=inner_node),)) +
                                   list(x for x in old_node.children[idx+1:])),
                    prune_value = old_node.prune_value)

            else:
                leaf_node = node_class(
                    value    = value,
                    children = {})
                new_node = node_class(
                    value       = old_node.value,
                    children    = (list(x for x in old_node.children[:idx]) +
                                   list((link_class(prefix=remaining_key, node=leaf_node),)) +
                                   list(x for x in old_node.children[idx:])),
                    prune_value = old_node.prune_value)

        self._propogate(new_node, path=path)

    def update(self, other=None, **kwargs):
        """x.update(E, **F) -> None. update x from trie/dict/iterable E or F.
        If E has a .keys() method, does:     for k in E: x[k] = E[k]
        If E lacks .keys() method, does:     for (k, v) in E: x[k] = v
        In either case, this is followed by: for k in F: x[k] = F[k]"""
        if other is None:
            other = ()

        if hasattr(other, 'keys'):
            for key in other:
                self._update(key, other[key])
        else:
            for key,value in other:
                self._update(key, value)

        for key,value in six.iteritems(kwargs):
            self._update(key, value)

    def __setitem__(self, key, value):
        "x.__setitem__(i, y) <==> x[i]=y"
        self.update(((key, value),))

    def setdefault(self, key, value):
        "x.setdefault(k[,d]) -> x.get(k,d), also set x[k]=d if k not in x"
        if key not in self:
            self.update(((key, value),))

    def _trim(self, key):
        key, key_ = self._prepare_key(key), key

        link_class = getattr(self, 'get_link_class',
            lambda: getattr(self, 'link_class'))()
        node_class = getattr(self, 'get_node_class',
            lambda: getattr(self, 'node_class', self.__class__))()

        path = list()
        prefix, old_node = self._get_node_by_key(key, path=path)

        if key == prefix:
            new_node = node_class(
                value       = old_node.value,
                children    = (link_class(prefix=link.prefix, hash=link.hash, count=link.count, size=link.size)
                               for link in old_node.children),
                prune_value = old_node.value is not None and True or None)

            length = old_node.length

        else:
            remaining_key = key[len(prefix):]
            idx = bisect_left(old_node.children, link_class(prefix=remaining_key[:1]))
            if idx not in range(len(old_node.children)):
                return 0

            link = old_node.children[idx]
            if link.pruned:
                return 0

            common_prefix = commonprefix([link.prefix, remaining_key])
            if common_prefix != remaining_key:
                return 0

            new_node = node_class(
                value       = old_node.value,
                children    = (list(x for x in old_node.children[:idx]) +
                               list((link_class(prefix = link.prefix,
                                                hash   = link.hash,
                                                count  = link.count,
                                                size   = link.size),)) +
                               list(x for x in old_node.children[idx+1:])),
                prune_value = old_node.prune_value)

            length = link.length

        self._propogate(new_node, path=path)
        return length

    def trim(self, prefixes):
        "Prunes any keys beginning with the specified the specified prefixes."
        _prefixes, prefixes = set(map(lambda k:self._prepare_key(k), prefixes)), list()
        for t in lookahead(sorted(_prefixes)):
            if t[1] is not None:
                if t[0] == commonprefix(t):
                    continue
            prefixes.append(t[0])
        length = 0
        for prefix in prefixes:
            length += self._trim(prefix)
        return length

    def _prune(self, key):
        link_class = getattr(self, 'get_link_class',
            lambda: getattr(self, 'link_class'))()
        node_class = getattr(self, 'get_node_class',
            lambda: getattr(self, 'node_class', self.__class__))()

        key, _key, path = self._prepare_key(key), key, list()
        prefix, old_node = self._get_node_by_key(key, path=path)
        if key != prefix or old_node.value is None or old_node.prune_value:
            raise KeyError(_key)

        new_node = node_class(
            value       = old_node.value,
            children    = old_node.children,
            prune_value = True)
        self._propogate(new_node, path=path)

    def prune(self, keys):
        "Removes the specified keys without changing any hash values."
        for key in keys:
            self._prune(key)

    def _delete(self, key):
        key, key_ = self._prepare_key(key), key

        link_class = getattr(self, 'get_link_class',
            lambda: getattr(self, 'link_class'))()
        node_class = getattr(self, 'get_node_class',
            lambda: getattr(self, 'node_class', self.__class__))()

        path = list()
        prefix, old_node = self._get_node_by_key(key, path=path)

        if prefix != key or old_node.value is None:
            raise KeyError(key_)

        new_node = node_class(value=None, children=old_node.children)

        if path and not new_node.size:
            # Remove from parent
            parent, idx, prefix = path.pop()
            new_node = node_class(
                value       = parent.value,
                children    = (list(x for x in parent.children[:idx]) +
                               list(x for x in parent.children[idx+1:])),
                prune_value = parent.prune_value)

        while all([path, len(new_node.children)==1, new_node.value is None]):
            # Squash with child node
            parent, idx, prefix = path.pop()
            new_node = node_class(
                value       = parent.value,
                children    = (list(x for x in parent.children[:idx]) +
                               list((link_class(
                                   prefix = prefix + new_node.children[0].prefix,
                                   node   = new_node.children[0].node,
                                   hash   = new_node.children[0]._hash,
                                   count  = new_node.children[0].count,
                                   size   = new_node.children[0].size),)) +
                               list(x for x in parent.children[idx+1:])),
                prune_value = parent.prune_value)

        self._propogate(new_node, path=path)

    def delete(self, keys):
        """x.delete(E) -> None. Same as `for k in E: del x[k]`"""
        for key in keys:
            self._delete(key)

    def __delitem__(self, key):
        "x.__delitem__(y) <==> del x[y]"
        self.delete([key])

    def copy(self, node_class=None):
        if node_class is None:
            node_class = getattr(self, 'get_node_class',
                lambda: getattr(self, 'node_class', self.__class__))()
        return node_class(
            value       = self.value,
            children    = self.children,
            prune_value = self.prune_value)

class BaseComposableAuthTree(BaseAuthTreeNode):
    link_class = ComposableAuthTreeLink
class MemoryComposableAuthTree(BaseComposableAuthTree):
    pass

class BasePatriciaAuthTree(BaseAuthTreeNode):
    link_class = PatriciaAuthTreeLink
class MemoryPatriciaAuthTree(BasePatriciaAuthTree):
    pass

# End of File
