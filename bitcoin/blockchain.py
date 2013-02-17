#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

from datetime import datetime, timedelta
from isodate import strftime
import numbers
from struct import pack, unpack

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from python_patterns.utils.decorators import Property

from .crypto import merkle
from .mixins import HashableMixin, SerializableMixin, ValidatesMixin
from .script import Script
from .serialize import (
    serialize_varchar, deserialize_varchar,
    serialize_hash, deserialize_hash,
    serialize_list, deserialize_list)
from .utils import target_from_compact

__all__ = [
    'OutPoint',
    'Input',
    'Output',
    'Transaction',
    'Merkle',
    'Block',
]

# ===----------------------------------------------------------------------===

class OutPoint(SerializableMixin, ValidatesMixin):
    def __init__(self, asset, hash=0, n=0xffffffff, *args, **kwargs):
        super(OutPoint, self).__init__(*args, **kwargs)
        self.asset = asset
        self.hash = hash
        self.n = n

    def serialize(self):
        result  = serialize_hash(self.hash, 32)
        result += pack('<I', self.n)
        return result
    @classmethod
    def deserialize(cls, asset, file_):
        initargs = {}
        initargs['hash'] = deserialize_hash(file_, 32)
        initargs['n'] = unpack('<I', file_.read(4))[0]
        return cls(asset, **initargs)

    def set_null(self):
        self.hash = 0
        self.n = 0xffffffff
    def is_null(self):
        return self.hash==0 and self.n==0xffffffff

    def validate(self, *args, **kwargs):
        if not isinstance(self.hash, numbers.Integral):
            raise self.ValidationError(
                u"invalid hash value in outpoint\n"
                u"    hash: %s" % repr(self.hash))
        if self.hash<0 or self.hash>=2**256:
            raise self.ValidationError(
                u"non-representable hash value in outpoint\n"
                u"    hash: %s" % repr(self.hash))
        if not isinstance(self.n, numbers.Integral):
            raise self.ValidationError(
                u"invalid numeric index in outpoint\n"
                u"    index: %s" % repr(self.n))
        if self.n<0 or self.n>=2**32:
            raise self.ValidationError(
                u"non-representable numeric index in outpoint\n"
                u"    index: %s" % repr(self.n))
        return super(OutPoint, self).validate(*args, **kwargs)

    def __eq__(self, other):
        return self.hash==other.hash and self.n==other.n
    def __repr__(self):
        return 'OutPoint(hash=%064x, n=%d)' % (
            self.hash,
            self.n==0xffffffff and -1 or self.n)

# ===----------------------------------------------------------------------===

