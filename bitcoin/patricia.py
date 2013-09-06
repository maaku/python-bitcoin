# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

# Python 2 and 3 compatibility utilities
import six

from bitcoin.mixins import HashableMixin, SerializableMixin
from bitcoin.serialize import (
    serialize_varint, deserialize_varint,
    serialize_varchar, deserialize_varchar,
    serialize_hash, deserialize_hash,
    serialize_list, deserialize_list)

from .tools import Bits, StringIO, icmp, list, tuple

SENTINAL = object()

# ===----------------------------------------------------------------------===

import numbers

class PatriciaLink(SerializableMixin, HashableMixin):
    __slots__ = 'prefix node _hash'.split()

    def __init__(self, prefix, node=None, hash=None, *args, **kwargs):
        if not isinstance(prefix, Bits):
            if isinstance(prefix, six.binary_type):
                prefix = Bits(bytes=prefix)
            else:
                prefix = Bits(prefix)
        if isinstance(node, numbers.Integral):
            node, hash = hash, node
        super(PatriciaLink, self).__init__(*args, **kwargs)
        self.prefix, self.node, self._hash = prefix, node, hash

    @property
    def pruned(self):
        return self.node is None

    def serialize(self, digest=False):
        result = serialize_varchar(self.prefix)
        if digest:
            result += serialize_hash(self.hash, 32)
        else:
            result += serialize_varchar(self.node.serialize(digest=digest))
        return result
    @classmethod
    def deserialize_node(cls, file_, *args, **kwargs):
        node_class = getattr(self, 'get_node_class', lambda:
                     getattr(self, 'node_class', PatriciaNode))()
        return node_class.deserialize(file_, *args, **kwargs)
    @classmethod
    def deserialize(cls, file_, digest=False, *args, **kwargs):
        initargs = {}
        initargs['prefix'] = deserialize_varchar(file_)
        if digest:
            initargs['hash'] = deserialize_hash(file_, 32)
        else:
            initargs['node'] = cls.deserialize_node(file_, digest=digest, *args, **kwargs)
        return cls(**initargs)

    def hash__getter(self):
        if getattr(self, '_hash', None) is not None:
            return self._hash
        value = getattr(self.node, 'hash', None)
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
        parts.append('hash=0x%064x' % (self.hash or 0))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(parts))

# ===----------------------------------------------------------------------===

