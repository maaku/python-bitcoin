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

from python_patterns.utils.decorators import Property

from .tools import icmp, list

SENTINAL = object()

# ===----------------------------------------------------------------------===

class PatriciaLink(SerializableMixin):
    __slots__ = 'prefix hash'.split()

    def __init__(self, prefix=b'', hash=0, *args, **kwargs):
        super(PatriciaLink, self).__init__(*args, **kwargs)
        self.prefix = prefix
        self.hash = hash

    def serialize(self):
        result  = serialize_varchar(self.prefix)
        result += serialize_hash(self.hash, 32)
        return result
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['prefix'] = deserialize_varchar(file_)
        initargs['hash'] = deserialize_hash(file_, 32)
        return cls(**initargs)

    def __cmp__(self, other):
        result = cmp(self.prefix, other.prefix)
        # Lazily evaluate hash, only if we need to:
        if not result:
            result = cmp(self.hash, other.hash)
        return result
    def __repr__(self):
        return ('%s(prefix=%s, '
                   'hash=%064x)' % (
            self.__class__.__name__,
            self.prefix.encode('hex'),
            self.hash))

# ===----------------------------------------------------------------------===

from collections import Mapping
class PatriciaNode(SerializableMixin, HashableMixin):
    __slots__ = 'flags children value'.split()

    HAS_VALUE = 0x01

    def __init__(self, flags=0, children=None, value=None, *args, **kwargs):
        if children is None:
            children = []
        if isinstance(children, Mapping):
            list_ = []
            for prefix,hash_ in six.iteritems(children):
                if hasattr(hash_, 'hash'):
                    hash_ = hash_.hash
                list_.append(PatriciaLink(prefix=prefix,hash=hash_))
            children = list_
        if (flags & self.HAS_VALUE) and not isinstance(value, six.binary_type):
            raise TypeError(u"if HAS_VALUE is set, value must be a binary string")
        if not (flags & self.HAS_VALUE) and value is not None:
            raise TypeError(u"HAS_VALUE must be set if value is specified")
        super(PatriciaNode, self).__init__(*args, **kwargs)
        self.flags = flags
        self.value = value
        self.children_create()
        self.children.extend(sorted(children))

    def children_create(self):
        self.children = []
    def children_clear(self):
        self.children_create()
        del self.hash

    def serialize(self):
        result  = serialize_varint(self.flags)
        result += serialize_list(self.children, lambda l:l.serialize())
        if self.flags & self.HAS_VALUE:
            result += serialize_varchar(self.value)
        return result
    @staticmethod
    def deserialize_link(file_, *args, **kwargs):
        return PatriciaLink.deserialize(file_, *args, **kwargs)
    @classmethod
    def deserialize(cls, file_, *args, **kwargs):
        initargs = {}
        initargs['flags'] = deserialize_varint(file_)
        initargs['children'] = deserialize_list(file_, lambda x:cls.deserialize_link(x))
        if initargs['flags'] & cls.HAS_VALUE:
            initargs['value'] = deserialize_varchar(file_)
        return cls(**initargs)

    def __eq__(self, other):
        result = (     self.flags     ==      other.flags and
                  list(self.children) == list(other.children))
        if self.flags & self.HAS_VALUE:
            result = result and self.value==other.value
        return result
    def __repr__(self):
        if self.flags & self.HAS_VALUE:
            value_str = ', value=0x%s' % self.value.encode('hex')
        else:
            value_str = ''
        return ('%s(flags=%s, '
                   'children=[%s]%s)' % (
            self.__class__.__name__,
            bin(self.flags),
            ', '.join(map(repr, self.children)),
            value_str))

# ===----------------------------------------------------------------------===

