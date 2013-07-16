# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

from python_patterns.utils.decorators import Property

from .script import *

__all__ = [
    'BaseId',
    'HashId',
    'PubKeyId',
    'PubKeyHashId',
    'ScriptHashId',
]

# ===----------------------------------------------------------------------===

from .serialize import serialize_hash

class BaseId(object):
    @Property
    def script():
        """Returns a Script object representing a contract script portion of a
        payment to the destination."""
        def fget(self):
            # The script object is cached, since constructing it may involve
            # a number of string-manipulation operations.
            if getattr(self, '_script', None) is None:
                self._script = self._script__getter()
            return self._script
        def fdel(self):
            self._script = None
        return locals()

    # Scince script generation is deterministic and unique, two destinations
    # are equal if and only if they result in the same generated script.
    def __eq__(self, other):
        return self.script == other.script

class HashId(BaseId):
    """HashId is the base class for any destination type whose configurable
    parameter is a single hash value. See PubKeyHashId and ScriptHashId for
    two common cases."""
    def __init__(self, hash=0, *args, **kwargs):
        super(HashId, self).__init__(*args, **kwargs)
        self._hash = hash

    @Property
    def hash():
        def fget(self):
            return self._hash
        def fset(self, value):
            self._hash = value
            del self.hash_digest
            del self.script
        def fdel(self):
            self.hash = 0
        return locals()

    @Property
    def hash_digest():
        def fget(self):
            if getattr(self, '_hash_digest', None) is None:
                self._hash_digest = serialize_hash(self._hash, 20)
            return self._hash_digest
        def fdel(self):
            self._hash_digest = None
        return locals()

# ===----------------------------------------------------------------------===

class PubKeyId(BaseId):
    "Explicit public-key destination, as is used by default in coinbase outputs."
    __slots__ = ('_verifying_key', '_script')
    def __init__(self, verifying_key, *args, **kwargs):
        super(PubKeyId, self).__init__(*args, **kwargs)
        self.verifying_key = verifying_key

    @Property
    def verifying_key():
        def fget(self):
            return self._verifying_key
        def fset(self, value):
            if hasattr(value, 'get_verifying_key'):
                value = verifying_key.get_verifying_key()
            self._verifying_key = value
            del self.script
        return locals()

    def _script__getter(self):
        return Script([ScriptOp(data=self._verifying_key.serialize()),
                       ScriptOp(OP_CHECKSIG)])

class PubKeyHashId(HashId):
    """Destination for standard version=0 bitcoin addresses, which contain the
    hash160 of the public-key used to redeem them."""
    def _script__getter(self):
        return Script([ScriptOp(OP_DUP),
                       ScriptOp(OP_HASH160),
                       ScriptOp(data=self.hash_digest),
                       ScriptOp(OP_EQUALVERIFY),
                       ScriptOp(OP_CHECKSIG)])

class ScriptHashId(HashId):
    """Destination for version=5 BIP-0013 bitcoin addresses, which contain a
    hash of the contract script actually used to redeem it."""
    def _script__getter(self):
        return Script([ScriptOp(OP_HASH160),
                       ScriptOp(data=self.hash_digest),
                       ScriptOp(OP_EQUAL)])
#
# End of File
#
