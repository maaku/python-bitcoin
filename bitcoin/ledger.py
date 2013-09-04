# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

# Python 2 and 3 compatibility utilities
import six

from blist import sorteddict

from .core import Output
from .crypto import hash256
from .mixins import SerializableMixin
from .patricia import PatriciaNode
from .serialize import (
    serialize_leint, deserialize_leint,
    serialize_varint, deserialize_varint)
from .tools import compress_amount, decompress_amount

# ===----------------------------------------------------------------------===

from .script import ScriptPickler

class UnspentTransaction(SerializableMixin, sorteddict):
    """Pruned version of core.Transaction: only retains metadata and unspent
    transaction outputs.

    Serialized format:
        - VARINT(version)
        - VARINT(code)
        - unspentness bitvector, for outputs[2] and further; least significant
          byte first
        - the non-spent, compressed TransactionOutputs
        - VARINT(height)
        - VARINT(reference_height)

    The code value consists of:
        - bit 1: is_coinbase flag
        - bit 2: outputs[0] is not spent
        - bit 4: outputs[1] is not spent
        - The higher bits encode N, the number of non-zero bytes in the following
          bitvector.
            - In case both bit 2 and bit 4 are unset, they encode N-1, as there
              must be at least one non-spent output.

    Example: 0104835800816115944e077fe7c803cfa57f29b36bf87c1d358bb85e
             <><><--------------------------------------------><---->
             |  \                  |                             /
       version   code           outputs[1]                  height
    
        - version = 1
        - code = 4 (outputs[1] is not spent, and 0 non-zero bytes of bitvector follow)
        - unspentness bitvector: as 0 non-zero bytes follow, it has length 0
        - outputs[1]: 835800816115944e077fe7c803cfa57f29b36bf87c1d35
            * 8358: compact amount representation for 60000000000 (600 BTC)
            * 00: special txout type pay-to-pubkey-hash
            * 816115944e077fe7c803cfa57f29b36bf87c1d35: address uint160
        - height = 203998
    
     Example: 02090440fe792b067e0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee...
              <><><--><-------------------------------------------------->
             /  |   \                     |
      version  code  unspentness     outputs[4]

              ...fe23290f00008c988f1a4a4de2161e0f50aac7f17e7f9555caa4fe3bd80100fde803
                 <--------------------------------------------------><--------><---->
                                             |                         /          |
                                        outputs[16]               height  reference_height
    
      - version = 2
      - code = 9: coinbase, neither outputs[0] or outputs[1] are unspent,
        2 (1, +1 because both bit 2 and bit 4 are unset) non-zero bitvector
        bytes follow.
      - unspentness bitvector: bits 2 (0x04) and 14 (0x4000) are set, so
        outputs[2+2] and outputs[14+2] are unspent
      - outputs[4]: fe792b067e0061b01caab50f1b8e9c50a5057eb43c2d9563a4ee
                    * fe792b067e: compact amount representation for 234925952 (2.35 BTC)
                    * 00: special txout type pay-to-pubkey-hash
                    * 61b01caab50f1b8e9c50a5057eb43c2d9563a4ee: address uint160
      - outputs[16]: fe23290f00008c988f1a4a4de2161e0f50aac7f17e7f9555caa4
                     * fe23290f00: compact amount representation for 110397 (0.001 BTC)
                     * 00: special txout type pay-to-pubkey-hash
                     * 8c988f1a4a4de2161e0f50aac7f17e7f9555caa4: address uint160
      - height = 120891
      - reference_height = 1000
    """
    # We only need one script pickler, which every instance of UnspentTransaction
    # can use (there's no concurrency issues with picklers, and it needs to be
    # available to the class anyway for deserialize).
    _pickler = ScriptPickler()

    def __init__(self, *args, **kwargs):
        # Since we behave like a dictionary object, we implement the copy
        # constructor, which requires copying meta information not contained
        # within the dictionary itself.
        if args and all(hasattr(args[0], x) for x in
                ('version', 'is_coinbase', 'height', 'reference_height')):
            other = args[0]
        else:
            other = None

        # You can either specify the transaction, another UnspentTransaction
        # object, or the metadata directly. Choose one.
        a = 'transaction' in kwargs
        b = other is not None
        c = any(x in kwargs for x in (
            'coinbase', 'version', 'reference_height'))
        if a + b + c >= 2: # <-- yes, you can do this
            raise TypeError(u"instantiate by either specifying the "
                u"transaction directly, another %s, or its individual "
                u"metadata; choose one" % self.__class__.__name__)

        # Extract captured parameters from kwargs, starting with the transaction
        # because its metadata are used as the default.
        transaction = kwargs.pop('transaction', None)
        if other is None:
            other = transaction

        version = kwargs.pop('version', getattr(other, 'version', 1))
        is_coinbase = kwargs.pop('coinbase', getattr(other, 'is_coinbase', False))
        height = kwargs.pop('height', getattr(other, 'height', 0))

        # Reference heights are added with transaction version=2, so we do
        # not extract that parameter unless version=2.
        reference_height = getattr(other, 'reference_height', 0)
        if version in (2,):
            reference_height = kwargs.pop('reference_height', reference_height)

        # Perform construction of the dictionary object (our superclass)
        super(UnspentTransaction, self).__init__(*args, **kwargs)

        # Store metadata
        self.version          = version
        self.is_coinbase      = is_coinbase
        self.height           = height
        self.reference_height = reference_height

        # Add the transaction's outputs only if outputs are not separately
        # specified (as is typically done if it is known in advance which
        # outputs are not spent at time of creation).
        if transaction is not None and not self:
            for idx,output in enumerate(transaction.outputs):
                self[idx] = output

    def serialize(self):
        # code&0x1: is_coinbase
        # code&0x2: outputs[0] unspent
        # code&0x4: outputs[1] unspent
        # code>>3: N, the minimal length of bitvector in bytes, or N-1 if both
        #   outputs[0] and outputs[1] are spent
        code, bitvector = 0, 0
        for idx in six.iterkeys(self):
            bitvector |= 1 << idx
        if not bitvector:
            raise TypeError()
        code |= bitvector & 0x3
        bitvector >>= 2
        bitvector = serialize_leint(bitvector)
        bitvector_len = len(bitvector)
        if not code:
            bitvector_len -= 1
        code |= bitvector_len << 2
        code <<= 1
        if self.is_coinbase:
            code |= 1

        result  = serialize_varint(self.version)
        result += serialize_varint(code)
        result += bitvector
        for output in six.itervalues(self):
            result += serialize_varint(compress_amount(output.amount))
            result += self._pickler.dumps(output.contract)
        result += serialize_varint(self.height)
        if self.version in (2,):
            result += serialize_varint(self.reference_height)
        return result
    @classmethod
    def deserialize(cls, file_):
        output_class = getattr(cls, 'get_output_class', lambda:
                       getattr(cls, 'output_class', Output))()
        kwargs = {}
        kwargs['version'] = deserialize_varint(file_)

        # See description of code, bitvector above.
        code, bitvector = deserialize_varint(file_), 0
        kwargs['coinbase'] = bool(code & 0x1)
        code >>= 1
        bitvector |= code & 0x3
        code >>= 2
        if not bitvector:
            code += 1
        if code:
            bitvector |= deserialize_leint(file_, code) << 2
        idx, items = 0, []
        while bitvector:
            if bitvector & 0x1:
                items.append(
                    (idx, output_class(
                        decompress_amount(deserialize_varint(file_)),
                        cls._pickler.load(file_))))
            idx, bitvector = idx + 1, bitvector >> 1

        kwargs['height'] = deserialize_varint(file_)
        if kwargs['version'] in (2,):
            kwargs['reference_height'] = deserialize_varint(file_)
        return cls(items, **kwargs)

    def __eq__(self, other):
        # Compare metadata first, as it's probably less expensive
        if any((self.height      != other.height,
                self.is_coinbase != other.is_coinbase,
                self.version     != other.version)):
            return False
        if self.version in (2,) and self.reference_height != other.reference_height:
            return False
        return super(UnspentTransaction, self).__eq__(other)
    __ne__ = lambda a,b:not a==b
    def __repr__(self):
        return '%s%s, coinbase=%s, version=%d, height=%d, reference_height=%d)' % (
            self.__class__.__name__,
            super(UnspentTransaction, self).__repr__()[10:-1],
            self.is_coinbase,
            self.version,
            self.height,
            self.reference_height)