class Input(SerializableMixin, ValidatesMixin):
    def __init__(self, asset, prevout=None, scriptSig=None,
                 nSequence=0xffffffff, *args, **kwargs):
        if prevout is None:
            prevout = self.deserialize_prevout(asset, StringIO('\x00'*32 + '\xff'*4))
        if scriptSig is None:
            scriptSig = kwargs.pop('coinbase', Script())
        super(Input, self).__init__(*args, **kwargs)
        self.asset = asset
        self.prevout = prevout
        self.scriptSig = scriptSig
        self.nSequence = nSequence

    def serialize(self):
        result  = self.prevout.serialize()
        if hasattr(self.scriptSig, 'serialize'):
            result += self.scriptSig.serialize()
        else:
            result += self.scriptSig # <-- coinbase
        result += pack('<I', self.nSequence)
        return result
    @staticmethod
    def deserialize_prevout(asset, file_):
        return OutPoint.deserialize(asset, file_)
    @classmethod
    def deserialize(cls, asset, file_):
        initargs = {}
        initargs['prevout'] = cls.deserialize_prevout(asset, file_)
        str_ = deserialize_varchar(file_)
        initargs['nSequence'] = unpack('<I', file_.read(4))[0]
        if initargs['prevout'].is_null() and initargs['nSequence']==0xffffffff:
            initargs['coinbase'] = str_ # <-- coinbase
        else:
            initargs['scriptSig'] = Script.deserialize(StringIO(str_))
        return cls(asset, **initargs)

    def validate(self, *args, **kwargs):
        self.prevout.validate()
        if isinstance(self.scriptSig, str):
            if not self.prevout.is_null():
                raise self.ValidationError(
                    u"non-null prevout combined with coinbase script is "
                    u"illegal: for non-coinbase inputs, make sure to "
                    u"deserialize the script\n"
                    u"    prevout:   %(prevout)s\n"
                    u"    scriptSig: %(scriptSig)s" % {
                        'prevout': repr(self.prevout),
                        'scriptSig': repr(self.scriptSig),
                    })
            len_ = len(self.scriptSig)
        else:
            self.scriptSig.validate()
            len_ = self.scriptSig.size
        if self.prevout.is_null():
            if len_ < 2:
                raise self.ValidationError(
                    u"coinbase script shorter than 2 bytes detected: "
                    u"coinbase script must be at least 2 bytes and no more "
                    u"than 100 bytes in length\n"
                    u"    scriptSig: %s" % repr(self.scriptSig))
            if len_ > 100:
                raise self.ValidationError(
                    u"coinbase script longer than 100 bytes detected: "
                    u"coinbase script must be at least 2 bytes and no more "
                    u"than 100 bytes in length\n"
                    u"    scriptSig: %s" % repr(self.scriptSig))
        if not isinstance(self.nSequence, numbers.Integral):
            raise self.ValidationError(
                u"invalid sequence number in input\n"
                u"    nSequence: %s" % repr(self.nSequence))
        if self.nSequence<0 or self.nSequence>=2**32:
            raise self.ValidationError(
                u"non-representable sequence number in input\n"
                u"    nSequence: %s" % repr(self.nSequence))
        return super(Input, self).validate(*args, **kwargs)

    def is_final(self):
        return self.nSequence==0xffffffff

    def __eq__(self, other):
        return (self.prevout   == other.prevout   and
                self.scriptSig == other.scriptSig and
                self.nSequence == other.nSequence)
    def __repr__(self):
        nSequence_str = (self.nSequence!=0xffffffff
            and ', nSequence=%d' % self.nSequence
             or '')
        return 'Input(prevout=%s, %s=%s%s)' % (
            repr(self.prevout),
            self.prevout.is_null() and 'coinbase' or 'scriptSig',
            repr(self.scriptSig),
            nSequence_str)

# ===----------------------------------------------------------------------===

class Output(SerializableMixin, ValidatesMixin):
    def __init__(self, asset, nValue=0, scriptPubKey=None, *args, **kwargs):
        if scriptPubKey is None:
            scriptPubKey = Script()
        super(Output, self).__init__(*args, **kwargs)
        self.asset = asset
        self.nValue = nValue
        self.scriptPubKey = scriptPubKey

    def serialize(self):
        result  = pack('<Q', self.nValue)
        result += self.scriptPubKey.serialize()
        return result
    @classmethod
    def deserialize(cls, asset, file_):
        initargs = {}
        initargs['nValue'] = unpack('<Q', file_.read(8))[0]
        initargs['scriptPubKey'] = Script.deserialize(StringIO(deserialize_varchar(file_)))
        return cls(asset, **initargs)

    def validate(self, *args, **kwargs):
        if not isinstance(self.nValue, numbers.Integral):
            raise self.ValidationError(
                u"invalid/non-representable output value\n"
                u"    nValue: %s" % repr(self.nValue))
        if self.nValue < 0:
            raise self.ValidationError(
                u"output underflow/negative value detected\n"
                u"    nValue: %s" % repr(self.nValue))
        if self.nValue > self.asset.max_value:
            raise self.ValidationError(
                u"output overflow/value exceeds asset's allowed range\n"
                u"    nValue: %s" % repr(self.nValue))
        self.scriptPubKey.validate()
        return super(Output, self).validate(*args, **kwargs)

    def __eq__(self, other):
        return (self.nValue == other.nValue and
            self.scriptPubKey == other.scriptPubKey)
    def __repr__(self):
        return 'Output(nValue=%d.%08d, scriptPubKey=%s)' % (
            self.nValue // 100000000,
            self.nValue % 100000000,
            repr(self.scriptPubKey))

# ===----------------------------------------------------------------------===

