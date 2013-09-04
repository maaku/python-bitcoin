# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import six

from struct import pack, unpack

from .tools import StringIO

from .mixins import SerializableMixin
from .serialize import (
    serialize_varchar, deserialize_varchar,
    serialize_hash, deserialize_hash)

# ===----------------------------------------------------------------------===

SIGHASH_ALL          = 0x01
SIGHASH_NONE         = 0x02
SIGHASH_SINGLE       = 0x03
SIGHASH_ANYONECANPAY = 0x80

TX_NONSTANDARD = 'non-standard'
TX_PUBKEY      = 'pubkey'
TX_PUBKEYHASH  = 'pubkey-hash'
TX_SCRIPTHASH  = 'script-hash'
TX_MULTISIG    = 'multi-sig'

# ===----------------------------------------------------------------------===

# push value
OP_0         = 0x00
OP_FALSE     = OP_0
OP_PUSHDATA1 = 0x4c
OP_PUSHDATA2 = 0x4d
OP_PUSHDATA4 = 0x4e
OP_1NEGATE   = 0x4f
OP_RESERVED  = 0x50
OP_1         = 0x51
OP_TRUE      = OP_1
OP_2         = 0x52
OP_3         = 0x53
OP_4         = 0x54
OP_5         = 0x55
OP_6         = 0x56
OP_7         = 0x57
OP_8         = 0x58
OP_9         = 0x59
OP_10        = 0x5a
OP_11        = 0x5b
OP_12        = 0x5c
OP_13        = 0x5d
OP_14        = 0x5e
OP_15        = 0x5f
OP_16        = 0x60

# control
OP_NOP      = 0x61
OP_VER      = 0x62
OP_IF       = 0x63
OP_NOTIF    = 0x64
OP_VERIF    = 0x65
OP_VERNOTIF = 0x66
OP_ELSE     = 0x67
OP_ENDIF    = 0x68
OP_VERIFY   = 0x69
OP_RETURN   = 0x6a

# stack ops
OP_TOALTSTACK   = 0x6b
OP_FROMALTSTACK = 0x6c
OP_2DROP        = 0x6d
OP_2DUP         = 0x6e
OP_3DUP         = 0x6f
OP_2OVER        = 0x70
OP_2ROT         = 0x71
OP_2SWAP        = 0x72
OP_IFDUP        = 0x73
OP_DEPTH        = 0x74
OP_DROP         = 0x75
OP_DUP          = 0x76
OP_NIP          = 0x77
OP_OVER         = 0x78
OP_PICK         = 0x79
OP_ROLL         = 0x7a
OP_ROT          = 0x7b
OP_SWAP         = 0x7c
OP_TUCK         = 0x7d

# splice ops
OP_CAT    = 0x7e
OP_SUBSTR = 0x7f
OP_LEFT   = 0x80
OP_RIGHT  = 0x81
OP_SIZE   = 0x82

# bit logic
OP_INVERT      = 0x83
OP_AND         = 0x84
OP_OR          = 0x85
OP_XOR         = 0x86
OP_EQUAL       = 0x87
OP_EQUALVERIFY = 0x88
OP_RESERVED1   = 0x89
OP_RESERVED2   = 0x8a

# numeric
OP_1ADD      = 0x8b
OP_1SUB      = 0x8c
OP_2MUL      = 0x8d
OP_2DIV      = 0x8e
OP_NEGATE    = 0x8f
OP_ABS       = 0x90
OP_NOT       = 0x91
OP_0NOTEQUAL = 0x92

OP_ADD    = 0x93
OP_SUB    = 0x94
OP_MUL    = 0x95
OP_DIV    = 0x96
OP_MOD    = 0x97
OP_LSHIFT = 0x98
OP_RSHIFT = 0x99

