#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === bitcoin.blockchain --------------------------------------------------===
# Copyright © 2012, RokuSigma Inc. and contributors as an unpublished work.
# See AUTHORS for details.
#
# RokuSigma Inc. (the “Company”) Confidential
#
# NOTICE: All information contained herein is, and remains the property of the
# Company. The intellectual and technical concepts contained herein are
# proprietary to the Company and may be covered by U.S. and Foreign Patents,
# patents in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from the
# Company. Access to the source code contained herein is hereby forbidden to
# anyone except current Company employees, managers or contractors who have
# executed Confidentiality and Non-disclosure agreements explicitly covering
# such access.
#
# The copyright notice above does not evidence any actual or intended
# publication or disclosure of this source code, which includes information
# that is confidential and/or proprietary, and is a trade secret, of the
# Company. ANY REPRODUCTION, MODIFICATION, DISTRIBUTION, PUBLIC PERFORMANCE,
# OR PUBLIC DISPLAY OF OR THROUGH USE OF THIS SOURCE CODE WITHOUT THE EXPRESS
# WRITTEN CONSENT OF THE COMPANY IS STRICTLY PROHIBITED, AND IN VIOLATION OF
# APPLICABLE LAWS AND INTERNATIONAL TREATIES. THE RECEIPT OR POSSESSION OF
# THIS SOURCE CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR IMPLY ANY
# RIGHTS TO REPRODUCE, DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE,
# USE, OR SELL ANYTHING THAT IT MAY DESCRIBE, IN WHOLE OR IN PART.
# ===----------------------------------------------------------------------===

# ===----------------------------------------------------------------------===
# This file is based in part on code published as part of the pynode project.
# The original work is copyrighted by it's authors and licensed according to
# the terms of the MIT license (below); modifications since then are the
# property of RokuSigma Inc. and subject to the above-referenced
# confidentiality and non-disclosure agreements.
# ===----------------------------------------------------------------------===

# ===----------------------------------------------------------------------===
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ===----------------------------------------------------------------------===

from struct import pack, unpack
from binascii import hexlify

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from python_patterns.utils.decorators import Property

from .crypto import hash256
from .merkle import merkle_list
from .script import Script
from .serialize import (
    serialize_varchar, deserialize_varchar,
    serialize_hash, deserialize_hash,
    serialize_list, deserialize_list)
from .utils import uint256_from_compact

__all__ = [
    'OutPoint',
    'Input',
    'Output',
    'Transaction',
    'Block',
]

class OutPoint(object):
    def __init__(self, hash=0, n=0xffffffff, *args, **kwargs):
        super(OutPoint, self).__init__(*args, **kwargs)
        self.hash = hash
        self.n = n

    def serialize(self):
        result  = serialize_hash(self.hash, 32)
        result += pack('<I', self.n)
        return result
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['hash'] = deserialize_hash(file_, 32)
        initargs['n'] = unpack('<I', file_.read(4))[0]
        return cls(**initargs)

    def set_null(self):
        self.hash = 0
        self.n = 0xffffffff
    def is_null(self):
        return self.hash==0 and self.n==0xffffffff

    def __eq__(self, other):
        return self.hash == other.hash and self.n == other.n
    def __repr__(self):
        return 'OutPoint(hash=%064x, n=%d)' % (
            self.hash,
            self.n==0xffffffff and -1 or self.n)