class Transaction(SerializableMixin, HashableMixin, ValidatesMixin):
    def __init__(self, asset, nVersion=1, vin=None, vout=None, nLockTime=0,
                 nRefHeight=0, *args, **kwargs):
        if vin is None: vin = []
        if vout is None: vout = []
        super(Transaction, self).__init__(*args, **kwargs)
        self.asset = asset
        self.nVersion = nVersion
        if not hasattr(self, 'vin'):
            self.vin_create()
        for tin in vin:
            self.vin_append(tin)
        if not hasattr(self, 'vout'):
            self.vout_create()
        for tout in vout:
            self.vout_append(tout)
        self.nLockTime = nLockTime
        self.nRefHeight = nRefHeight

    def vin_create(self):
        self.vin = []
    def vin_append(self, tin):
        self.vin.append(tin)
    def vin_count(self):
        return len(self.vin)
    def vin_index(self, idx):
        return self.vin[idx]
    vin_clear = vin_create

    def vout_create(self):
        self.vout = []
    def vout_append(self, tout):
        self.vout.append(tout)
    def vout_count(self):
        return len(self.vout)
    def vout_index(self, idx):
        return self.vout[idx]
    vout_clear = vout_create

    def serialize(self):
        if self.nVersion not in (1,2):
            raise NotImplementedError
        result  = pack('<I', self.nVersion)
        result += serialize_list(self.vin, lambda i:i.serialize())
        result += serialize_list(self.vout, lambda o:o.serialize())
        result += pack('<I', self.nLockTime)
        if self.nVersion==2:
            result += pack('<I', self.nRefHeight)
        return result
    @staticmethod
    def deserialize_input(asset, file_, *args, **kwargs):
        return Input.deserialize(asset, file_, *args, **kwargs)
    @staticmethod
    def deserialize_output(asset, file_, *args, **kwargs):
        return Output.deserialize(asset, file_, *args, **kwargs)
    @classmethod
    def deserialize(cls, asset, file_):
        initargs = {}
        initargs['nVersion'] = unpack('<I', file_.read(4))[0]
        if initargs['nVersion'] not in (1,2):
            raise NotImplementedError
        initargs['vin'] = list(deserialize_list(file_, lambda f:cls.deserialize_input(asset, f)))
        initargs['vout'] = list(deserialize_list(file_, lambda f:cls.deserialize_output(asset, f)))
        initargs['nLockTime'] = unpack('<I', file_.read(4))[0]
        if initargs['nVersion']==2:
            initargs['nRefHeight'] = unpack('<I', file_.read(4))[0]
        else:
            initargs['nRefHeight'] = 0
        return cls(asset, **initargs)

    def is_final(self, block_height=None, block_time=None):
        #if self.nLockTime < LOCKTIME_THRESHOLD:
        #    if block_height is None:
        #        pass # FIXME: nBlockHeight = nBestHeight
        #    if self.nLockTime < block_height:
        #        return False
        #else:
        #    if block_time is None:
        #        pass # FIXME: nBlockTime = GetAdjustedTime()
        #    if self.nLockTime < block_time:
        #        return False
        for txin in self.vin:
            if not txin.is_final():
                return False
        return True

    def is_newer_than(self, other):
        vin_count = self.vin_count()
        if vin_count != other.vin_count():
            return False
        # FIXME: this could be made more pythonic...
        newer = False
        lowest = 0xffffffff
        for idx in xrange(vin_count):
            self_vin = self.vin_index(idx)
            other_vin = other.vin_index(idx)
            if self_vin.prevout != other_vin.prevout:
                return False
            if self_vin.nSequence != other_vin.nSequence:
                if self_vin.nSequence <= lowest:
                    newer = False
                    lowest = self_vin.nSequence
                if other_vin.nSequence < lowest:
                    newer = True
                    lowest = other_vin.nSequence
        return newer

    def is_coinbase(self):
        return self.vin_count()==1 and self.vin_index(0).prevout.is_null()

    def is_standard(self):
        if self.nVersion not in (1,2):
            return False

    def validate(self, *args, **kwargs):
        allowed_versions = set([1])
        # if TXVERSION2_REFHEIGHT in self.asset.features:
        #     if allowed_versions.add(2)
        if self.nVersion not in allowed_versions:
            raise self.ValidationError(
                u"unrecognized transaction version\n"
                u"    nVersion: %s" % repr(self.nVersion))

        if self.vin_count() <= 0:
            raise self.ValidationError(
                u"input vector empty: every transaction must have at least "
                u"one input")
        for idx, txin in enumerate(self.vin):
            if txin is None:
                raise self.ValidationError(
                    u"transaction input missing at index %d: pruned "
                    u"transactions cannot be validated" % idx)
            txin.validate()
        if self.is_coinbase():
            coinbase = self.vin_index(0)
            if not coinbase.prevout.is_null():
                raise self.ValidationError(
                    u"coinbase input non-null: first input of a coinbase "
                    u"transaction must be null")
            start = 1
        else:
            start = 0
        if start != self.vin_count():
            if any(self.vin_index(idx).prevout.is_null()
                   for idx in xrange(start, self.vin_count())):
                raise self.ValidationError(
                    u"unexpected null input encountered: only the first "
                    u"input of a coinbase transaction is allowed to be null; "
                    u"it is illegal to have a null value for subsequent "
                    u"inputs or any input of a non-coinbase transaction")
        if self.vout_count() <= 0:
            raise self.ValidationError(
                u"output vector empty: every transaction must have at least "
                u"one output")
        for idx, txout in enumerate(self.vout):
            if txout is None:
                raise self.ValidationError(
                    u"transaction output missing at index %d: pruned "
                    u"transactions cannot be validated" % idx)
            txout.validate()

        if not isinstance(self.nLockTime, numbers.Integral):
            raise self.ValidationError(
                u"invalid lock time\n"
                u"    nLockTime: %s" %
                repr(self.nLockTime))
        if self.nLockTime<0 or self.nLockTime>=2**32:
            raise self.ValidationError(
                u"non-representable lock time\n"
                u"    nLockTime: %s" %
                repr(self.nLockTime))

        if self.nVersion in (2,):
            if not isinstance(self.nRefHeight, numbers.Integral):
                raise self.ValidationError(
                    u"invalid reference height\n"
                    u"    nRefHeight: %s" %
                    repr(self.nRefHeight))
            if self.nRefHeight<0 or self.nRefHeight>=2**32:
                raise self.ValidationError(
                    u"non-representable reference height\n"
                    u"    nRefHeight: %s" %
                    repr(self.nRefHeight))
        else:
            if self.nRefHeight != 0:
                raise self.ValidationError(
                    u"reference height must be zero if nVersion=%(nVersion_raw)d\n"
                    u"    nRefHeight: %(nRefHeight)s" % {
                        'nVersion_raw': self.nVersion,
                        'nRefHeight': repr(self.nRefHeight),
                    })

        if self.size > self.asset.max_block_length:
            raise self.ValidationError(
                u"transaction exceeds maximum block length\n"
                u"    size: %d.%03dkB" % (
                    self.size // 1000,
                    self.size  % 1000))

        outpoints = set()
        for txin in self.vin:
            if txin.prevout in outpoints:
                raise self.ValidationError(
                    u"duplicate input detected\n"
                    u"    prevout: %s" % repr(txin.prevout))
            outpoints.add(txin.prevout)

        return super(Transaction, self).validate(*args, **kwargs)

    def __eq__(self, other):
        if (self.nVersion   != other.nVersion  or
            self.nLockTime  != other.nLockTime or
            self.nRefHeight != other.nRefHeight):
            return False
        if list(self.vin) != list(other.vin):
            return False
        if list(self.vout) != list(other.vout):
            return False
        return True
    def __repr__(self):
        nRefHeight_str = (self.nVersion==2
            and ', nRefHeight=%d' % self.nRefHeight
             or '')
        return ('Transaction(nVersion=%d, '
                            'vin=%s, '
                            'vout=%s, '
                            'nLockTime=%d%s)' % (
            self.nVersion,
            repr(self.vin),
            repr(self.vout),
            self.nLockTime,
            nRefHeight_str))