OP_BOOLAND            = 0x9a
OP_BOOLOR             = 0x9b
OP_NUMEQUAL           = 0x9c
OP_NUMEQUALVERIFY     = 0x9d
OP_NUMNOTEQUAL        = 0x9e
OP_LESSTHAN           = 0x9f
OP_GREATERTHAN        = 0xa0
OP_LESSTHANOREQUAL    = 0xa1
OP_GREATERTHANOREQUAL = 0xa2
OP_MIN                = 0xa3
OP_MAX                = 0xa4

OP_WITHIN = 0xa5

# crypto
OP_RIPEMD160           = 0xa6
OP_SHA1                = 0xa7
OP_SHA256              = 0xa8
OP_HASH160             = 0xa9
OP_HASH256             = 0xaa
OP_CODESEPARATOR       = 0xab
OP_CHECKSIG            = 0xac
OP_CHECKSIGVERIFY      = 0xad
OP_CHECKMULTISIG       = 0xae
OP_CHECKMULTISIGVERIFY = 0xaf

# expansion
OP_NOP1  = 0xb0
OP_NOP2  = 0xb1
OP_NOP3  = 0xb2
OP_NOP4  = 0xb3
OP_NOP5  = 0xb4
OP_NOP6  = 0xb5
OP_NOP7  = 0xb6
OP_NOP8  = 0xb7
OP_NOP9  = 0xb8
OP_NOP10 = 0xb9

# template matching params
OP_SMALLINTEGER = 0xfa
OP_PUBKEYS      = 0xfb
OP_PUBKEYHASH   = 0xfd
OP_PUBKEY       = 0xfe

OP_INVALIDOPCODE = 0xff

# ===----------------------------------------------------------------------===

VALID_OPCODES = set([
    OP_1NEGATE,
    OP_RESERVED,
    OP_1,
    OP_2,
    OP_3,
    OP_4,
    OP_5,
    OP_6,
    OP_7,
    OP_8,
    OP_9,
    OP_10,
    OP_11,
    OP_12,
    OP_13,
    OP_14,
    OP_15,
    OP_16,

    OP_NOP,
    OP_VER,
    OP_IF,
    OP_NOTIF,
    OP_VERIF,
    OP_VERNOTIF,
    OP_ELSE,
    OP_ENDIF,
    OP_VERIFY,
    OP_RETURN,

    OP_TOALTSTACK,
    OP_FROMALTSTACK,
    OP_2DROP,
    OP_2DUP,
    OP_3DUP,
    OP_2OVER,
    OP_2ROT,
    OP_2SWAP,
    OP_IFDUP,
    OP_DEPTH,
    OP_DROP,
    OP_DUP,
    OP_NIP,
    OP_OVER,
    OP_PICK,
    OP_ROLL,
    OP_ROT,
    OP_SWAP,
    OP_TUCK,

    OP_CAT,
    OP_SUBSTR,
    OP_LEFT,
    OP_RIGHT,
    OP_SIZE,

    OP_INVERT,
    OP_AND,
    OP_OR,
    OP_XOR,
    OP_EQUAL,
    OP_EQUALVERIFY,
    OP_RESERVED1,
    OP_RESERVED2,

    OP_1ADD,
    OP_1SUB,
    OP_2MUL,
    OP_2DIV,
    OP_NEGATE,
    OP_ABS,
    OP_NOT,
    OP_0NOTEQUAL,

    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_DIV,
    OP_MOD,
    OP_LSHIFT,
    OP_RSHIFT,

    OP_BOOLAND,
    OP_BOOLOR,
    OP_NUMEQUAL,
    OP_NUMEQUALVERIFY,
    OP_NUMNOTEQUAL,
    OP_LESSTHAN,
    OP_GREATERTHAN,
    OP_LESSTHANOREQUAL,
    OP_GREATERTHANOREQUAL,
    OP_MIN,
    OP_MAX,

    OP_WITHIN,

    OP_RIPEMD160,
    OP_SHA1,
    OP_SHA256,
    OP_HASH160,
    OP_HASH256,
    OP_CODESEPARATOR,
    OP_CHECKSIG,
    OP_CHECKSIGVERIFY,
    OP_CHECKMULTISIG,
    OP_CHECKMULTISIGVERIFY,

    OP_NOP1,
    OP_NOP2,
    OP_NOP3,
    OP_NOP4,
    OP_NOP5,
    OP_NOP6,
    OP_NOP7,
    OP_NOP8,
    OP_NOP9,
    OP_NOP10,

    OP_SMALLINTEGER,
    OP_PUBKEYS,
    OP_PUBKEYHASH,
    OP_PUBKEY,
])

