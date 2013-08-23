# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

__all__ = [
    'SerializableMixin',
    'HashableMixin',
]

# ===----------------------------------------------------------------------===

from types import MethodType

class SerializableMixin(object):
    def __init__(self, *args, **kwargs):
        super(SerializableMixin, self).__init__(*args, **kwargs)
        self.deserialize = MethodType(self.deserialize, self, self.__class__)

    def __bytes__(self, *args, **kwargs):
        return self.serialize(*args, **kwargs)

# ===----------------------------------------------------------------------===

class HashableMixin(object):
    """Provides a single property to the inheriting subclass, `hash`, as well
    as hooks to enable caching of the hash value using the storage backend of
    the object relational mapper. By default, the `_hash` attribute is used to
    store cached hash values."""
    from .crypto import hash256 as compressor

    def hash__getter(self, *args, **kwargs):
        # Cryptographic hashes are expensive, so `hash` is only recomputed if
        # the binary representation has changed or if no cached value exists.
        # When such an event occurs that could change the objects hash value
        # `_hash`, the underlying column, set to `None` so that it will be
        # recomputed on next access.
        if getattr(self, '_hash', None) is not None:
            return self._hash
        # Hash can't be computed without a compressor object:
        compressor = self.compressor
        if compressor is None:
            return None
        # Hash doesn't exist or has been set to `None` (indicating a need to
        # recompute). So calculate the new hash value, and cache it for future
        # access:
        value = compressor.new(self.__bytes__(*args, **kwargs)).intdigest()
        self.hash__setter(value)
        # Return the newly computed hash to the caller.
        return value

    def hash__setter(self, value):
        self._hash = value

    def hash__deleter(self):
        # As a convenient shortcut, other methods can indicate the hash needs
        # to be recomputed with a simple `del block.hash`:
        self.hash__setter(None)

    @property
    def hash(self):
        """The hash value is changed whenever the binary representation of the
        block changes, and is recomputed as necessary. This is accomplished
        efficiently by having `hash` be recomputed on access, if necessary,
        and the result cached."""
        return self.hash__getter()
    @hash.deleter
    def hash(self):
        self.hash__deleter()

#
# End of File
#
