# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

from bitcoin.address import *
from bitcoin.errors import Base58Error

# ===----------------------------------------------------------------------===

from bitcoin.script import *

BITCOIN_ADDRESS = [
    # Valid addresses
    dict(version  = BitcoinAddress.PUBKEY_HASH,
         hash     = 533613946177287109634438767478602490652520581919L,
         base58   = u"13snZ4ZyCzaL7358SmgvHGC9AxskqumNxP",
         script   = Script().join([
                        ScriptOp(OP_DUP),
                        ScriptOp(OP_HASH160),
                        ScriptOp(data='1f8b1340c286881bcc449c37569ae320b013785d'.decode('hex')),
                        ScriptOp(OP_EQUALVERIFY),
                        ScriptOp(OP_CHECKSIG),
                    ])),
    dict(version  = BitcoinAddress.SCRIPT_HASH,
         hash     = 1439889050650639417403043439503616658465773899358L,
         base58   = u"3ALJH9Y951VCGcVZYAdpA3KchoP9McEj1G",
         script   = Script().join([
                        ScriptOp(OP_HASH160),
                        ScriptOp(data='5ece0cadddc415b1980f001785947120acdb36fc'.decode('hex')),
                        ScriptOp(OP_EQUAL),
                    ])),
    # Null addresses
    dict(version  = BitcoinAddress.PUBKEY_HASH,
         hash     = 0,
         base58   = u"1111111111111111111114oLvT2",
         script   = Script().join([
                        ScriptOp(OP_DUP),
                        ScriptOp(OP_HASH160),
                        ScriptOp(data='\x00'*20),
                        ScriptOp(OP_EQUALVERIFY),
                        ScriptOp(OP_CHECKSIG),
                    ])),
    dict(version  = BitcoinAddress.SCRIPT_HASH,
         hash     = 0,
         base58   = u"31h1vYVSYuKP6AhS86fbRdMw9XHieotbST",
         script   = Script().join([
                        ScriptOp(OP_HASH160),
                        ScriptOp(data='\x00'*20),
                        ScriptOp(OP_EQUAL),
                    ])),
]

class TestBitcoinAddress(unittest2.TestCase):
    "Test base58 bitcoin addresses"
    __metaclass__ = ScenarioMeta
    class test_init_from_base58(ScenarioTest):
        scenarios = BITCOIN_ADDRESS
        def __test__(self, version, hash, base58, script):
            data = base58.decode('base58')
            address = BitcoinAddress(data)
            self.assertEqual(address, data)
            self.assertEqual(address.hash, hash)
            self.assertEqual(address.destination.script, script)
            address = BitcoinAddress(data=data, add_hash=False)
            self.assertEqual(address, data)
            self.assertEqual(address.hash, hash)
            self.assertEqual(address.destination.script, script)
            address = BitcoinAddress(data=data[:-4], add_hash=True)
            self.assertEqual(address, data)
            self.assertEqual(address.hash, hash)
            self.assertEqual(address.destination.script, script)
    class test_init_from_version_hash(ScenarioTest):
        scenarios = BITCOIN_ADDRESS
        def __test__(self, version, hash, base58, script):
            address = BitcoinAddress(hash)
            self.assertEqual(address.version, BitcoinAddress.SCRIPT_HASH)
            self.assertEqual(address.hash, hash)
            address = BitcoinAddress(hash, version=version)
            self.assertEqual(address, base58.decode('base58'))
            self.assertEqual(address.hash, hash)
            self.assertEqual(address.destination.script, script)
    class test_nonzero(ScenarioTest):
        scenarios = BITCOIN_ADDRESS
        def __test__(self, version, hash, base58, script):
            address = BitcoinAddress(base58.decode('base58'))
            self.assertEqual(bool(hash), bool(address))