OPCODE_NAMES = {
    OP_0 : 'OP_0',
    OP_PUSHDATA1 : 'OP_PUSHDATA1',
    OP_PUSHDATA2 : 'OP_PUSHDATA2',
    OP_PUSHDATA4 : 'OP_PUSHDATA4',
    OP_1NEGATE : 'OP_1NEGATE',
    OP_RESERVED : 'OP_RESERVED',
    OP_1 : 'OP_1',
    OP_2 : 'OP_2',
    OP_3 : 'OP_3',
    OP_4 : 'OP_4',
    OP_5 : 'OP_5',
    OP_6 : 'OP_6',
    OP_7 : 'OP_7',
    OP_8 : 'OP_8',
    OP_9 : 'OP_9',
    OP_10 : 'OP_10',
    OP_11 : 'OP_11',
    OP_12 : 'OP_12',
    OP_13 : 'OP_13',
    OP_14 : 'OP_14',
    OP_15 : 'OP_15',
    OP_16 : 'OP_16',
    OP_NOP : 'OP_NOP',
    OP_VER : 'OP_VER',
    OP_IF : 'OP_IF',
    OP_NOTIF : 'OP_NOTIF',
    OP_VERIF : 'OP_VERIF',
    OP_VERNOTIF : 'OP_VERNOTIF',
    OP_ELSE : 'OP_ELSE',
    OP_ENDIF : 'OP_ENDIF',
    OP_VERIFY : 'OP_VERIFY',
    OP_RETURN : 'OP_RETURN',
    OP_TOALTSTACK : 'OP_TOALTSTACK',
    OP_FROMALTSTACK : 'OP_FROMALTSTACK',
    OP_2DROP : 'OP_2DROP',
    OP_2DUP : 'OP_2DUP',
    OP_3DUP : 'OP_3DUP',
    OP_2OVER : 'OP_2OVER',
    OP_2ROT : 'OP_2ROT',
    OP_2SWAP : 'OP_2SWAP',
    OP_IFDUP : 'OP_IFDUP',
    OP_DEPTH : 'OP_DEPTH',
    OP_DROP : 'OP_DROP',
    OP_DUP : 'OP_DUP',
    OP_NIP : 'OP_NIP',
    OP_OVER : 'OP_OVER',
    OP_PICK : 'OP_PICK',
    OP_ROLL : 'OP_ROLL',
    OP_ROT : 'OP_ROT',
    OP_SWAP : 'OP_SWAP',
    OP_TUCK : 'OP_TUCK',
    OP_CAT : 'OP_CAT',
    OP_SUBSTR : 'OP_SUBSTR',
    OP_LEFT : 'OP_LEFT',
    OP_RIGHT : 'OP_RIGHT',
    OP_SIZE : 'OP_SIZE',
    OP_INVERT : 'OP_INVERT',
    OP_AND : 'OP_AND',
    OP_OR : 'OP_OR',
    OP_XOR : 'OP_XOR',
    OP_EQUAL : 'OP_EQUAL',
    OP_EQUALVERIFY : 'OP_EQUALVERIFY',
    OP_RESERVED1 : 'OP_RESERVED1',
    OP_RESERVED2 : 'OP_RESERVED2',
    OP_1ADD : 'OP_1ADD',
    OP_1SUB : 'OP_1SUB',
    OP_2MUL : 'OP_2MUL',
    OP_2DIV : 'OP_2DIV',
    OP_NEGATE : 'OP_NEGATE',
    OP_ABS : 'OP_ABS',
    OP_NOT : 'OP_NOT',
    OP_0NOTEQUAL : 'OP_0NOTEQUAL',
    OP_ADD : 'OP_ADD',
    OP_SUB : 'OP_SUB',
    OP_MUL : 'OP_MUL',
    OP_DIV : 'OP_DIV',
    OP_MOD : 'OP_MOD',
    OP_LSHIFT : 'OP_LSHIFT',
    OP_RSHIFT : 'OP_RSHIFT',
    OP_BOOLAND : 'OP_BOOLAND',
    OP_BOOLOR : 'OP_BOOLOR',
    OP_NUMEQUAL : 'OP_NUMEQUAL',
    OP_NUMEQUALVERIFY : 'OP_NUMEQUALVERIFY',
    OP_NUMNOTEQUAL : 'OP_NUMNOTEQUAL',
    OP_LESSTHAN : 'OP_LESSTHAN',
    OP_GREATERTHAN : 'OP_GREATERTHAN',
    OP_LESSTHANOREQUAL : 'OP_LESSTHANOREQUAL',
    OP_GREATERTHANOREQUAL : 'OP_GREATERTHANOREQUAL',
    OP_MIN : 'OP_MIN',
    OP_MAX : 'OP_MAX',
    OP_WITHIN : 'OP_WITHIN',
    OP_RIPEMD160 : 'OP_RIPEMD160',
    OP_SHA1 : 'OP_SHA1',
    OP_SHA256 : 'OP_SHA256',
    OP_HASH160 : 'OP_HASH160',
    OP_HASH256 : 'OP_HASH256',
    OP_CODESEPARATOR : 'OP_CODESEPARATOR',
    OP_CHECKSIG : 'OP_CHECKSIG',
    OP_CHECKSIGVERIFY : 'OP_CHECKSIGVERIFY',
    OP_CHECKMULTISIG : 'OP_CHECKMULTISIG',
    OP_CHECKMULTISIGVERIFY : 'OP_CHECKMULTISIGVERIFY',
    OP_NOP1 : 'OP_NOP1',
    OP_NOP2 : 'OP_NOP2',
    OP_NOP3 : 'OP_NOP3',
    OP_NOP4 : 'OP_NOP4',
    OP_NOP5 : 'OP_NOP5',
    OP_NOP6 : 'OP_NOP6',
    OP_NOP7 : 'OP_NOP7',
    OP_NOP8 : 'OP_NOP8',
    OP_NOP9 : 'OP_NOP9',
    OP_NOP10 : 'OP_NOP10',
    OP_SMALLINTEGER : 'OP_SMALLINTEGER',
    OP_PUBKEYS : 'OP_PUBKEYS',
    OP_PUBKEYHASH : 'OP_PUBKEYHASH',
    OP_PUBKEY : 'OP_PUBKEY',
}