from bisect import bisect_left
from os.path import commonprefix
class PatriciaTrie(object):
    """An ordered dictionary implemented with a hybrid level- and node-
    compressed prefix tree."""
    def __init__(self, *args, **kwargs):
        """Initialize a PATRICIA trie. Signature is the same as for regular
        dictionaries (see: help(dict))."""
        elems = dict(*args, **kwargs)
        for prefix,hash_ in six.iteritems(elems):
            if hasattr(hash_, 'hash'):
                elems[prefix] = hash_.hash
        super(PatriciaTrie, self).__init__()
        self.clear()
        self.update(elems)

    def _get_by_key(self, key, path=None):
        """Returns the 2-tuple (prefix, node) where node either contains the value
        corresponding to the key, or is the most specific prefix on the path which
        would contain the key if it were there. The key was found if prefix==key
        and the HAS_VALUE bit of node.flags is set."""
        prefix, subkey, node = b'', key, self._root
        while prefix != key:
            for idx,link in enumerate(node.children):
                if subkey.startswith(link.prefix):
                    subkey = subkey[len(link.prefix):]
                    prefix += link.prefix
                    if path is not None:
                        path.append((node, idx, link.prefix))
                    node = self._node[link.hash]
                    break
            else:
                break
        return (prefix, node)

    def _propogate(self, node, path):
        while path:
            parent, idx, prefix = path.pop()
            old_hash = parent.hash
            parent.children[idx].hash = node.hash
            del parent.hash
            new_hash = parent.hash

            del self._node[old_hash]
            self._node[new_hash] = parent

            node = parent

    def _forward_iterator(self):
        "Returns a forward iterator over the trie"
        path = [(self._root, 0, b'')]
        while path:
            node, idx, prefix = path.pop()
            if idx==0 and (node.flags & node.HAS_VALUE):
                yield (prefix, node.value)
            if idx<len(node.children):
                path.append((node, idx+1, prefix))
                path.append((
                    self._node[node.children[idx].hash],
                    0,
                    prefix + node.children[idx].prefix))

    def _reverse_iterator(self):
        "Returns a reverse/backwards iterator over the trie"
        path = [(self._root, len(self._root.children)-1, b'')]
        while path:
            node, idx, prefix = path.pop()
            if idx<0 and (node.flags & node.HAS_VALUE):
                yield (prefix, node.value)
            if idx>=0:
                path.append((node, idx-1, prefix))
                link = node.children[idx]
                node = self._node[link.hash]
                path.append((node, len(node.children)-1, prefix + link.prefix))

    def __len__(self):
        "x.__len__() <==> len(x)"
        return self._length

    def __getitem__(self, key):
        "x.__getitem__(y) <==> x[y]"
        prefix, node = self._get_by_key(key)
        if prefix==key and node.flags&node.HAS_VALUE:
            return node.value
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        "x.__setitem__(i, y) <==> x[i]=y"
        self.update({key: value})

    def __delitem__(self, key):
        "x.__delitem__(y) <==> del x[y]"
        self.delete([key])

    def __iter__(self):
        """x.__iter__() <==> iter(x)
        Return a forward iterator over the trie"""
        return self.iterkeys()

    def __reversed__(self):
        """x.__reversed__() <==> reversed(x)
        Return a reverse iterator over the trie"""
        return self.reversed_iterkeys()

    def __contains__(self, key):
        """x.__contains__(k) <==> k in x
        True if x has a key k, else False"""
        prefix, node = self._get_by_key(key)
        return prefix==key and node.flags&node.HAS_VALUE
    has_key = __contains__

    def clear(self):
        "x.clear() -> None.  Remove all items from x."
        self._root = PatriciaNode()
        self._node = {self._root.hash: self._root}
        self._length = 0

    def copy(self):
        "x.copy() -> a copy of x"
        return self.__class__(self.iteritems())
    deepcopy = copy

    def get(self, key, value=None):
        "x.get(k[,d]) -> x[k] if k in x, else d. d defaults to None."
        prefix, node = self._get_by_key(key)
        if prefix==key and node.flags&node.HAS_VALUE:
            return node.value
        else:
            return value

    def pop(self, key, value=SENTINAL):
        """x.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If d is not specified, KeyError is raised if the key is not found."""
        prefix, node = self._get_by_key(key)
        if prefix==key and node.flags&node.HAS_VALUE:
            value = node.value
            self.delete([key])
            return value
        else:
            if value is SENTINAL:
                raise KeyError(key)
            else:
                return value

    def popitem(self):
        """x.popitem() -> (k, v), remove and return some (key, value) pair as a
        2-tuple; but raise KeyError if x is empty."""
        if not self._length:
            raise KeyError(u"popitem(): trie is empty")
        key,value = next(self.reversed_iteritems())
        self.delete([key])
        return (key, value)

    def setdefault(self, key, value):
        "x.setdefault(k[,d]) -> x.get(k,d), also set x[k]=d if k not in x"
        if key not in self:
            self.update({key: value})

    def update(self, other=None, **kwargs):
        """x.update(E, **F) -> None. update x from trie/dict/iterable E or F.
        If E has a .keys() method, does:     for k in E: x[k] = E[k]
        If E lacks .keys() method, does:     for (k, v) in E: x[k] = v
        In either case, this is followed by: for k in F: x[k] = F[k]"""
        if other is None: other = []
        def _update(key, value):
            if not (isinstance(key, six.binary_type) and
                    isinstance(value, six.binary_type)):
                raise TypeError(u"%s can only map binary string -> binary "
                    u"string" % self.__class__.__name__)

            path = list()
            prefix, node = self._get_by_key(key, path=path)
            old_hash = node.hash

            # The simplist case is if the path already exists in the trie, in
            # which case no modifications need to be done to the trie structure.
            if prefix == key:
                if not (node.flags & node.HAS_VALUE):
                    node.flags |= node.HAS_VALUE
                    self._length += 1
                node.value = value

            else:
                self._length += 1

                # Otherwise there are three possible code paths depending on
                # whether the remaining the insertion key is a substring of any
                # of the child links, if they have a prefix in common, or if
                # matches any existing child of the node or not.
                remaining_key = key[len(prefix):]
                idx = bisect_left(node.children, PatriciaLink(remaining_key[:1], 0))

                if idx in xrange(len(node.children)):
                    common_prefix = commonprefix([node.children[idx].prefix, remaining_key])
                else:
                    common_prefix = ''

                if common_prefix == remaining_key:
                    new_node = PatriciaNode(
                        flags    = PatriciaNode.HAS_VALUE,
                        children = (PatriciaLink(
                            prefix = node.children[idx].prefix[len(common_prefix):],
                            hash   = node.children[idx].hash),),
                        value    = value)
                    self._node[new_node.hash] = new_node
                    node.children[idx].prefix = common_prefix
                    node.children[idx].hash = new_node.hash

                elif common_prefix:
                    new_node = PatriciaNode(
                        flags    = PatriciaNode.HAS_VALUE,
                        children = {},
                        value    = value)
                    inner_node = PatriciaNode(children={
                        remaining_key[len(common_prefix):]:
                            new_node,
                        node.children[idx].prefix[len(common_prefix):]:
                            node.children[idx].hash})
                    self._node[new_node.hash] = new_node
                    self._node[inner_node.hash] = inner_node
                    node.children[idx].prefix = common_prefix
                    node.children[idx].hash = inner_node.hash

                else:
                    new_node = PatriciaNode(
                        flags    = PatriciaNode.HAS_VALUE,
                        children = {},
                        value    = value)
                    self._node[new_node.hash] = new_node
                    node.children.insert(idx, PatriciaLink(remaining_key, new_node.hash))

            del node.hash
            del self._node[old_hash]
            self._node[node.hash] = node
            self._propogate(node, path=path)

        if isinstance(other, Mapping):
            for key in other:
                _update(key, other[key])
        else:
            for (key,value) in other:
                _update(key, value)
        for key,value in six.iteritems(kwargs):
            _update(key, kwargs[key])

    def delete(self, keys):
        """x.delete(E) -> None. Same as `for k in E: del x[k]`"""
        def _delete(key):
            path = list()
            prefix, node = self._get_by_key(key, path=path)

            if prefix != key or not node.flags&node.HAS_VALUE:
                raise KeyError(key)

            old_hash = node.hash
            node.flags = node.flags & ~node.HAS_VALUE
            node.value = None
            self._length -= 1

            if path and not node.children:
                # Remove from indices
                del self._node[old_hash]

                # Remove from parent
                node, idx, prefix = path.pop()
                old_hash = node.hash
                del node.children[idx]

            while (path and
                   len(node.children)==1 and
                   not (node.flags&node.HAS_VALUE)):
                # Remove from indices
                del self._node[old_hash]

                # Squash with child node
                parent, idx, prefix = path.pop()
                old_hash = parent.hash
                parent.children[idx].prefix += node.children[0].prefix
                parent.children[idx].hash = node.children[0].hash
                node = parent

            # Update indices
            del node.hash
            new_hash = node.hash
            del self._node[old_hash]
            self._node[new_hash] = node
            self._propogate(node, path=path)

        for key in keys:
            _delete(key)

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

    def reversed_keys(self):
        "x.reversed_keys() -> list of the keys of x in reversed order"
        return [x for x in self.reversed_iterkeys()]
    def reversed_iterkeys(self):
        "x.reversed_iterkeys() -> an iterator over the keys of x in reversed order"
        for key,value in self.reversed_iteritems():
            yield key

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

    def __eq__(self, other):
        "x.__eq__(o) <==> x == o"
        return self.hash == other.hash
    def __ne__(self, other):
        "x.__eq__(o) <==> x != o"
        return self.hash != other.hash
    def __lt__(self, other):
        "x.__lt__(o) <==> x < o"
        return icmp(self.iteritems(), other.iteritems()) < 0
    def __gt__(self, other):
        "x.__lt__(o) <==> x < o"
        return icmp(self.iteritems(), other.iteritems()) > 0
    def __le__(self, other):
        "x.__lt__(o) <==> x < o"
        return self.hash == other.hash or self < other
    def __ge__(self, other):
        "x.__lt__(o) <==> x < o"
        return self.hash == other.hash or self > other

    @Property
    def hash():
        "proxy for the hash property of the root node"
        def fget(self):
            return self._root.hash
        return locals()

    def __repr__(self):
        "x.__repr__() <==> repr(x)"
        repr_ = ', '.join(map(lambda i:"b'%s': 0x%s" % (
                                  i[0], i[1].encode('hex')),
                              self.iteritems()))
        return "%s({%s})" % (self.__class__.__name__, repr_)

#
# End of File
#