INVALID_ADDRESSES = [
    # From "base58_keys_invalid.json"
    dict(address=u""),
    dict(address=u"x"),
    dict(address=u"37qgekLpCCHrQuSjvX3fs496FWTGsHFHizjJAs6NPcR47aefnnCWECAhHV6E3g4YN7u7Yuwod5Y"),
    dict(address=u"dzb7VV1Ui55BARxv7ATxAtCUeJsANKovDGWFVgpTbhq9gvPqP3yv"),
    dict(address=u"MuNu7ZAEDFiHthiunm7dPjwKqrVNCM3mAz6rP9zFveQu14YA8CxExSJTHcVP9DErn6u84E6Ej7S"),
    dict(address=u"rPpQpYknyNQ5AEHuY6H8ijJJrYc2nDKKk9jjmKEXsWzyAQcFGpDLU2Zvsmoi8JLR7hAwoy3RQWf"),
    dict(address=u"4Uc3FmN6NQ6zLBK5QQBXRBUREaaHwCZYsGCueHauuDmJpZKn6jkEskMB2Zi2CNgtb5r6epWEFfUJq"),
    dict(address=u"7aQgR5DFQ25vyXmqZAWmnVCjL3PkBcdVkBUpjrjMTcghHx3E8wb"),
    dict(address=u"17QpPprjeg69fW1DV8DcYYCKvWjYhXvWkov6MJ1iTTvMFj6weAqW7wybZeH57WTNxXVCRH4veVs"),
    dict(address=u"KxuACDviz8Xvpn1xAh9MfopySZNuyajYMZWz16Dv2mHHryznWUp3"),
    dict(address=u"7nK3GSmqdXJQtdohvGfJ7KsSmn3TmGqExug49583bDAL91pVSGq5xS9SHoAYL3Wv3ijKTit65th"),
    dict(address=u"cTivdBmq7bay3RFGEBBuNfMh2P1pDCgRYN2Wbxmgwr4ki3jNUL2va"),
    dict(address=u"gjMV4vjNjyMrna4fsAr8bWxAbwtmMUBXJS3zL4NJt5qjozpbQLmAfK1uA3CquSqsZQMpoD1g2nk"),
    dict(address=u"emXm1naBMoVzPjbk7xpeTVMFy4oDEe25UmoyGgKEB1gGWsK8kRGs"),
    dict(address=u"7VThQnNRj1o3Zyvc7XHPRrjDf8j2oivPTeDXnRPYWeYGE4pXeRJDZgf28ppti5hsHWXS2GSobdqyo"),
    dict(address=u"1G9u6oCVCPh2o8m3t55ACiYvG1y5BHewUkDSdiQarDcYXXhFHYdzMdYfUAhfxn5vNZBwpgUNpso"),
    dict(address=u"31QQ7ZMLkScDiB4VyZjuptr7AEc9j1SjstF7pRoLhHTGkW4Q2y9XELobQmhhWxeRvqcukGd1XCq"),
    dict(address=u"DHqKSnpxa8ZdQyH8keAhvLTrfkyBMQxqngcQA5N8LQ9KVt25kmGN"),
    dict(address=u"2LUHcJPbwLCy9GLH1qXmfmAwvadWw4bp4PCpDfduLqV17s6iDcy1imUwhQJhAoNoN1XNmweiJP4i"),
    dict(address=u"7USRzBXAnmck8fX9HmW7RAb4qt92VFX6soCnts9s74wxm4gguVhtG5of8fZGbNPJA83irHVY6bCos"),
    dict(address=u"1DGezo7BfVebZxAbNT3XGujdeHyNNBF3vnficYoTSp4PfK2QaML9bHzAMxke3wdKdHYWmsMTJVu"),
    dict(address=u"2D12DqDZKwCxxkzs1ZATJWvgJGhQ4cFi3WrizQ5zLAyhN5HxuAJ1yMYaJp8GuYsTLLxTAz6otCfb"),
    dict(address=u"8AFJzuTujXjw1Z6M3fWhQ1ujDW7zsV4ePeVjVo7D1egERqSW9nZ"),
    dict(address=u"163Q17qLbTCue8YY3AvjpUhotuaodLm2uqMhpYirsKjVqnxJRWTEoywMVY3NbBAHuhAJ2cF9GAZ"),
    dict(address=u"2MnmgiRH4eGLyLc9eAqStzk7dFgBjFtUCtu"),
    dict(address=u"461QQ2sYWxU7H2PV4oBwJGNch8XVTYYbZxU"),
    dict(address=u"2UCtv53VttmQYkVU4VMtXB31REvQg4ABzs41AEKZ8UcB7DAfVzdkV9JDErwGwyj5AUHLkmgZeobs"),
    dict(address=u"cSNjAsnhgtiFMi6MtfvgscMB2Cbhn2v1FUYfviJ1CdjfidvmeW6mn"),
    dict(address=u"gmsow2Y6EWAFDFE1CE4Hd3Tpu2BvfmBfG1SXsuRARbnt1WjkZnFh1qGTiptWWbjsq2Q6qvpgJVj"),
    dict(address=u"nksUKSkzS76v8EsSgozXGMoQFiCoCHzCVajFKAXqzK5on9ZJYVHMD5CKwgmX3S3c7M1U3xabUny"),
    dict(address=u"L3favK1UzFGgdzYBF2oBT5tbayCo4vtVBLJhg2iYuMeePxWG8SQc"),
    dict(address=u"7VxLxGGtYT6N99GdEfi6xz56xdQ8nP2dG1CavuXx7Rf2PrvNMTBNevjkfgs9JmkcGm6EXpj8ipyPZ"),
    dict(address=u"2mbZwFXF6cxShaCo2czTRB62WTx9LxhTtpP"),
    dict(address=u"dB7cwYdcPSgiyAwKWL3JwCVwSk6epU2txw"),
    dict(address=u"HPhFUhUAh8ZQQisH8QQWafAxtQYju3SFTX"),
    dict(address=u"4ctAH6AkHzq5ioiM1m9T3E2hiYEev5mTsB"),
    dict(address=u"Hn1uFi4dNexWrqARpjMqgT6cX1UsNPuV3cHdGg9ExyXw8HTKadbktRDtdeVmY3M1BxJStiL4vjJ"),
    dict(address=u"Sq3fDbvutABmnAHHExJDgPLQn44KnNC7UsXuT7KZecpaYDMU9Txs"),
    dict(address=u"6TqWyrqdgUEYDQU1aChMuFMMEimHX44qHFzCUgGfqxGgZNMUVWJ"),
    dict(address=u"giqJo7oWqFxNKWyrgcBxAVHXnjJ1t6cGoEffce5Y1y7u649Noj5wJ4mmiUAKEVVrYAGg2KPB3Y4"),
    dict(address=u"cNzHY5e8vcmM3QVJUcjCyiKMYfeYvyueq5qCMV3kqcySoLyGLYUK"),
    dict(address=u"37uTe568EYc9WLoHEd9jXEvUiWbq5LFLscNyqvAzLU5vBArUJA6eydkLmnMwJDjkL5kXc2VK7ig"),
    dict(address=u"EsYbG4tWWWY45G31nox838qNdzksbPySWc"),
    dict(address=u"nbuzhfwMoNzA3PaFnyLcRxE9bTJPDkjZ6Rf6Y6o2ckXZfzZzXBT"),
    dict(address=u"cQN9PoxZeCWK1x56xnz6QYAsvR11XAce3Ehp3gMUdfSQ53Y2mPzx"),
    dict(address=u"1Gm3N3rkef6iMbx4voBzaxtXcmmiMTqZPhcuAepRzYUJQW4qRpEnHvMojzof42hjFRf8PE2jPde"),
    dict(address=u"2TAq2tuN6x6m233bpT7yqdYQPELdTDJn1eU"),
    dict(address=u"ntEtnnGhqPii4joABvBtSEJG6BxjT2tUZqE8PcVYgk3RHpgxgHDCQxNbLJf7ardf1dDk2oCQ7Cf"),
    dict(address=u"Ky1YjoZNgQ196HJV3HpdkecfhRBmRZdMJk89Hi5KGfpfPwS2bUbfd"),
    dict(address=u"2A1q1YsMZowabbvta7kTy2Fd6qN4r5ZCeG3qLpvZBMzCixMUdkN2Y4dHB1wPsZAeVXUGD83MfRED"),
]

class TestInvalidAddresses(unittest2.TestCase):
    "Test invalid bitcoin addresses"
    __metaclass__ = ScenarioMeta
    class test_invalid_address(ScenarioTest):
        scenarios = INVALID_ADDRESSES
        def __test__(self, address):
            with self.assertRaises(InvalidAddressError):
                try:
                    BitcoinAddress(address.decode('base58'))
                except Base58Error:
                    raise InvalidAddressError(Base58Error)

#
# End of File
#
