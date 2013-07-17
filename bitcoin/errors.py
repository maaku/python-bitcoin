# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

class Base58Error(Exception):
    "An error related to base58 encoding/decoding."
    pass

class InvalidBase58Error(Base58Error):
    "Base58 string cannot be properly decoded."
    pass

class HashChecksumError(Base58Error):
    "Checksum doesn't match data for base58 string."
    pass

class VersionedPayloadError(Base58Error):
    "Invalid versioned payload string."
    pass

class BaseSerializationError(Exception):
    "An error related to parsing serialization formats."
    pass

class InvalidAddressError(BaseSerializationError):
    "Unrecognized / invalid format for Bitcoin address."
    pass

class InvalidSecretError(BaseSerializationError):
    "Unrecognized / invalid format for ECDSA secret."
    pass

class ValidationError(Exception):
    "An error while validating data."
    pass

#
# End of File
#