# ===----------------------------------------------------------------------===

class BaseScriptError(Exception):
    "Base class for all Script-related encode/decode exceptions"

class BaseScriptDecodeError(BaseScriptError):
    "Error while parsing bitcoin script"
class EmptyScriptError(BaseScriptDecodeError):
    "Attempted to retrieve opcode from empty script"
class MissingPushDataError(BaseScriptDecodeError):
    "End-of-script encountered while parsing multi-byte push code"

class ScriptOp(SerializableMixin, six.binary_type):
    def __new__(cls, opcode=None, data=None, *args, **kwargs):
        # If just data is specified, then we automatically fill-in the opcode
        # as required to push the data on the stack.
        if opcode is None and data:
            len_ = len(data)
            if 0 <= len_ < OP_PUSHDATA1:
                opcode = len_
            elif OP_PUSHDATA1 <= len_ <= 0xff:
                opcode = OP_PUSHDATA1
            elif 0xff < len_ < 0xffff:
                opcode = OP_PUSHDATA2
            elif 0xffff < len_ < 0xffffffff:
                opcode = OP_PUSHDATA4
            else:
                raise TypeError(u"pushed data exceeds maximum length")

        # The push opcode encodes the length of the data to be pushed, or
        # the size of the length which directly follows. In either case we
        # need to make sure the actual data length meets or does not exceed
        # this limit.
        if opcode==OP_INVALIDOPCODE:
            raise ValueError(u"invalid opcode")
        elif 0 < opcode < OP_PUSHDATA1 and opcode!=len(data):
            raise ValueError(u"opcode/data-length mismatch")
        elif (opcode==OP_PUSHDATA1 and len(data)>0xff or
              opcode==OP_PUSHDATA2 and len(data)>0xffff or
              opcode==OP_PUSHDATA4 and len(data)>0xffffffff):
            raise ValueError(u"data length exceeds serialization limit")

        result = pack('<B', opcode)
        if opcode == OP_PUSHDATA1:
            result += pack('<B', len(data))
        elif opcode == OP_PUSHDATA2:
            result += pack('<H', len(data))
        elif opcode == OP_PUSHDATA4:
            result += pack('<I', len(data))
        if 0 < opcode <= OP_PUSHDATA4:
            result += data

        return super(ScriptOp, cls).__new__(cls, result, *args, **kwargs)

    @property
    def opcode(self):
        return unpack('>B', self[:1])[0]

    @property
    def data(self):
        if self.opcode <= OP_PUSHDATA4:
            return self[1:]
        else:
            return None

    def serialize(self):
        return self
    @classmethod
    def deserialize(cls, file_):
        opcode = file_.read(1)
        if not len(opcode):
            raise EmptyScriptError
        opcode = unpack('<B', opcode)[0]

        datalen = 0
        if opcode < OP_PUSHDATA1:
            datalen = opcode
        elif opcode == OP_PUSHDATA1:
            datalen = unpack('<B', file_.read(1))[0]
        elif opcode == OP_PUSHDATA2:
            datalen = unpack('<H', file_.read(2))[0]
        elif opcode == OP_PUSHDATA4:
            datalen = unpack('<I', file_.read(4))[0]
        if datalen:
            data = file_.read(datalen)
        else:
            data = b''
        if len(data) != datalen:
            raise MissingPushDataError

        if 0 < opcode <= OP_PUSHDATA4:
            return cls(opcode, data=data)
        return cls(opcode)

    @property
    def boolean(self):
        if self.opcode == OP_0:
            return False
        if self.opcode == OP_1NEGATE:
            return True
        if OP_1 <= self.opcode <= OP_16:
            return True
        if self.opcode in xrange(1,OP_PUSHDATA4+1):
            return (
                any(map(lambda c:c!='\x00', self.data[:-1])) or
                self.data[-1] not in ('\x00', '\x80'))
        else:
            raise ValueError(u"non-data script-op cannot be interpreted as truth value")

    @boolean.setter
    def boolean(self, value):
        if value:
            self.opcode, self.data = OP_TRUE, None
        else:
            self.opcode, self.data = OP_FALSE, None

    @property
    def integral(self):
        if self.opcode == OP_1NEGATE:
            return -1
        elif self.opcode == OP_0:
            return 0
        elif OP_1 <= self.opcode <= OP_16:
            return self.opcode - OP_1 + 1
        elif self.opcode in xrange(1,OP_PUSHDATA4+1):
            data = self.data[:-1] + chr(ord(self.data[-1])&0x7f)
            bignum = deserialize_hash(StringIO(data), len(data))
            if ord(self.data[-1]) & 0x80:
                return -bignum
            return bignum
        else:
            raise ValueError(u"non-data script-op cannot be interpreted as integer")

    @integral.setter
    def integral(self, value):
        self.data = None
        if value == -1:
            self.opcode = OP_1NEGATE
        elif value == 0:
            self.opcode = OP_0
        elif 1 <= value <= 16:
            self.opcode = OP_1 + value - 1
        else:
            neg = value < 1
            absv = abs(value)
            data = serialize_hash(absv, 1+len(bin(long(absv)).rstrip('L')[2:])//8)
            if neg: data = data[:-1] + chr(ord(data[-1])|0x80)
            datalen = len(data)
            if datalen < OP_PUSHDATA1:
                self.opcode = datalen
            elif datalen <= 0xff:
                self.opcode = OP_PUSHDATA1
            elif datalen <= 0xffff:
                self.opcode = OP_PUSHDATA2
            elif datalen <= 0xffffffff:
                self.opcode = OP_PUSHDATA4
            else:
                raise ValueError(u"integer representation exceeds serialization limits")
            self.data = data

    def __repr__(self):
        data_str = ''.join([
            '\'',
            (self.data or '').encode('hex'),
            '\'.decode(\'hex\')'])
        if self.opcode>0 and self.opcode<=OP_PUSHDATA4:
            return data_str
        else:
            if self.opcode in OPCODE_NAMES and self.data is None:
                return OPCODE_NAMES[self.opcode]
            else:
                if self.data is None:
                    data_str = ''
                else:
                    data_str = ', data=' + data_str
                return 'ScriptOp(%d%s)' % (self.opcode, data_str)

# ===----------------------------------------------------------------------===

class Script(SerializableMixin, six.binary_type):
    def __iter__(self):
        script_op_class = getattr(self, 'get_script_op_class', lambda:
                          getattr(self, 'script_op_class', ScriptOp))()
        file_ = StringIO(self)
        while True:
            yield script_op_class.deserialize(file_)

    def serialize(self):
        return serialize_varchar(self)
    @classmethod
    def deserialize(cls, file_):
        return cls(deserialize_varchar(file_))

    def __repr__(self):
        try:
            return u"Script([%s])" % ', '.join(map(repr, self))
        except:
            return u"Script(\'%s\'.decode(\'hex\'))" % self.encode('hex')

# ===----------------------------------------------------------------------===

from .crypto import VerifyingKey
from .defaults import CLIENT_VERSION
from .serialize import SER_DISK, serialize_varint, deserialize_varchar
from .tools import StringIO

class ScriptPickler(object):
    """Compact serializer for scripts.

    It detects common cases and encodes them much more efficiently.
    3 special cases are defined:
      * Pay to pubkey hash (encoded as 21 bytes)
      * Pay to script hash (encoded as 21 bytes)
      * Pay to pubkey starting with 0x02, 0x03 or 0x04 (encoded as 33 bytes)

    Other scripts up to 121 bytes require 1 byte + script length. Above
    that, scripts up to 16505 bytes require 2 bytes + script length."""
    def __init__(self, file=None, protocol=SER_DISK, version=CLIENT_VERSION,
                 *args, **kwargs):
        if file is None: file = StringIO()
        super(ScriptPickler, self).__init__(*args, **kwargs)
        self._file = file
        self._protocol = protocol
        self._version = version

    @staticmethod
    def _dump(script, file_, protocol, version):
        if hasattr(script, 'serialize'):
            script = script.serialize()
            script = deserialize_varchar(StringIO(script))
        script_len = len(script)
        if 23 == script_len and all(
            script[k:k+1] == six.int2byte(v)
                    for k,v in six.iteritems({
                        0:  OP_HASH160,
                        1:  20,
                        22: OP_EQUAL})):
            str_ = b''.join([b'\x01', script[2:22]])
        elif 25 == script_len and all(
                script[k:k+1] == six.int2byte(v)
                    for k,v in six.iteritems({
                        0:  OP_DUP,
                        1:  OP_HASH160,
                        2:  20,
                        23: OP_EQUALVERIFY,
                        24: OP_CHECKSIG})):
            str_ = b''.join([b'\x00', script[3:23]])
        elif 35 == script_len and script[1:2] in map(six.int2byte, [2, 3]) and all(
                script[k:k+1] == six.int2byte(v)
                    for k,v in six.iteritems({
                        0:  33,
                        34: OP_CHECKSIG})):
            str_ = script[1:34]
        elif 67 == script_len and all(
                script[k:k+1] == six.int2byte(v)
                    for k,v in six.iteritems({
                        0:  65,
                        1:  4,
                        66: OP_CHECKSIG})):
            str_ = b''.join([six.int2byte(0x04 | ord(script[65:66])&0x01), script[2:34]])
        else:
            str_ = b''.join([serialize_varint(script_len + 0x06), script])
        file_.write(str_)

    @staticmethod
    def _load(file_, protocol, version):
        size = unpack("<B", file_.read(1))[0]
        if size == 0:
            hash_ = file_.read(20)
            return b''.join([
                six.int2byte(25),
                six.int2byte(OP_DUP),
                six.int2byte(OP_HASH160),
                six.int2byte(20), hash_,
                six.int2byte(OP_EQUALVERIFY),
                six.int2byte(OP_CHECKSIG),
            ])
        elif size == 1:
            hash_ = file_.read(20)
            return b''.join([
                six.int2byte(23),
                six.int2byte(OP_HASH160),
                six.int2byte(20), hash_,
                six.int2byte(OP_EQUAL),
            ])
        elif size in (2, 3):
            compressed_key = file_.read(32)
            return b''.join([
                six.int2byte(35),
                six.int2byte(33),
                six.int2byte(size),
                compressed_key,
                six.int2byte(OP_CHECKSIG),
            ])
        elif size in (4, 5):
            verifying_key = VerifyingKey.deserialize(StringIO(
                b''.join([six.int2byte(size-2), file_.read(32)])))
            verifying_key.compressed = False
            return b''.join([
                six.int2byte(67),
                six.int2byte(65),
                verifying_key.serialize(),
                six.int2byte(OP_CHECKSIG),
            ])
        elif size == 0xfd:
            size = unpack("<H", file_.read(2))[0]
        elif size == 0xfe:
            size = unpack("<I", file_.read(4))[0]
        elif size == 0xff:
            size = unpack("<Q", file_.read(8))[0]
        size = size - 6
        script = file_.read(size)
        return serialize_varchar(script)

    def get_script_class(self):
        return getattr(self, 'script_class', Script)

    def dump(self, script, file=None):
        "Write a compressed representation of script to the Pickler's file object."
        if file is None:
            file = self._file
        self._dump(script, file, self._protocol, self._version)

    def dumps(self, script):
        "Return a compressed representation of script as a binary string."
        string = StringIO()
        self._dump(script, string, self._protocol, self._version)
        return string.getvalue()

    def load(self, file=None):
        "Read and decompress a compact script from the Pickler's file object."
        if file is None:
            file = self._file
        script_class = self.get_script_class()
        script = self._load(file, self._protocol, self._version)
        return script_class.deserialize(StringIO(script))

    def loads(self, string):
        "Decompress the passed-in compact script and return the result."
        script_class = self.get_script_class()
        script = self._load(StringIO(string), self._protocol, self._version)
        return script_class.deserialize(StringIO(script))

ScriptUnpickler = ScriptPickler

# ===----------------------------------------------------------------------===

__all__ = OPCODE_NAMES.values() + [
    'OP_TRUE',
    'OP_FALSE',
    'OP_INVALIDOPCODE',
    'Script',
    'ScriptOp',
    'ScriptPickler',
    'ScriptUnpickler',
]

#
# End of File
#
