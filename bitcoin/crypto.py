# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

__all__ = [
    'hash160',
    'hash256',
    'SECP256k1',
    'Secret',
    'InvalidSecretError',
    'Signature',
    'CompactSignature',
    'SigningKey',
    'VerifyingKey'
]

from .hash import hash160, hash256

from .errors import InvalidSecretError

try:
    from .ecdsa_openssl import (
        SECP256k1, Secret,
        Signature, CompactSignature,
        SigningKey, VerifyingKey)
except:
    from .ecdsa_generic import (
        SECP256k1, Secret,
        Signature, CompactSignature,
        SigningKey, VerifyingKey)

# End of File
