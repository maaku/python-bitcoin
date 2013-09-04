# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import numbers
import six

from struct import unpack

from .base58 import VersionedPayload
from .errors import InvalidSecretError
from .mixins import SerializableMixin
from .serialize import serialize_beint, deserialize_beint
from .tools import StringIO

from .ecdsa__common import *

# Import as a different name so as to clearly distinguish from our ecdsa* modules
import ecdsa as pyecdsa

# Certicom secp256-k1, the ECDSA curve used by Bitcoin. This curve has recently
# been added to the python-ecdsa repository, but is still missing from the latest
# version on PyPI.
try:
    pyecdsa.curves.find_curve((1, 3, 132, 0, 10))
except pyecdsa.curves.UnknownCurveError:
    _a  = 0x0000000000000000000000000000000000000000000000000000000000000000L
    _b  = 0x0000000000000000000000000000000000000000000000000000000000000007L
    _p  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2FL
    _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798L
    _Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8L
    _r  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141L
    curve_secp256k1 = pyecdsa.ellipticcurve.CurveFp(_p, _a, _b)
    generator_secp256k1 = pyecdsa.ellipticcurve.Point(curve_secp256k1, _Gx, _Gy, _r)
    SECP256k1 = pyecdsa.curves.Curve('SECP256k1',
                                     curve_secp256k1,
                                     generator_secp256k1,
                                     (1, 3, 132, 0, 10))
    pyecdsa.curves.curves.append(SECP256k1)

# The Point class is only used in the creation of public keys and in the
# implementation of various ECDSA operations. Since all operations relevant to
# bitcoin are contained within this file, the Point class is not a properly
# specified API, and so for convenience we simply reuse the python-ecdsa Point
# class. Our only tweak is to use the SECP256k1 curve by default. INFINITY is
# a special-cased Point object.
from ecdsa.ellipticcurve import INFINITY
class Point(pyecdsa.ellipticcurve.Point):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('order', SECP256k1.order)
        super(Point, self).__init__(SECP256k1.curve, *args, **kwargs)