# ===----------------------------------------------------------------------===

class Merkle(SerializableMixin, HashableMixin):
    def __init__(self, asset, children=None, *args, **kwargs):
        if children is None: children = []
        super(Merkle, self).__init__(*args, **kwargs)
        self.asset = asset
        if not hasattr(self, 'children'):
            self.children_create()
        for child in children:
            if hasattr(child, 'hash'):
                child = child.hash
            self.children_append(child)

    def children_create(self):
        self.children = []
    def children_append(self, tx):
        self.children.append(tx)
    def children_count(self):
        return len(self.children)
    def children_index(self, idx):
        return self.children[idx]
    children_clear = children_create

    def serialize(self):
        # detect version=2 (explicit) merkle trees
        if any(lambda h:not isinstance(h, numbers.Integral), self.children):
            raise NotImplementedError
        return serialize_list(self.children, lambda x:serialize_hash(x, 32))
    @classmethod
    def deserialize(cls, asset, file_):
        return cls(deserialize_list(file_, lambda x:deserialize_hash(x, 32)))

    def __eq__(self, other):
        return map(merkle, self.children) == map(merkle, other.children)
    def __repr__(self):
        return ''.join(['Merkle([', ', '.join(map(repr, self.children)), '])'])

# ===----------------------------------------------------------------------===

