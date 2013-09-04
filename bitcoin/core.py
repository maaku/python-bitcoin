# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import calendar
import numbers
from struct import pack, unpack

from recordtype import recordtype

from .mixins import HashableMixin, SerializableMixin
from .numeric import mpq
from .serialize import (
    serialize_varchar, deserialize_varchar,
    serialize_hash, deserialize_hash,
    serialize_list, deserialize_list)
from .tools import StringIO, icmp, list, target_from_compact, tuple

__all__ = [
    'ChainParameters',
    'Output',
    'Input',
    'Transaction',
    'Block',
    'ConnectedBlockInfo',
]

# ===----------------------------------------------------------------------===

ChainParameters = recordtype('ChainParameters',
    ['magic', 'port', 'genesis', 'testnet', 'pubkey_hash_prefix',
     'script_hash_prefix', 'secret_prefix', 'max_value', 'transient_reward',
     'transient_budget', 'perpetual_reward', 'perpetual_budget', 'fee_budget',
     'maximum_target', 'next_target', 'alert_keys','checkpoints', 'features'])

# ===----------------------------------------------------------------------===

from .script import Script

# ===----------------------------------------------------------------------===

class Output(SerializableMixin):
    def __init__(self, amount=0, contract=None, *args, **kwargs):
        if contract is None:
            contract = self.get_script_class()()
        super(Output, self).__init__(*args, **kwargs)
        self.amount = amount
        self.contract = contract

    @classmethod
    def get_script_class(cls):
        return getattr(cls, 'script_class', Script)

    def serialize(self):
        result  = pack('<Q', self.amount)
        result += self.contract.serialize()
        return result
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['amount'] = unpack('<Q', file_.read(8))[0]
        initargs['contract'] = cls.get_script_class().deserialize(file_)
        return cls(**initargs)

    def __eq__(self, other):
        return all((self.amount   == other.amount,
                    self.contract == other.contract))
    def __repr__(self):
        return '%s(amount=%d.%08d, contract=%s)' % (
            self.__class__.__name__,
            self.amount // 100000000,
            self.amount  % 100000000,
            repr(self.contract))

# ===----------------------------------------------------------------------===

class Input(SerializableMixin):
    def __init__(self, hash=0, index=0xffffffff, endorsement=None,
                 sequence=0xffffffff, *args, **kwargs):
        if endorsement is None:
            endorsement = kwargs.pop('coinbase', self.get_script_class()())
        super(Input, self).__init__(*args, **kwargs)
        self.hash = hash
        self.index = index
        self.endorsement = endorsement
        self.sequence = sequence

    @classmethod
    def get_script_class(cls):
        return getattr(cls, 'script_class', Script)

    def serialize(self):
        result  = serialize_hash(self.hash, 32)
        result += pack('<I', self.index)
        if hasattr(self.endorsement, 'serialize'):
            result += self.endorsement.serialize()
        else:
            result += serialize_varchar(self.endorsement) # <-- coinbase
        result += pack('<I', self.sequence)
        return result
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['hash'] = deserialize_hash(file_, 32)
        initargs['index'] = unpack('<I', file_.read(4))[0]
        str_ = deserialize_varchar(file_) # <-- might be coinbase!
        initargs['sequence'] = unpack('<I', file_.read(4))[0]
        if not all((initargs['hash']  == 0,
                    initargs['index'] == 0xffffffff)):
            initargs['coinbase'] = str_
        else:
            initargs['endorsement'] = cls.get_script_class().deserialize(
                StringIO(serialize_varchar(str_)))
        return cls(**initargs)

    @property
    def is_coinbase(self):
        return all((self.hash  == 0,
                    self.index == 0xffffffff))

    def __eq__(self, other):
        return all((self.hash        == other.hash,
                    self.index       == other.index,
                    self.endorsement == other.endorsement,
                    self.sequence    == other.sequence))

    def __repr__(self):
        sequence_str = (self.sequence!=0xffffffff
            and ', sequence=%d' % self.sequence
             or '')
        return ('%s(hash=0x%064x, '
                   'index=%d, '
                   '%s=%s%s)') % (
            self.__class__.__name__,
            self.hash,
            self.index==0xffffffff and -1 or self.index,
            self.is_coinbase and 'coinbase' or 'endorsement',
            repr(self.endorsement),
            sequence_str)

# ===----------------------------------------------------------------------===