class Input(object):
    def __init__(self, prevout=None, scriptSig=None, nSequence=0xffffffff, *args, **kwargs):
        if prevout is None:
            prevout = self.deserialize_prevout(StringIO('\x00'*32 + '\xff'*4))
        if scriptSig is None:
            scriptSig = kwargs.pop('coinbase', Script())
        super(Input, self).__init__(*args, **kwargs)
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
    def deserialize_prevout(file_):
        return OutPoint.deserialize(file_)
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['prevout'] = cls.deserialize_prevout(file_)
        str_ = deserialize_varchar(file_)
        initargs['nSequence'] = unpack('<I', file_.read(4))[0]
        if initargs['prevout'].is_null() and initargs['nSequence']==0xffffffff:
            initargs['coinbase'] = str_ # <-- coinbase
        else:
            initargs['scriptSig'] = Script.deserialize(StringIO(str_))
        return cls(**initargs)

    def is_final(self):
        return self.nSequence==0xffffffff
    def is_valid(self):
        return True

    def __eq__(self, other):
        return (self.prevout == other.prevout and
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

class Output(object):
    def __init__(self, nValue=0, scriptPubKey=None, *args, **kwargs):
        if scriptPubKey is None:
            scriptPubKey = Script()
        super(Output, self).__init__(*args, **kwargs)
        self.nValue = nValue
        self.scriptPubKey = scriptPubKey

    def serialize(self):
        result  = pack('<Q', self.nValue)
        result += self.scriptPubKey.serialize()
        return result
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['nValue'] = unpack('<Q', file_.read(8))[0]
        initargs['scriptPubKey'] = Script.deserialize(StringIO(deserialize_varchar(file_)))
        return cls(**initargs)

    def is_valid(self):
        if self.nValue<0 or self.nValue>2100000000000000L:
            return False
        return True

    def __eq__(self, other):
        return (self.nValue == other.nValue and
            self.scriptPubKey == other.scriptPubKey)
    def __repr__(self):
        return 'Output(nValue=%d.%08d, scriptPubKey=%s)' % (
            self.nValue // 100000000,
            self.nValue % 100000000,
            repr(self.scriptPubKey))

class Transaction(object):
    def __init__(self, nVersion=1, vin=None, vout=None, nLockTime=0, nRefHeight=0, *args, **kwargs):
        # defaults
        if vin is None:
            vin = []
        if vout is None:
            vout = []

        super(Transaction, self).__init__(*args, **kwargs)

        # serialized
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

    def vout_create(self):
        self.vout = []
    def vout_append(self, tout):
        self.vout.append(tout)
    def vout_count(self):
        return len(self.vout)
    def vout_index(self, idx):
        return self.vout[idx]

    def serialize(self):
        result  = pack('<I', self.nVersion)
        result += serialize_list(self.vin, lambda i:i.serialize())
        result += serialize_list(self.vout, lambda o:o.serialize())
        result += pack('<I', self.nLockTime)
        if self.nVersion==2:
            result += pack('<I', self.nRefHeight)
        return result
    @staticmethod
    def deserialize_input(file_, *args, **kwargs):
        return Input.deserialize(file_, *args, **kwargs)
    @staticmethod
    def deserialize_output(file_, *args, **kwargs):
        return Output.deserialize(file_, *args, **kwargs)
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['nVersion'] = unpack('<I', file_.read(4))[0]
        initargs['vin'] = list(deserialize_list(file_, cls.deserialize_input))
        initargs['vout'] = list(deserialize_list(file_, cls.deserialize_output))
        initargs['nLockTime'] = unpack('<I', file_.read(4))[0]
        if initargs['nVersion']==2:
            initargs['nRefHeight'] = unpack('<I', file_.read(4))[0]
        else:
            initargs['nRefHeight'] = 0
        return cls(**initargs)

    @Property
    def hash():
        def fget(self):
            return hash256(self.serialize())
        return locals()

    @Property
    def size():
        def fget(self):
            return len(self.serialize())
        return locals()

    def is_valid(self, mode=None):
        if mode is None:
            mode = 'simple'
        if mode not in ('full', 'simple'):
            raise ValueError(u"unrecognized input validation mode")
        getattr(self, 'hash')
        if not self.is_coinbase():
            for idx in xrange(self.vin_count()):
                if not self.vin_index(idx).is_valid():
                    return False
        for idx in xrange(self.vout_count()):
            if not self.vout_index(idx).is_valid():
                return False
        if self.nVersion not in (2,):
            if self.nRefHeight != 0:
                return False
        if mode in ('simple',):
            return True
        return True
    def is_final(self):
        for idx in xrange(self.vin_count()):
            if not self.vin_index(idx).is_final():
                return False
        return True
    def is_coinbase(self):
        return self.vin_count()==1 and self.vin_index(0).prevout.is_null()

    def __eq__(self, other):
        if (self.nVersion != other.nVersion or
            self.nLockTime != other.nLockTime or
            self.nRefHeight != other.nRefHeight):
            return False
        vin_count = self.vin_count()
        if vin_count != other.vin_count():
            return False
        for idx in xrange(vin_count):
            if self.vin_index(idx) != other.vin_index(idx):
                return False
        vout_count = self.vout_count()
        if vout_count != other.vout_count():
            return False
        for idx in xrange(vout_count):
            if self.vout_index(idx) != other.vout_index(idx):
                return False
        return True
    def __repr__(self):
        nRefHeight_str = (self.nVersion==2
            and ', nRefHeight=%d' % self.nRefHeight
             or '')
        return 'Transaction(nVersion=%d, vin=%s, vout=%s, nLockTime=%d%s)' % (
            self.nVersion,
            repr(self.vin),
            repr(self.vout),
            self.nLockTime,
            nRefHeight_str)

class Block(object):
    def __init__(self, nVersion=1, hashPrevBlock=0, hashMerkleRoot=None, nTime=0, nBits=0x1d00ffff, nNonce=0, vtx=None, *args, **kwargs):
        if vtx is None:
            vtx = []

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
            self.vtx_append(tx)

    def vtx_create(self):
        self.vtx = []
    def vtx_append(self, tx):
        self.vtx.append(tx)
    def vtx_count(self):
        return len(self.vtx)
    def vtx_index(self, idx):
        return self.vtx[idx]

    def serialize(self, mode=None):
        if mode is None:
            mode = 'header'
        if mode not in ('full', 'header'):
            raise ValueError(u"unrecognized block serialization mode")
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
    @staticmethod
    def deserialize_transaction(file_, *args, **kwargs):
        return Transaction.deserialize(file_, *args, **kwargs)
    @classmethod
    def deserialize(cls, file_, mode=None):
        if mode is None:
            mode = 'header'
        if mode not in ('full', 'header'):
            raise ValueError(u"unrecognized block serialization mode")
        initargs = {}
        initargs['nVersion'] = unpack('<I', file_.read(4))[0]
        initargs['hashPrevBlock'] = deserialize_hash(file_, 32)
        initargs['hashMerkleRoot'] = deserialize_hash(file_, 32)
        initargs['nTime'] = unpack('<I', file_.read(4))[0]
        initargs['nBits'] = unpack('<I', file_.read(4))[0]
        initargs['nNonce'] = unpack('<I', file_.read(4))[0]
        if mode in ('header',):
            return cls(**initargs)
        initargs['vtx'] = list(deserialize_list(file_, cls.deserialize_transaction))
        return cls(**initargs)

    @Property
    def hash():
        def fget(self):
            return hash256(self.serialize(mode='header'))
        return locals()

    @Property
    def size():
        def fget(self):
            return len(self.serialize(mode='full'))
        return locals()

    def is_valid(self, mode=None):
        if mode is None:
            mode = 'header'
        if mode not in ('full', 'simple', 'header'):
            raise ValueError(u"unrecognized block validation mode")
        target = uint256_from_compact(self.nBits)
        if self.hash > target:
            return False
        if mode in ('header',):
            return True
        if self.hashMerkleRoot != merkle_list(self.vtx_index(idx).hash for idx in xrange(self.vtx_count())):
            return False
        for idx in xrange(self.vtx_count()):
            if not self.vtx_index(idx).is_valid(mode):
                return False
        return True

    def __repr__(self):
        return 'Block(nVersion=%d, hashPrevBlock=0x%064x, hashMerkleRoot=0x%064x, nTime=%s, nBits=0x%08x, nNonce=0x%08x, vtx=%s)' % (
            self.nVersion,
            self.hashPrevBlock,
            self.hashMerkleRoot,
            self.nTime,
            self.nBits,
            self.nNonce,
            repr(self.vtx))

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