class Block(SerializableMixin, HashableMixin, ValidatesMixin):
    def __init__(self, asset, nVersion=1, hashPrevBlock=0, hashMerkleRoot=None,
                 nTime=0, nBits=0x1d00ffff, nNonce=0, vtx=None, *args, **kwargs):
        if vtx is None: vtx = []
        super(Block, self).__init__(*args, **kwargs)

        # serialized, header
        self.nVersion = nVersion
        self.hashPrevBlock = hashPrevBlock
        self.hashMerkleRoot = hashMerkleRoot
        self.nTime = nTime
        self.nBits = nBits
        self.nNonce = nNonce

        # serialized, transactions
        if not hasattr(self, 'vtx'):
            self.vtx_create()
        for tx in vtx:
            self.vtx_add(tx)

    def vtx_create(self):
        self.vtx = set()
    def vtx_add(self, tx):
        self.vtx.add(tx)
    def vtx_count(self):
        return len(self.vtx)
    def vtx_clear(self):
        self.vtx.clear()

    def serialize(self, mode=None):
        if mode is None:
            mode = 'header'
        if mode not in ('full', 'header'):
            raise ValueError(u"unrecognized block serialization mode")
        if self.nVersion not in (1,2):
            raise NotImplementedError
        result  = pack('<I', self.nVersion)
        result += serialize_hash(self.hashPrevBlock, 32)
        result += serialize_hash(self.hashMerkleRoot, 32)
        result += pack('<I', self.nTime)
        result += pack('<I', self.nBits)
        result += pack('<I', self.nNonce)
        if mode in ('header',):
            return result
        result += serialize_list(self.vtx, lambda t:t.serialize())
        return result
    def __bytes__(self):
        return self.serialize(mode='header')
    @staticmethod
    def deserialize_transaction(asset, file_, *args, **kwargs):
        return Transaction.deserialize(asset, file_, *args, **kwargs)
    @classmethod
    def deserialize(cls, asset, file_, mode=None):
        if mode is None:
            mode = 'header'
        if mode not in ('full', 'header'):
            raise ValueError(u"unrecognized block serialization mode")
        initargs = {}
        initargs['nVersion'] = unpack('<I', file_.read(4))[0]
        if initargs['nVersion'] not in (1,2):
            raise NotImplementedError
        initargs['hashPrevBlock'] = deserialize_hash(file_, 32)
        initargs['hashMerkleRoot'] = deserialize_hash(file_, 32)
        initargs['nTime'] = unpack('<I', file_.read(4))[0]
        initargs['nBits'] = unpack('<I', file_.read(4))[0]
        initargs['nNonce'] = unpack('<I', file_.read(4))[0]
        if mode in ('header',):
            return cls(asset, **initargs)
        initargs['vtx'] = list(deserialize_list(file_, lambda f:cls.deserialize_transaction(asset, f)))
        return cls(asset, **initargs)

    def validate(self, *args, **kwargs):
        allowed_versions = set([1])
        # if BIP0032_BLOCKVERSION2 in self.asset.features:
        #     if allowed_versions.add(2)
        if self.nVersion not in allowed_versions:
            raise self.ValidationError(
                u"unrecognized block version\n"
                u"    nVersion: %s" % repr(self.nVersion))
        if not isinstance(self.hashPrevBlock, numbers.Integral):
            raise self.ValidationError(
                u"invalid hash value for prevBlock\n"
                u"    hashPrevBlock: %s" % repr(self.hashPrevBlock))
        if self.hashPrevBlock<0 or self.hashPrevBlock>=2**256:
            raise self.ValidationError(
                u"non-representable hash value for prevBlock\n"
                u"    hashPrevBlock: %s" % repr(self.hashPrevBlock))
        if not isinstance(self.hashMerkleRoot, numbers.Integral):
            raise self.ValidationError(
                u"invalid hash value for merkleRoot\n"
                u"    hashMerkleRoot: %s" % repr(self.hashMerkleRoot))
        if self.hashMerkleRoot<0 or self.hashMerkleRoot>=2**256:
            raise self.ValidationError(
                u"non-representable hash value for merkleRoot\n"
                u"    hashMerkleRoot: %s" % repr(self.hashMerkleRoot))
        if not isinstance(self.nTime, numbers.Integral):
            raise self.ValidationError(
                u"invalid timestamp value\n"
                u"    nTime: %s" % repr(self.nTime))
        if self.nTime<0 or self.nTime>=2**32:
            raise self.ValidationError(
                u"non-representable timestamp value\n"
                u"    nTime: %s" % repr(self.nTime))
        # FIXME: replace datetime.now() with network-adjusted time, and then
        #     eventually a hybrid NTP/network-adjusted time.
        allowed_drift = timedelta(seconds=7200)
        maximum_timestamp = datetime.now() + maximum_future_drift
        if datetime.utcfromtimestamp(self.nTime) > maximum_timestamp:
            raise self.ValidationError(
                u"timestamp exceeds network-adjusted time by more than the "
                u"maximum allowed drift of %(allowed_drift)s\n"
                u"    nTime > %(maximum_timestamp)s" % {
                    'allowed_drift': strftime(allowed_drift, "%P"),
                    'maximum_timestamp': maximum_timestamp.isoformat()[:19],
                })
        if not isinstance(self.nBits, numbers.Integeral):
            raise self.ValidationError(
                u"invalid target/nBits value\n"
                u"    nBits: %s" % repr(self.nBits))
        if self.nBits<0 or self.nBits>=2**32:
            raise self.ValidationError(
                u"non-representable target/nBits value\n"
                u"    nBits: %s" % repr(self.nBits))
        target = target_from_compact(self.nBits)
        maximum_target = target_from_compact(0x1d00ffff)
        if target<=0 or target>maximum_target:
            raise self.ValidationError(
                u"target/nBits outside of allowed range\n"
                u"    nBits:        0x%(nBits_raw)08x\n"
                u"    target:       %(target)s"
                u"    target (hex): 0x%(target_raw)064x"
                u"    target (max): 0x%(target_max)064x"
                u"    target (min): 0x%(target_min)064x" % {
                    'nBits_raw': self.nBits,
                    'target': repr(target),
                    'target_raw': target,
                    'target_max': maximum_target,
                    'target_min': 1L,
                })
        if not isinstance(self.nNonce, numbers.Integral):
            raise self.ValidationError(
                u"invalid nonce\n"
                u"    nNonce: %s" % repr(self.nNonce))
        if self.nNonce<0 or self.nNonce>=2**32:
            raise self.ValidationError(
                u"non-representable nonce\n"
                u"    nNonce: %s" % repr(self.nNonce))

        hash_ = self.hash
        if hash_ > target:
            raise self.ValidationError(
                u"hash does not meet target threshold\n"
                u"    hash:   %(hash)064x\n"
                u"    target: %(target)064x\n" % {
                    'hash': hash_,
                    'target': target,
                })

        return super(Block, self).validate(*args, **kwargs)

    def __eq__(self, other):
        if (self.nVersion       != other.nVersion       or
            self.hashPrevBlock  != other.hashPrevBlock  or
            self.hashMerkleRoot != other.hashMerkleRoot or
            self.nTime          != other.nTime          or
            self.nBits          != other.nBits          or
            self.nNonce         != other.nNonce):
            return False
        return True
    def __repr__(self):
        return ('Block(nVersion=%d, '
                      'hashPrevBlock=0x%064x, '
                      'hashMerkleRoot=0x%064x, '
                      'nTime=%s, '
                      'nBits=0x%08x, '
                      'nNonce=0x%08x, '
                      'vtx=%s)' % (
            self.nVersion,
            self.hashPrevBlock,
            self.hashMerkleRoot,
            self.nTime,
            self.nBits,
            self.nNonce,
            repr(self.vtx)))

# End of File
#
