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

from .tools import StringIO, icmp, list, tuple

SENTINAL = object()

# ===----------------------------------------------------------------------===

from recordtype import recordtype
PatriciaLink = recordtype('PatriciaLink', 'prefix node'.split())
PatriciaLink.__lt__ = lambda self, other: (self.prefix, self.node) <  (other.prefix, other.node)
PatriciaLink.__le__ = lambda self, other: (self.prefix, self.node) <= (other.prefix, other.node)
PatriciaLink.__eq__ = lambda self, other: (self.prefix, self.node) == (other.prefix, other.node)
PatriciaLink.__ne__ = lambda self, other: (self.prefix, self.node) != (other.prefix, other.node)
PatriciaLink.__ge__ = lambda self, other: (self.prefix, self.node) >= (other.prefix, other.node)
PatriciaLink.__gt__ = lambda self, other: (self.prefix, self.node) >  (other.prefix, other.node)
PatriciaLink.__repr__ = lambda self: '%s(prefix=\'%s\'.decode(\'hex\'), node=0x%064x)' % (
    self.__class__.__name__, self.prefix.encode('hex'), self.node.hash)

# ===----------------------------------------------------------------------===

from bisect import bisect_left
from os.path import commonprefix
class PatriciaNode(SerializableMixin, HashableMixin):
    __slots__ = 'value extra children _hash size length start end parents'.split()

    HAS_VALUE = 0x1
    HAS_EXTRA = 0x2

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
    _prepare_key = lambda cls,elem:cls._prepare(elem, 'key')
    _prepare_value = lambda cls,elem:cls._prepare(elem, 'value')

    @classmethod
    def _unpickle(cls, string, attr):
        attr_class = cls._get_attr_class(attr)
        deserialize = getattr(attr_class, 'deserialize', None)
        if six.callable(deserialize):
            return deserialize(StringIO(string))
        else:
            return attr_class(string)
    _unpickle_key = lambda cls,string:cls._unpickle(string, 'key')
    _unpickle_value = lambda cls,string:cls._unpickle(string, 'value')

    def __init__(self, value=None, extra=None, children=None,
                 start=None, end=None, *args, **kwargs):
        if value is not None and not isinstance(value, six.binary_type):
            raise TypeError(u"value must be a binary string, or None")
        if extra is not None and not isinstance(extra, six.binary_type):
            raise TypeError(u"extra must be a binary string, or None")
        if children is None:
            children = tuple()
        if hasattr(children, 'keys'):
            children = tuple(
                PatriciaLink(prefix=prefix,node=children[prefix])
                for prefix in sorted(children))

        super(PatriciaNode, self).__init__(*args, **kwargs)

        self.value = value
        self.extra = extra
        getattr(self, 'children_create', lambda x:setattr(x, 'children', list()))(self)
        self.children.extend(children)
        getattr(self, 'parents_create', lambda x:setattr(x, 'parents', set()))(self)
        self.size = int(value is not None)
        self.length = self.size
        for child in children:
            child.node.parents.add(self)
            self.size += child.node.size
            self.length += child.node.length
        self.start = start
        self.end = end

    @property
    def flags(self):
        flags = 0
        if self.value is not None: flags |= self.HAS_VALUE
        if self.extra is not None: flags |= self.HAS_EXTRA
        return flags

    def serialize(self, digest=False):
        flags = self.flags
        result = serialize_varint(flags)
        if digest:
            result += serialize_list(self.children,
                lambda child:b''.join([serialize_varchar(child.prefix),
                                       serialize_hash(child.node.hash, 32)]))
        else:
            result += serialize_list(self.children,
                lambda child:b''.join([serialize_varchar(child.prefix),
                                       serialize_varchar(child.node.serialize(digest=digest))]))
        if flags & self.HAS_VALUE:
            result += serialize_varchar(self.value)
        if flags & self.HAS_EXTRA:
            result += serialize_varchar(self.extra)
        return result
    @staticmethod
    def deserialize_link(file_, nodes, *args, **kwargs):
        prefix = deserialize_varchar(file_)
        hash = deserialize_hash(file_, 32)
        return getattr(cls, 'get_patricia_link_class',
            lambda: getattr(cls, 'patricia_link_class', PatriciaLink)
            )(prefix=prefix, node=nodes[hash], *args, **kwargs)
    @classmethod
    def deserialize(cls, file_, start=0, end=None, nodes=None, *args, **kwargs):
        nodes = nodes or {}
        initargs = {}
        flags = deserialize_varint(file_)
        initargs['children'] = deserialize_list(file_,
            lambda x:cls.deserialize_link(x, nodes))
        if flags & cls.HAS_VALUE:
            initargs['value'] = deserialize_varchar(file_)
        if flags & cls.HAS_EXTRA:
            initargs['extra'] = deserialize_varchar(file_)
        return cls(start=start, end=end, **initargs)

    def hash__getter(self):
        return super(PatriciaNode, self).hash__getter(digest=True)

    def __hash__(self):
        "x.__hash__() <==> hash(x)"
        return self.hash

    def __repr__(self):
        if self.value is not None:
            value_str = 'value=\'%s\'.decode(\'hex\'), ' % self.value.encode('hex')
        else:
            value_str = ''
        if self.extra is not None:
            extra_str = 'extra=\'%s\'.decode(\'hex\'), ' % self.extra.encode('hex')
        else:
            extra_str = ''
        if self.start is not None:
            start_str = ', start=%d' % self.start
        else:
            start_str = ''
        if self.end is not None:
            end_str = ', end=%d' % self.end
        else:
            end_str = ''
        return ('%s(%s%schildren=[%s]%s%s)' % (
            self.__class__.__name__,
            value_str,
            extra_str,
            ', '.join(map(repr, self.children)),
            start_str,
            end_str))

    def __nonzero__(self):
        "x.__nonzero__() <==> bool(x)"
        return bool(self.length)

    def __lt__(self, other):
        "x.__lt__(o) <==> x < o"
        return icmp(self.iteritems(), other.iteritems()) < 0
    def __le__(self, other):
        "x.__lt__(o) <==> x < o"
        return self.hash == other.hash or self < other
    def __eq__(self, other):
        "x.__eq__(o) <==> x == o"
        return self.hash == other.hash
    def __ne__(self, other):
        "x.__eq__(o) <==> x != o"
        return self.hash != other.hash
    def __ge__(self, other):
        "x.__lt__(o) <==> x < o"
        return self.hash == other.hash or self > other
    def __gt__(self, other):
        "x.__lt__(o) <==> x < o"
        return icmp(self.iteritems(), other.iteritems()) > 0

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

    def _get_by_key(self, key, path=None):
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
        prefix, node = self._get_by_key(_key)
        return prefix==_key and node.value is not None
    has_key = __contains__

    def __getitem__(self, key):
        "x.__getitem__(y) <==> x[y]"
        _key = self._prepare_key(key)
        prefix, node = self._get_by_key(_key)
        if prefix==_key and node.value is not None:
            return self._unpickle_value(node.value)
        else:
            raise KeyError(key)

    def get(self, key, value=None):
        "x.get(k[,d]) -> x[k] if k in x, else d. d defaults to None."
        _key = self._prepare_key(key)
        prefix, node = self._get_by_key(_key)
        if prefix==_key and node.value is not None:
            return self._unpickle_value(node.value)
        else:
            return value

    def _propogate(self, node, path):
        while path:
            parent, idx, prefix = path.pop()
            parent.children[idx].node = node
            parent.size, parent.length = (int(parent.value is not None),)*2
            for link in parent.children:
                parent.size += link.node.size
                parent.length += link.node.length
            del parent.hash
            node = parent

    def _update(self, key, value):
        key = self._prepare_key(key)
        value = self._prepare_value(value)

        if not (isinstance(key, six.binary_type) and
                isinstance(value, six.binary_type)):
            raise TypeError(u"%s can only map binary string -> binary "
                u"string" % self.__class__.__name__)

        path = list()
        prefix, node = self._get_by_key(key, path=path)

        # The simplist case is if the path already exists in the trie, in
        # which case no modifications need to be done to the trie structure.
        if prefix == key:
            node.value = value
            if node.value is not None:
                node.size += 1
                node.length += 1

        else:
            # Otherwise there are three possible code paths depending on
            # whether the remaining the insertion key is a substring of any
            # of the child links, if they have a prefix in common, or if
            # matches any existing child of the node or not.
            remaining_key = key[len(prefix):]
            idx = bisect_left(node.children, PatriciaLink(remaining_key[:1], None))

            if idx in xrange(len(node.children)):
                common_prefix = commonprefix([node.children[idx].prefix, remaining_key])
            else:
                common_prefix = ''

            if common_prefix == remaining_key:
                new_node = self.__class__(
                    #start    = None,
                    #end      = None,
                    value    = value,
                    extra    = None,
                    children = (PatriciaLink(
                        prefix = node.children[idx].prefix[len(common_prefix):],
                        node   = node.children[idx].node),))
                node.children[idx].prefix = common_prefix
                node.children[idx].node   = new_node

            elif common_prefix:
                new_node = PatriciaNode(
                    #start    = None,
                    #end      = None,
                    value    = value,
                    extra    = None,
                    children = {})
                inner_node = PatriciaNode(
                    #start    = None,
                    #end      = None,
                    value    = None,
                    extra    = None,
                    children = {
                        remaining_key[len(common_prefix):]:
                            new_node,
                        node.children[idx].prefix[len(common_prefix):]:
                            node.children[idx].node})
                node.children[idx].prefix = common_prefix
                node.children[idx].node   = inner_node

            else:
                new_node = PatriciaNode(
                    #start    = None,
                    #end      = None,
                    value    = value,
                    extra    = None,
                    children = {})
                node.children.insert(idx, PatriciaLink(prefix=remaining_key, node=new_node))

            node.size += 1
            node.length += 1

        del node.hash
        self._propogate(node, path=path)

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

        path = list()
        prefix, node = self._get_by_key(key, path=path)

        if prefix != key or node.value is None:
            raise KeyError(key_)

        node.value = None
        node.size -= 1
        node.length -= 1
        del node.hash

        if path and not node.size:
            # Remove from parent
            node, idx, prefix = path.pop()
            del node.children[idx]
            del node.hash

        while all([path, len(node.children)==1, node.value is None]):
            # Squash with child node
            parent, idx, prefix = path.pop()
            parent.children[idx].prefix += node.children[0].prefix
            parent.children[idx].node    = node.children[0].node
            del parent.hash
            node = parent

        self._propogate(node, path=path)

    def delete(self, keys):
        """x.delete(E) -> None. Same as `for k in E: del x[k]`"""
        for key in keys:
            self._delete(key)

    def __delitem__(self, key):
        "x.__delitem__(y) <==> del x[y]"
        self.delete([key])

#
# End of File
#