import operator
from bisect import bisect_left
from os.path import commonprefix
from struct import pack, unpack
class PatriciaNode(SerializableMixin, HashableMixin):
    """An ordered dictionary implemented with a hybrid level- and node-
    compressed prefix tree."""
    __slots__ = 'value children _hash size length'.split()

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
            return deserialize(StringIO(string))
        else:
            return attr_class(string)
    @classmethod
    def _unpickle_key(cls, string):
        string = getattr(string, 'bytes', string)
        return cls._unpickle(string, 'key')
    _unpickle_value = classmethod(lambda cls,string:cls._unpickle(string, 'value'))

    def __init__(self, value=None, children=None, prune_value=None, *args, **kwargs):
        if value is not None:
            if not isinstance(value, six.binary_type):
                raise TypeError(u"value must be a binary string, or None")
            if prune_value is None:
                prune_value = False
        else:
            assert prune_value is None

        if children is None:
            children = tuple()
        link_class = getattr(self, 'get_link_class',
            lambda: getattr(self, 'link_class', PatriciaLink))()
        if hasattr(children, 'keys'):
            _children = list()
            for prefix in children:
                if not isinstance(children[prefix], numbers.Integral):
                    _children.append(link_class(prefix=prefix, node=children[prefix]))
                else:
                    _children.append(link_class(prefix=prefix, hash=children[prefix]))
            children = _children
        else:
            _children = list()
            for child in children:
                if not all(hasattr(child, x) for x in ('prefix', 'node', 'hash')):
                    child = link_class(*child)
                _children.append(child)
            children = _children
        children = sorted(children)

        assert 0 <= len(children) <= 2
        for link in children:
            assert 0 < len(link.prefix) < 2**64
        assert len(children) == len(set(l.prefix[0] for l in children))

        super(PatriciaNode, self).__init__(*args, **kwargs)

        self.value, self.prune_value = value, prune_value
        getattr(self, 'children_create', lambda:setattr(self, 'children', list()))()
        self.children.extend(sorted(children))

        size = int(value is not None)
        length = size - int(prune_value is True)
        for link in children:
            if not link.pruned:
                size += link.node.size
                length += link.node.length
        self.size, self.length = size, length

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
        if self.left is not None:
            flags |= min(3, len(self.left.prefix))  << self.OFFSET_LEFT
        if self.right is not None:
            flags |= min(3, len(self.right.prefix)) << self.OFFSET_RIGHT
        return flags

    def serialize(self, digest=False):
        def _serialize_link(link):
            len_ = len(link.prefix)
            if len_ >= 3:
                parts.append(serialize_varint(len_-3))
            parts.append(link.prefix[1:].tobytes())
            if digest or link.pruned:
                parts.append(serialize_hash(link.hash, 32))
            else:
                parts.append(link.node.serialize(digest=digest))
        parts = []
        flags = self.flags
        if digest:
            flags &= self.HASH_MASK
        parts.append(pack('B', flags))
        if self.left is not None:
            _serialize_link(self.left)
        if self.right is not None:
            _serialize_link(self.right)
        if self.value is not None:
            parts.append(serialize_varchar(self.value))
        return b''.join(parts)
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        flags = deserialize_varint(file_)
        initargs['children'] = {}
        def _deserialize_branch(attr, implicit, bitlength, prune):
            if not bitlength:
                return
            if bitlength == 3:
                bitlength = deserialize_varint(file_) + 3
            bytelength = (bitlength + 7) // 8
            bytes_ = file_.read(bytelength)
            assert len(bytes_) == bytelength
            prefix = implicit + Bits(bytes=bytes_, length=bitlength-1)
            if prune:
                initargs['children'][prefix] = deserialize_hash(file_, 32)
            else:
                initargs['children'][prefix] = cls.deserialize(file_)
        _deserialize_branch('left', Bits([False]),
            (flags >> cls.OFFSET_LEFT)  & 3, bool(flags & (1 << cls.PRUNE_LEFT)),)
        _deserialize_branch('right', Bits([True]),
            (flags >> cls.OFFSET_RIGHT) & 3, bool(flags & (1 << cls.PRUNE_RIGHT)),)
        if flags & (1 << cls.HAS_VALUE):
            initargs['value'] = deserialize_varchar(file_)
            initargs['prune_value'] = bool(flags & (1 << cls.PRUNE_VALUE))
        return cls(**initargs)

    def hash__getter(self):
        return super(PatriciaNode, self).hash__getter(digest=True)

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
                if isinstance(other, PatriciaNode):
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
        path = [(self, 0, b'')]
        while path:
            node, idx, prefix = path.pop()
            if idx==0 and node.value is not None:
                yield (self._unpickle_key(prefix), self._unpickle_value(node.value))
            if idx<len(node.children):
                path.append((node, idx+1, prefix))
                path.append((
                    node.children[idx].node,
                    0,
                    prefix + node.children[idx].prefix))

    def _reverse_iterator(self):
        "Returns a reverse/backwards iterator over the trie"
        path = [(self, len(self.children)-1, b'')]
        while path:
            node, idx, prefix = path.pop()
            if idx<0 and node.value is not None:
                yield (self._unpickle_key(prefix), self._unpickle_value(node.value))
            if idx>=0:
                path.append((node, idx-1, prefix))
                link = node.children[idx]
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
        and the HAS_VALUE bit of node.flags is set."""
        prefix, subkey, node = b'', key, self
        while prefix != key:
            for idx,link in enumerate(node.children):
                if subkey.startswith(link.prefix):
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
            lambda: getattr(self, 'link_class', PatriciaLink))()
        node_class = getattr(self, 'get_node_class',
            lambda: getattr(self, 'node_class', self.__class__))()
        while path:
            parent, idx, prefix = path.pop()
            node = node_class(
                value    = parent.value,
                children = (list(x for x in parent.children[:idx]) +
                            list((link_class(prefix=prefix, node=node),)) +
                            list(x for x in parent.children[idx+1:])))
        for attr in self.__slots__:
            setattr(self, attr, getattr(node, attr, None))

    def _update(self, key, value):
        key = self._prepare_key(key)
        value = self._prepare_value(value)

        link_class = getattr(self, 'get_link_class',
            lambda: getattr(self, 'link_class', PatriciaLink))()
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
            idx = bisect_left(old_node.children, link_class(prefix=remaining_key[:1], node=None))

            if idx in xrange(len(old_node.children)):
                common_prefix = commonprefix([old_node.children[idx].prefix, remaining_key])
            else:
                common_prefix = ''

            if common_prefix == remaining_key:
                inner_node = node_class(
                    value    = value,
                    children = (link_class(
                        prefix = old_node.children[idx].prefix[len(common_prefix):],
                        node   = old_node.children[idx].node,
                        hash   = old_node.children[idx]._hash),))
                new_node = node_class(
                    value    = old_node.value,
                    children = (list(x for x in old_node.children[:idx]) +
                                list((link_class(prefix=common_prefix, node=inner_node),)) +
                                list(x for x in old_node.children[idx+1:])))

            elif len(common_prefix):
                leaf_node = node_class(
                    value    = value,
                    children = {})
                inner_node = node_class(
                    value    = None,
                    children = {
                        remaining_key[len(common_prefix):]:
                            leaf_node,
                        old_node.children[idx].prefix[len(common_prefix):]:
                            old_node.children[idx].node})
                new_node = node_class(
                    value    = old_node.value,
                    children = (list(x for x in old_node.children[:idx]) +
                                list((link_class(prefix=common_prefix, node=inner_node),)) +
                                list(x for x in old_node.children[idx+1:])))

            else:
                leaf_node = node_class(
                    value    = value,
                    children = {})
                new_node = node_class(
                    value    = old_node.value,
                    children = (list(x for x in old_node.children[:idx]) +
                                list((link_class(prefix=remaining_key, node=leaf_node),)) +
                                list(x for x in old_node.children[idx:])))

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

    def _delete(self, key):
        key, key_ = self._prepare_key(key), key

        link_class = getattr(self, 'get_link_class',
            lambda: getattr(self, 'link_class', PatriciaLink))()
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
                value    = parent.value,
                children = (list(x for x in parent.children[:idx]) +
                            list(x for x in parent.children[idx+1:])))

        while all([path, len(new_node.children)==1, new_node.value is None]):
            # Squash with child node
            parent, idx, prefix = path.pop()
            new_node = node_class(
                value    = parent.value,
                children = (list(x for x in parent.children[:idx]) +
                            list((link_class(
                                prefix = prefix + new_node.children[0].prefix,
                                node   = new_node.children[0].node,
                                hash   = new_node.children[0]._hash),)) +
                            list(x for x in parent.children[idx+1:])))

        self._propogate(new_node, path=path)

    def delete(self, keys):
        """x.delete(E) -> None. Same as `for k in E: del x[k]`"""
        for key in keys:
            self._delete(key)

    def __delitem__(self, key):
        "x.__delitem__(y) <==> del x[y]"
        self.delete([key])

    def copy(self):
        node_class = getattr(self, 'get_node_class',
            lambda: getattr(self, 'node_class', self.__class__))()
        return node_class(value=self.value, children=self.children)

#
# End of File
#