class Transaction(SerializableMixin, HashableMixin):
    def __init__(self, version=1, inputs=None, outputs=None, lock_time=0,
                 reference_height=0, *args, **kwargs):
        if inputs is None: inputs = ()
        if outputs is None: outputs = ()
        super(Transaction, self).__init__(*args, **kwargs)
        self.version = version
        getattr(self, 'inputs_create', lambda:setattr(x, 'inputs', list()))
        self.inputs.extend(inputs)
        getattr(self, 'outputs_create', lambda:setattr(x, 'outputs', list()))
        self.outputs.extend(outputs)
        self.lock_time = lock_time
        self.reference_height = reference_height

    @classmethod
    def get_input_class(cls):
        return getattr(cls, 'input_class', Input)

    @classmethod
    def get_output_class(cls):
        return getattr(cls, 'output_class', Output)

    def serialize(self):
        if self.version not in (1,2):
            raise NotImplementedError()
        result  = pack('<I', self.version)
        result += serialize_list(self.inputs, lambda i:i.serialize())
        result += serialize_list(self.outputs, lambda o:o.serialize())
        result += pack('<I', self.lock_time)
        if self.version==2:
            result += pack('<I', self.reference_height)
        return result
    @classmethod
    def deserialize_input(cls, file_, *args, **kwargs):
        return cls.get_input_class().deserialize(file_, *args, **kwargs)
    @classmethod
    def deserialize_output(cls, file_, *args, **kwargs):
        return cls.get_output_class().deserialize(file_, *args, **kwargs)
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['version'] = unpack('<I', file_.read(4))[0]
        if initargs['version'] not in (1,2):
            raise NotImplementedError()
        initargs['inputs'] = list(deserialize_list(file_, lambda f:cls.deserialize_input(f)))
        initargs['outputs'] = list(deserialize_list(file_, lambda f:cls.deserialize_output(f)))
        initargs['lock_time'] = unpack('<I', file_.read(4))[0]
        if initargs['version'] in (2,):
            initargs['reference_height'] = unpack('<I', file_.read(4))[0]
        return cls(**initargs)

    @property
    def is_coinbase(self):
        return 1==len(self.inputs) and not self.inputs[0].is_coinbase

    def __eq__(self, other):
        return all((self.version          == other.version,
                    self.lock_time        == other.lock_time,
                    self.reference_height == other.reference_height,
                    icmp(iter(self.inputs),  iter(other.inputs))  == 0,
                    icmp(iter(self.outputs), iter(other.outputs)) == 0))
    def __repr__(self):
        reference_height_str = (self.version in (2,)
            and ', reference_height=%d' % self.reference_height
             or '')
        return ('%s(version=%d, '
                   'inputs=%s, '
                   'outputs=%s, '
                   'lock_time=%d%s)' % (
            self.__class__.__name__,
            self.version,
            repr(self.inputs),
            repr(self.outputs),
            self.lock_time,
            reference_height_str))

# ===----------------------------------------------------------------------===

from .merkle import MerkleList

class Block(SerializableMixin, HashableMixin):
    def __init__(self, version=1, parent_hash=0, merkle_hash=0,
                 time=0, bits=0x1d00ffff, nonce=0, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        parent = getattr(parent, 'hash', parent)
        parent_hash = getattr(parent_hash, 'hash', parent_hash)
        if None not in (parent, parent_hash) and parent != parent_hash:
            raise ValueError( u"parent.hash does not match parent_hash; are "
                u"you sure you know what you're doing?")
        parent_hash = parent_hash or parent or 0

        merkle = kwargs.pop('merkle', None)
        merkle = getattr(merkle, 'hash', merkle)
        merkle_hash = getattr(merkle_hash, 'hash', merkle_hash)
        if None not in (merkle, merkle_hash) and merkle != merkle_hash:
            raise ValueError( u"merkle.hash does not match merkle_hash; are "
                u"you sure you know what you're doing?")
        merkle_hash = merkle_hash or merkle or 0

        super(Block, self).__init__(*args, **kwargs)

        self.version     = version
        self.parent_hash = parent_hash
        self.merkle_hash = merkle_hash
        self.time        = time
        self.bits        = bits
        self.nonce       = nonce

    def serialize(self):
        if self.version not in (1,2):
            raise NotImplementedError()
        result  = pack('<I', self.version)
        result += serialize_hash(self.parent_hash, 32)
        result += serialize_hash(self.merkle_hash, 32)
        if isinstance(self.time, numbers.Integral):
            time = self.time
        else:
            time = calendar.timegm(self.time.utctimetuple())
        result += pack('<I', time)
        result += pack('<I', self.bits)
        result += pack('<I', self.nonce)
        return result
    def __bytes__(self):
        return self.serialize()
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['version'] = unpack('<I', file_.read(4))[0]
        if initargs['version'] not in (1,2):
            raise NotImplementedError()
        initargs['parent_hash'] = deserialize_hash(file_, 32)
        initargs['merkle_hash'] = deserialize_hash(file_, 32)
        initargs['time'] = unpack('<I', file_.read(4))[0]
        initargs['bits'] = unpack('<I', file_.read(4))[0]
        initargs['nonce'] = unpack('<I', file_.read(4))[0]
        return cls(**initargs)

    def __eq__(self, other):
        return all((self.version     == other.version,
                    self.parent_hash == other.parent_hash,
                    self.merkle_hash == other.merkle_hash,
                    self.time        == other.time,
                    self.bits        == other.bits,
                    self.nonce       == other.nonce))
    def __repr__(self):
        return ('%s(version=%d, '
                   'parent_hash=0x%064x, '
                   'merkle_hash=0x%064x, '
                   'time=%s, '
                   'bits=0x%08x, '
                   'nonce=0x%08x)' % (
            self.__class__.__name__,
            self.version,
            self.parent_hash,
            self.merkle_hash,
            self.time,
            self.bits,
            self.nonce))

    @property
    def difficulty(self):
        return mpq(target_from_compact(0x1d00ffff),
                   target_from_compact(self.bits))

    @property
    def work(self):
        target = target_from_compact(self.bits)
        if target < 0:
            return 0
        return (1<<256) // (target+1)

ConnectedBlockInfo = recordtype('ConnectedBlockInfo',
    ['parent', 'height', 'aggregate_work'])

#
# End of File
#