class Secret(VersionedPayload):
    # The only understood secret version has a prefix byte of 0x80 (128)
    SECP256K1_EXPONENT = 0x80

    def __new__(cls, exponent=None, compressed=None, *args, **kwargs):
        if isinstance(exponent, numbers.Integral):
            # The exponent is a random number within range(1, curve.order).
            # Using an exponent of zero would result in trivial-to-break
            # encryption, and as stupid as it sounds, it is a mistake that
            # can happen, so we check for it.
            exponent = exponent % SECP256k1.order
            if not exponent:
                raise InvalidSecretError(u"the secret exponent must be an integer x such "
                    u"that 1 <= x < 0x%x (received 0x%x)" % (SECP256k1.order, exponent))

            # The exponent is always stored as 32 bytes, even if some of the
            # leading bits are zero.
            exponent = serialize_beint(exponent, 32)

            # As a rather hackish extension of the Bitcoin secret format, a compressed
            # key is indicated by suffixing a '\x01' byte to the secret exponent. Note
            # that compression is a property of public keys, not private keys.
            if compressed is None or compressed:
                exponent += six.int2byte(1)

            kwargs.setdefault('version', cls.SECP256K1_EXPONENT)

            # Reuse VersionPayload's constructor:
            return super(Secret, cls).__new__(cls, exponent, *args, **kwargs)

        # At the time of this writing the only serialized secret format is what
        # we call SECP256K1_EXPONENT, a serialized exponent of the SECP256k1
        # curve, with an optional suffix indicating compression.
        if 'payload' in kwargs:
            kwargs.setdefault('version', cls.SECP256K1_EXPONENT)

        # The VersionedPayload superclass takes care of the details of
        # extracting (and validating) the version, payload, and checksum.
        # Other than the checksum, it is our responsibilty to make sure
        # that the internal fields make sense:
        if compressed is not None:
            raise InvalidSecretError(u"cannot specify compression when "
                u"constructing from an existing serialized secret")

        # The 'payload' parameter of VersionedPayload may be specified as
        # either a positional or keyword argument, or not at all. Since we
        # don't know, we run the risk of sending multiple values if we
        # blindly pass on exponent. If it's passed as a keyword, exponent
        # should be None (the default value for VersionedPayload as well),
        # so we use that fact to distinguish the two cases:
        if exponent is None:
            secret = super(Secret, cls).__new__(cls, *args, **kwargs)
        else:
            secret = super(Secret, cls).__new__(cls, exponent, *args, **kwargs)

        # Do some basic checks to make sure that what we received was actually
        # a valid serialized Secret.
        if len(secret) not in (37, 38):
            raise InvalidSecretError(u"serialized secret must be either 37 "
                u"(uncompressed) or 38 (compressed) bytes in length, not "
                u"%d" % len(secret))
        if secret[:1] != six.int2byte(128):
            raise InvalidSecretError(u"incorrect version for serialized secret; "
                u"expected 0x80 (128), not 0x%x (%d)" % ((ord(secret[:1]),)*2))
        if len(secret) == 38 and secret[33:34] != six.int2byte(1):
            raise InvalidSecretError(u"compression flag must be 0x01 (1), "
                u"not 0x%x (%d)" % ((ord(secret[33:34]),)*2))
        assert 1 <= secret.exponent < SECP256k1.order, (u"encoded exponent "
            u"must be an integer x such that 1 <= x < 0x%x" % SECP256k1.order)

        # Return the newly generated Secret
        return secret

    # The exponent is stored as a 256-bit big endian integer, the first field
    # of the payload:
    exponent = property(lambda self:deserialize_beint(StringIO(self.payload[:32]), 32))
    # A compressed key is requested by suffixing 0x01 to the payload field. Note
    # that the following comparison only returns true if payload is exactly 33
    # bytes in length and the final byte is '\x01'.
    compressed = property(lambda self:self.payload[32:] == six.int2byte(1))

from recordtype import recordtype
BaseSignature = recordtype('BaseSignature', 'r s'.split())

class Signature(SerializableMixin, BaseSignature):
    def serialize(self):
        def _serialize_sint(n):
            n_str = serialize_beint(n)
            if not n_str or n_str[:1] > six.int2byte(0x7f):
                n_str = six.int2byte(0) + n_str
            return n_str
        def _serialize_derint(n):
            n_str = _serialize_sint(n)
            return b''.join([
                six.int2byte(0x02),
                six.int2byte(len(n_str)),
                n_str,
            ])
        r_str = _serialize_derint(self.r)
        s_str = _serialize_derint(self.s)
        return b''.join([
            six.int2byte(0x30),
            six.int2byte(len(r_str + s_str)),
            r_str,
            s_str,
        ])
    @classmethod
    def deserialize(cls, file_):
        id_ = unpack('>B', file_.read(1))[0]
        assert id_ == 0x30, id_
        seq_len = unpack('>B', file_.read(1))[0]
        seq = file_.read(seq_len)
        id_, seq = unpack('>B', seq[:1])[0], seq[1:]
        assert id_ == 0x02, id_
        r_len, seq = unpack('>B', seq[:1])[0], seq[1:]
        r_str, seq = seq[:r_len], seq[r_len:]
        id_, seq = unpack('>B', seq[:1])[0], seq[1:]
        assert id_ == 0x02, id_
        s_len, seq = unpack('>B', seq[:1])[0], seq[1:]
        s_str = seq[:s_len]
        assert 2+r_len+2+s_len == seq_len, (2+r_len+2+s_len, seq_len)
        return cls(deserialize_beint(StringIO(r_str), len(r_str)),
                   deserialize_beint(StringIO(s_str), len(s_str)))