# ===----------------------------------------------------------------------===

class BaseTxIdIndex(object):
    key_class = hash256
    value_class = UnspentTransaction

class TxIdIndex(BaseTxIdIndex, PatriciaNode):
    pass

# ===----------------------------------------------------------------------===

from recordtype import recordtype

ContractOutPoint = recordtype('ContractOutPoint', ['contract', 'hash', 'index'])
ContractOutPoint._pickler = ScriptPickler()
def _serialize_contract_outpoint(self):
    return b''.join([self._pickler.dumps(self.contract.serialize()),
                     hash256.serialize(self.hash),
                     serialize_varint(self.index)])
ContractOutPoint.serialize = _serialize_contract_outpoint
def _deserialize_contract_outpoint(cls, file_):
    kwargs = {}
    kwargs['contract'] = cls._pickler.load(file_)
    kwargs['hash'] = hash256.deserialize(file_)
    kwargs['index'] = deserialize_varint(file_)
    return cls(**kwargs)
ContractOutPoint.deserialize = classmethod(_deserialize_contract_outpoint)
def _repr_contract_outpoint(self):
    return '%s(contract=%s, hash=%064x, index=%d)' % (
        self.__class__.__name__, repr(self.contract), self.hash, self.index)
ContractOutPoint.__repr__ = _repr_contract_outpoint

OutputData = recordtype('OutputData',
    ['version', 'amount', 'coinbase', 'height', 'reference_height'])
OutputData.is_coinbase = OutputData.coinbase
def _serialize_output_data(self):
    result  = serialize_varint(self.version)
    result += serialize_varint((self.height<<1)|self.is_coinbase)
    result += serialize_varint(compress_amount(self.amount))
    if self.version in (2,):
        result += serialize_varint((self.height<<1)|self.reference_height)
    return result
OutputData.serialize = _serialize_output_data
def _deserialize_output_data(cls, file_):
    kwargs = {}
    kwargs['version'] = deserialize_varint(file_)
    code = deserialize_varint(file_)
    kwargs['coinbase'] = code & 1
    kwargs['height'] = code >> 1
    kwargs['amount'] = decompress_amount(deserialize_varint(file_))
    if kwargs['version'] in (2,):
        kwargs['reference_height'] = deserialize_varint(file_)
    return cls(**kwargs)
OutputData.deserialize = classmethod(_deserialize_output_data)

class BaseContractIndex(object):
    key_class = ContractOutPoint
    value_class = OutputData

class ContractIndex(BaseContractIndex, PatriciaNode):
    pass

#
# End of File
#
