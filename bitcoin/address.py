# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import six
import numbers

from .serialize import serialize_hash, deserialize_hash
from .tools import StringIO

# ===----------------------------------------------------------------------===

from .base58 import VersionedPayload
from .destination import PubKeyHashId, ScriptHashId
from .errors import InvalidAddressError

class BitcoinAddress(VersionedPayload):
    PUBKEY_HASH = 0
    SCRIPT_HASH = 5

    def __new__(cls, hash=None, *args, **kwargs):
        if isinstance(hash, numbers.Integral):
            # hash160 is used for the standard bitcoin address formats, which
            # means a 20-byte hash.
            hash = serialize_hash(hash, 20)
            # The default version is SCRIPT_HASH, which is the future of bitcoin.
            kwargs.setdefault('version', cls.SCRIPT_HASH)
            # Returns an immutable value, an instance of Python's binary type:
            return super(BitcoinAddress, cls).__new__(cls, hash, *args, **kwargs)

        # The default version is SCRIPT_HASH (a BIP-0013 address), since this
        # is the future of bitcoin. It adds the absolute minimum size to the
        # UTXO set, and allows greater privacy.
        if 'payload' in kwargs:
            kwargs.setdefault('version', cls.SCRIPT_HASH)

        # Construct the address string, but be careful not to send multiple
        # values for the 'payload' parameter.
        if hash is None:
            address = super(BitcoinAddress, cls).__new__(cls, *args, **kwargs)
        else:
            address = super(BitcoinAddress, cls).__new__(cls, hash, *args, **kwargs)

        # Check that the created address is sensible. We restrict ourselves to
        # only the address types we know about even though that violates future-
        # proof pythonic duck typiing because (1) the type of address determines
        # the script, so we can't make scripts for address types we aren't aware
        # of, and (2) the bitcoin unit tests reject unknown address versions as
        # well.
        if len(address) != 25:
            raise InvalidAddressError(
                u"serialized address must be 25 bytes, not %d" % len(address))
        if address.version not in (cls.PUBKEY_HASH, cls.SCRIPT_HASH):
            raise InvalidAddressError(
                u"unrecognized address version: %x (%d)" % ((address.version,)*2))

        # Return the newly generated address:
        return address

    # Re-interpret the hash value from the serialized payload:
    @property
    def hash(self):
        return deserialize_hash(StringIO(self.payload), 20)

    @property
    def destination(self):
        # The original pay-to-pubkey-hash bitcoin address:
        if self.version == self.PUBKEY_HASH:
            return PubKeyHashId(hash=deserialize_hash(StringIO(self.payload), 20))
        # The new BIP-0016 pay-to-script-hash address:
        if self.version == self.SCRIPT_HASH:
            return ScriptHashId(hash=deserialize_hash(StringIO(self.payload), 20))
        # Any futue defined address format is not understood:
        raise InvalidAddressError(u"unknown address version: %s" % repr(self.version))

    def __nonzero__(self):
        "Returns true if the hash value is non-zero."
        # Use payload over hash because there's no need to incur deserialization
        # costs if we can compare directly:
        return self.payload != '\x00'*20

#
# End of File
#