class CompactSignature(Signature):
    def __init__(self, v, r, s, *args, **kwargs):
        super(CompactSignature, self).__init__(r, s, *args, **kwargs)
        self.v = v

    def serialize(self):
        return b''.join([
            six.int2byte(self.v),
            serialize_beint(self.r, 32),
            serialize_beint(self.s, 32),
        ])
    @classmethod
    def deserialize(cls, file_):
        v = unpack('>B', file_.read(1))[0]
        r = deserialize_beint(file_, 32)
        s = deserialize_beint(file_, 32)
        return cls(v, r, s)

class SigningKey(object):
    def __init__(self, secret, *args, **kwargs):
        super(SigningKey, self).__init__(*args, **kwargs)
        self._ecdsa_signing_key = pyecdsa.SigningKey.from_secret_exponent(
            secret.exponent, curve=SECP256k1, hashfunc=hash256)
        self.compressed = secret.compressed

    @property
    def secret(self):
        cls = getattr(self, 'get_secret_class', lambda:
              getattr(self, 'secret_class', Secret))()
        return cls(self._ecdsa_signing_key.privkey.secret_multiplier,
                   compressed=self.compressed)

    # Private / signing keys can be serialized in two ways: using the industry standard DER/ASN.1 notation, or by recording the 
    def serialize(self):
        return self._ecdsa_signing_key.to_der()
    @classmethod
    def deserialize(cls, file_):
        id_ = unpack('>B', file_.read(1))[0]
        assert id_ == 0x30, id_
        seq_len = unpack('>B', file_.read(1))[0]
        seq = file_.read(seq_len)
        ecdsa_signing_key = pyecdsa.SigningKey.from_der(b''.join([
            six.int2byte(id_),
            six.int2byte(seq_len),
            seq]))
        obj = cls.__new__(cls)
        obj._ecdsa_signing_key = ecdsa_signing_key
        return obj

    def get_verifying_key(self):
        cls = getattr(self, 'get_verifying_key_class', lambda:
              getattr(self, 'verifying_key_class', VerifyingKey))()
        obj = cls.__new__(cls)
        obj._ecdsa_verifying_key = self._ecdsa_signing_key.verifying_key
        obj.compressed = self.compressed
        return obj

    def sign(self, digest, entropy=None):
        return Signature(*self._ecdsa_signing_key.sign_number(digest))

class VerifyingKey(object):
    def __init__(self, point, compressed=True, *args, **kwargs):
        super(VerifyingKey, self).__init__(*args, **kwargs)
        self._ecdsa_verifying_key = pyecdsa.VerifyingKey.from_public_point(
            point, curve=SECP256k1, hashfunc=hash256)
        self.compressed = compressed

    @property
    def point(self):
        return self._ecdsa_verifying_key.pubkey.point

    def serialize(self):
        point = self.point
        order = self._ecdsa_verifying_key.curve.generator.order()
        x_str = pyecdsa.util.number_to_string(point.x(), order)
        y_str = pyecdsa.util.number_to_string(point.y(), order)
        if self.compressed:
            return b''.join([six.int2byte(2 + (point.y() & 1)), x_str])
        else:
            return b''.join([six.int2byte(4), x_str, y_str])
    @classmethod
    def deserialize(cls, file_):
        id_ = unpack('>B', file_.read(1))[0]
        assert id_ in (0x02, 0x03, 0x04), id_
        x = pyecdsa.util.string_to_number(file_.read(SECP256k1.baselen))
        if id_ in (0x02, 0x03):
            compressed = True
            a = SECP256k1.curve.a()
            b = SECP256k1.curve.b()
            p = SECP256k1.curve.p()
            y = x * (x**2 + a) + b
            y = pyecdsa.numbertheory.square_root_mod_prime(y%p, p)
            if y&0x01 != id_&0x01:
                y = p - y
        else:
            compressed = False
            y = pyecdsa.util.string_to_number(file_.read(SECP256k1.baselen))
        return cls(Point(x,y), compressed=compressed)

    def verifies(self, signature, digest):
        return self._ecdsa_verifying_key.pubkey.verifies(digest, signature)

# ===----------------------------------------------------------------------===

from .crypto import hash256

#
# End of File
#
