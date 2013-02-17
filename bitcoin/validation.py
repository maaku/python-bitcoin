#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

__all__ = [
    'BaseValidator',
    'BasicValidator',
]

# ===----------------------------------------------------------------------===

class BaseValidator(object):
    # `ValidationError` is raised by `validate()` if the object does not pass
    # validation.
    from .errors import ValidationError

    def validate(self, obj):
        """The terminal `validate()` method. Takes no arguments and simply
        returns (so that subclasses can safely call `super.validate()` under
        any circumstance)."""
        return

# ===----------------------------------------------------------------------===

class BasicValidator(BaseValidator):
    def validate(self, obj, *args, **kwargs):
        if isinstance(obj, OutPoint):
            if not isinstance(obj.hash, numbers.Integral):
                raise self.ValidationError(
                    u"invalid hash value in outpoint\n"
                    u"    hash: %s" % repr(obj.hash))
            if obj.hash<0 or obj.hash>=2**256:
                raise self.ValidationError(
                    u"non-representable hash value in outpoint\n"
                    u"    hash: %s" % repr(obj.hash))
            if not isinstance(obj.n, numbers.Integral):
                raise self.ValidationError(
                    u"invalid numeric index in outpoint\n"
                    u"    index: %s" % repr(obj.n))
            if obj.n<0 or obj.n>=2**32:
                raise self.ValidationError(
                    u"non-representable numeric index in outpoint\n"
                    u"    index: %s" % repr(obj.n))

        if isinstance(obj, Input):
            self.validate(obj.prevout, *args, **kwargs)
            if isinstance(obj.scriptSig, str):
                if not obj.prevout.is_null():
                    raise self.ValidationError(
                        u"non-null prevout combined with coinbase script is "
                        u"illegal: for non-coinbase inputs, make sure to "
                        u"deserialize the script\n"
                        u"    prevout:   %(prevout)s\n"
                        u"    scriptSig: %(scriptSig)s" % {
                            'prevout': repr(obj.prevout),
                            'scriptSig': repr(obj.scriptSig),
                        })
                len_ = len(obj.scriptSig)
            else:
                self.validate(obj.scriptSig, *args, **kwargs)
                len_ = obj.scriptSig.size
            if obj.prevout.is_null():
                if len_ < 2:
                    raise self.ValidationError(
                        u"coinbase script shorter than 2 bytes detected: "
                        u"coinbase script must be at least 2 bytes and no "
                        u"more than 100 bytes in length\n"
                        u"    scriptSig: %s" % repr(obj.scriptSig))
                if len_ > 100:
                    raise self.ValidationError(
                        u"coinbase script longer than 100 bytes detected: "
                        u"coinbase script must be at least 2 bytes and no "
                        u"more than 100 bytes in length\n"
                        u"    scriptSig: %s" % repr(obj.scriptSig))
            if not isinstance(obj.nSequence, numbers.Integral):
                raise self.ValidationError(
                    u"invalid sequence number in input\n"
                    u"    nSequence: %s" % repr(obj.nSequence))
            if obj.nSequence<0 or obj.nSequence>=2**32:
                raise self.ValidationError(
                    u"non-representable sequence number in input\n"
                    u"    nSequence: %s" % repr(obj.nSequence))

        if isinstance(obj, Output):
            if not isinstance(obj.nValue, numbers.Integral):
                raise self.ValidationError(
                    u"invalid/non-representable output value\n"
                    u"    nValue: %s" % repr(obj.nValue))
            if obj.nValue < 0:
                raise self.ValidationError(
                    u"output underflow/negative value detected\n"
                    u"    nValue: %s" % repr(obj.nValue))
            if obj.nValue > obj.asset.max_value:
                raise self.ValidationError(
                    u"output overflow/value exceeds asset's allowed range\n"
                    u"    nValue: %s" % repr(obj.nValue))
            self.validate(obj.scriptPubKey, *args, **kwargs)

        if isinstance(obj, Transaction):
            allowed_versions = set([1])
            # if TXVERSION2_REFHEIGHT in obj.asset.features:
            #     if allowed_versions.add(2)
            if obj.nVersion not in allowed_versions:
                raise self.ValidationError(
                    u"unrecognized transaction version\n"
                    u"    nVersion: %s" % repr(obj.nVersion))
            if not len(obj.vin):
                raise self.ValidationError(
                    u"input vector empty: every transaction must have at "
                    u"least one input")
            for idx, txin in enumerate(obj.vin):
                if txin is None:
                    raise self.ValidationError(
                        u"transaction input missing at index %d: pruned "
                        u"transactions cannot be validated" % idx)
                self.validate(txin)
            if obj.is_coinbase():
                coinbase = obj.vin[0]
                if not coinbase.prevout.is_null():
                    raise self.ValidationError(
                        u"coinbase input non-null: first input of a coinbase "
                        u"transaction must be null")
                start = 1
            else:
                start = 0
            if start != len(obj.vin):
                if any(obj.vin[idx].prevout.is_null()
                       for idx in xrange(start, len(obj.vin))):
                    raise self.ValidationError(
                        u"unexpected null input encountered: only the first "
                        u"input of a coinbase transaction is allowed to be "
                        u"null; it is illegal to have a null value for "
                        u"subsequent inputs or any input of a non-coinbase "
                        u"transaction")
            if not len(obj.vout):
                raise self.ValidationError(
                    u"output vector empty: every transaction must have at "
                    u"least one output")
            for idx, txout in enumerate(obj.vout):
                if txout is None:
                    raise self.ValidationError(
                        u"transaction output missing at index %d: pruned "
                        u"transactions cannot be validated" % idx)
                self.validate(txout)
            if not isinstance(obj.nLockTime, numbers.Integral):
                raise obj.ValidationError(
                    u"invalid lock time\n"
                    u"    nLockTime: %s" %
                    repr(obj.nLockTime))
            if obj.nLockTime<0 or obj.nLockTime>=2**32:
                raise self.ValidationError(
                    u"non-representable lock time\n"
                    u"    nLockTime: %s" %
                    repr(obj.nLockTime))
            if obj.nVersion in (2,):
                if not isinstance(obj.nRefHeight, numbers.Integral):
                    raise self.ValidationError(
                        u"invalid reference height\n"
                        u"    nRefHeight: %s" %
                        repr(obj.nRefHeight))
                if obj.nRefHeight<0 or obj.nRefHeight>=2**32:
                    raise self.ValidationError(
                        u"non-representable reference height\n"
                        u"    nRefHeight: %s" %
                        repr(obj.nRefHeight))
            else:
                if obj.nRefHeight != 0:
                    raise self.ValidationError(
                        u"reference height must be zero if nVersion=%(nVersion_raw)d\n"
                        u"    nRefHeight: %(nRefHeight)s" % {
                            'nVersion_raw': obj.nVersion,
                            'nRefHeight': repr(obj.nRefHeight),
                        })
            if obj.size > obj.asset.max_block_length:
                raise self.ValidationError(
                    u"transaction exceeds maximum block length\n"
                    u"    size: %d.%03dkB" % (
                        obj.size // 1000,
                        obj.size  % 1000))
            outpoints = set()
            for txin in obj.vin:
                if txin.prevout in outpoints:
                    raise self.ValidationError(
                        u"duplicate input detected\n"
                        u"    prevout: %s" % repr(txin.prevout))
                outpoints.add(txin.prevout)

        if isinstance(obj, Block):
            allowed_versions = set([1])
            # if BIP0032_BLOCKVERSION2 in self.asset.features:
            #     allowed_versions.add(2)
            if obj.nVersion not in allowed_versions:
                raise self.ValidationError(
                    u"unrecognized block version\n"
                    u"    nVersion: %s" % repr(obj.nVersion))
            if not isinstance(obj.hashPrevBlock, numbers.Integral):
                raise self.ValidationError(
                    u"invalid hash value for prevBlock\n"
                    u"    hashPrevBlock: %s" % repr(obj.hashPrevBlock))
            if obj.hashPrevBlock<0 or obj.hashPrevBlock>=2**256:
                raise self.ValidationError(
                    u"non-representable hash value for prevBlock\n"
                    u"    hashPrevBlock: %s" % repr(obj.hashPrevBlock))
            if not isinstance(obj.hashMerkleRoot, numbers.Integral):
                raise self.ValidationError(
                    u"invalid hash value for merkleRoot\n"
                    u"    hashMerkleRoot: %s" % repr(obj.hashMerkleRoot))
            if obj.hashMerkleRoot<0 or obj.hashMerkleRoot>=2**256:
                raise self.ValidationError(
                    u"non-representable hash value for merkleRoot\n"
                    u"    hashMerkleRoot: %s" % repr(obj.hashMerkleRoot))
            if not isinstance(obj.nTime, numbers.Integral):
                raise self.ValidationError(
                    u"invalid timestamp value\n"
                    u"    nTime: %s" % repr(obj.nTime))
            if obj.nTime<0 or obj.nTime>=2**32:
                raise self.ValidationError(
                    u"non-representable timestamp value\n"
                    u"    nTime: %s" % repr(obj.nTime))
            # FIXME: replace datetime.now() with network-adjusted time, and then
            #     eventually a hybrid NTP/network-adjusted time.
            allowed_drift = timedelta(seconds=7200)
            maximum_timestamp = datetime.now() + allowed_drift
            if datetime.utcfromtimestamp(obj.nTime) > maximum_timestamp:
                raise self.ValidationError(
                    u"timestamp exceeds network-adjusted time by more than the "
                    u"maximum allowed drift of %(allowed_drift)s\n"
                    u"    nTime > %(maximum_timestamp)s" % {
                        'allowed_drift': strftime(allowed_drift, "%P"),
                        'maximum_timestamp': maximum_timestamp.isoformat()[:19],
                    })
            if not isinstance(obj.nBits, numbers.Integral):
                raise self.ValidationError(
                    u"invalid target/nBits value\n"
                    u"    nBits: %s" % repr(obj.nBits))
            if obj.nBits<0 or obj.nBits>=2**32:
                raise self.ValidationError(
                    u"non-representable target/nBits value\n"
                    u"    nBits: %s" % repr(obj.nBits))
            target = target_from_compact(obj.nBits)
            if target>obj.asset.maximum_target:
                raise self.ValidationError(
                    u"target/nBits outside of allowed range\n"
                    u"    nBits:        0x%(nBits_raw)08x\n"
                    u"    target:       %(target)s"
                    u"    target (hex): 0x%(target_raw)064x"
                    u"    target (max): 0x%(target_max)064x" % {
                        'nBits_raw': obj.nBits,
                        'target': repr(target),
                        'target_raw': target,
                        'target_max': obj.asset.maximum_target,
                    })
            if not isinstance(obj.nNonce, numbers.Integral):
                raise self.ValidationError(
                    u"invalid nonce\n"
                    u"    nNonce: %s" % repr(obj.nNonce))
            if obj.nNonce<0 or obj.nNonce>=2**32:
                raise self.ValidationError(
                    u"non-representable nonce\n"
                    u"    nNonce: %s" % repr(obj.nNonce))
            hash_ = obj.hash
            if hash_ > target:
                raise self.ValidationError(
                    u"hash does not meet target threshold\n"
                    u"    hash:   %(hash)064x\n"
                    u"    target: %(target)064x\n" % {
                        'hash': hash_,
                        'target': target,
                    })

        return super(BasicValidator, self).validate(obj, *args, **kwargs)

#
# End of File
#
