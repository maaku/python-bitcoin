# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

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
    @property
    def script(self):
        """Returns a Script object representing a contract script portion of a
        payment to the destination."""
        # The script object is cached, since constructing it may involve
        # a number of string-manipulation operations.
        if getattr(self, '_script', None) is None:
            self._script = self._script__getter()
        return self._script

    @script.deleter
    def script(self):
        self._script = None

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

    @property
    def hash(self):
        return self._hash
    @hash.setter
    def hash(self, value):
        self._hash = value
        del self.hash_digest
        del self.script
    @hash.deleter
    def hash(self):
        self.hash = 0

    @property
    def hash_digest(self):
        if getattr(self, '_hash_digest', None) is None:
            self._hash_digest = serialize_hash(self._hash, 20)
        return self._hash_digest
    @hash_digest.deleter
    def hash_digest(self):
        self._hash_digest = None

# ===----------------------------------------------------------------------===

class PubKeyId(BaseId):
    "Explicit public-key destination, as is used by default in coinbase outputs."
    __slots__ = ('_verifying_key', '_script')
    def __init__(self, verifying_key, *args, **kwargs):
        super(PubKeyId, self).__init__(*args, **kwargs)
        self.verifying_key = verifying_key

    @property
    def verifying_key(self):
        return self._verifying_key
    @verifying_key.setter
    def verifying_key(self, value):
        if hasattr(value, 'get_verifying_key'):
            value = verifying_key.get_verifying_key()
        self._verifying_key = value
        del self.script

    def _script__getter(self):
        return Script().join([
            ScriptOp(data=self._verifying_key.serialize()),
            ScriptOp(OP_CHECKSIG)])

class PubKeyHashId(HashId):
    """Destination for standard version=0 bitcoin addresses, which contain the
    hash160 of the public-key used to redeem them."""
    def _script__getter(self):
        return Script().join([
            ScriptOp(OP_DUP),
            ScriptOp(OP_HASH160),
            ScriptOp(data=self.hash_digest),
            ScriptOp(OP_EQUALVERIFY),
            ScriptOp(OP_CHECKSIG)])

class ScriptHashId(HashId):
    """Destination for version=5 BIP-0013 bitcoin addresses, which contain a
    hash of the contract script actually used to redeem it."""
    def _script__getter(self):
        return Script().join([
            ScriptOp(OP_HASH160),
            ScriptOp(data=self.hash_digest),
            ScriptOp(OP_EQUAL)])
#
# End of File
#
