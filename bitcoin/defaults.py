# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

CLIENT_VERSION_MAJOR    = 0
CLIENT_VERSION_MINOR    = 8
CLIENT_VERSION_REVISION = 2
CLIENT_VERSION_BUILD    = 2
CLIENT_VERSION = (  1000000 * CLIENT_VERSION_MAJOR
                  +   10000 * CLIENT_VERSION_MINOR
                  +     100 * CLIENT_VERSION_REVISION
                  +       1 * CLIENT_VERSION_BUILD)

LOCKTIME_THRESHOLD = 500000000

from .core import ChainParameters
from .tools import target_from_compact, Constant, LinearArithmetic, SteppedGeometric

CHAIN_PARAMETERS = {
    'bitcoin.org' : ChainParameters(
        magic = 'f9beb4d9'.decode('hex'),
        port = 8333,
        genesis = (
            'AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAO6Pt/Xp7ErJ6xyw+Z3aPYX/IG8OI'
            'ilEyOp+4qkseXkopq19J//8AHR2sK3wBAQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAP////9NBP//AB0BBEVUaGUgVGltZXMgMDMvSmFuLzIwMDkgQ2hhbmNlbGxvciBvbiBicmlu'
            'ayBvZiBzZWNvbmQgYmFpbG91dCBmb3IgYmFua3P/////AQDyBSoBAAAAQ0EEZ4r9sP5VSCcZZ/Gm'
            'cTC3EFzWqCjgOQmmeWLg6h9h3rZJ9rw/TO84xPNVBOUewRLeXDhN97oLjVeKTHAra/EdX6wAAAAA'
        ).decode('base64'),
        testnet = False,
        pubkey_hash_prefix = 0,
        script_hash_prefix = 5,
        secret_prefix = 128,
        max_value = 2100000000000000L,
        transient_reward = SteppedGeometric(50*100000000, 210000),
        transient_budget = lambda *args, **kwargs:(0, {}),
        perpetual_reward = Constant(0),
        perpetual_budget = lambda *args, **kwargs:(0, {}),
        fee_budget = lambda *args, **kwargs:(0, {}),
        maximum_target = target_from_compact(0x1d00ffff),
        next_target = lambda *args, **kwargs:0,
        alert_keys = [],
        checkpoints = {
            0:      0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26fL,
            11111:  0x0000000069e244f73d78e8fd29ba2fd2ed618bd6fa2ee92559f542fdb26e7c1dL,
            33333:  0x000000002dd5588a74784eaa7ab0507a18ad16a236e7b1ce69f00d7ddfb5d0a6L,
            74000:  0x0000000000573993a3c9e41ce34471c079dcf5f52a0e824a81e7f953b8661a20L,
            105000: 0x00000000000291ce28027faea320c8d2b054b2e0fe44a773f3eefb151d6bdc97L,
            134444: 0x00000000000005b12ffd4cd315cd34ffd4a594f430ac814c91184a0d42d2b0feL,
            168000: 0x000000000000099e61ea72015e79632f216fe6cb33d7899acb35b75c8303b763L,
            193000: 0x000000000000059f452a5f7340de6682a977387c17010ff6e6c3bd83ca8b1317L,
            210000: 0x000000000000048b95347e83192f69cf0366076336c639f9b7228e9ba171342eL,
            216116: 0x00000000000001b4f4b433e81ee46494af945cf96014816a4e2370f11b23df4eL,
            225430: 0x00000000000001c108384350f74090433e7fcf79a606b8e797f065b130575932L,
        },
        features = {}),
    'testnet3.bitcoin.org' : ChainParameters(
        magic = '0b110907'.decode('hex'),
        port = 18333,
        genesis = (
            'AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAO6Pt/Xp7ErJ6xyw+Z3aPYX/IG8OI'
            'ilEyOp+4qkseXkra5UlN//8AHRqkrhgBAQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAP////9NBP//AB0BBEVUaGUgVGltZXMgMDMvSmFuLzIwMDkgQ2hhbmNlbGxvciBvbiBicmlu'
            'ayBvZiBzZWNvbmQgYmFpbG91dCBmb3IgYmFua3P/////AQDyBSoBAAAAQ0EEZ4r9sP5VSCcZZ/Gm'
            'cTC3EFzWqCjgOQmmeWLg6h9h3rZJ9rw/TO84xPNVBOUewRLeXDhN97oLjVeKTHAra/EdX6wAAAAA'
        ).decode('base64'),
        testnet = True,
        pubkey_hash_prefix = 111,
        script_hash_prefix = 196,
        secret_prefix = 239,
        max_value = 2100000000000000L,
        transient_reward = SteppedGeometric(50*100000000, 210000),
        transient_budget = lambda *args, **kwargs:(0, {}),
        perpetual_reward = Constant(0),
        perpetual_budget = lambda *args, **kwargs:(0, {}),
        fee_budget = lambda *args, **kwargs:(0, {}),
        maximum_target = target_from_compact(0x1d00ffff),
        next_target = lambda *args, **kwargs:0,
        alert_keys = [],
        checkpoints = {
            0:   0x000000000933ea01ad0ee984209779baaec3ced90fa3f408719526f8d77f4943L,
            546: 0x000000002a936ca763904c3c35fce2f3556c559c0214345d31b1bcebf76acb70L,
        },
        features = {}),
    'freico.in' : ChainParameters(
        magic = '2cfe7e6d'.decode('hex'),
        port = 8639,
        genesis = (
            'AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAvcj0mpGkU1oV92tIbMn+DXC9qogS'
            '9YzoC6Qel6obO/XQzdRQ//8AHWpylRABAgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAP////9NBP//AB0BBEVUZWxlZ3JhcGggMjcvSnVuLzIwMTIgQmFyY2xheXMgaGl0IHdpdGgg'
            'wqMyOTBtIGZpbmUgb3ZlciBMaWJvciBmaXhpbmf/////CIk0KO0FAAAAQ0EEZ4r9sP5VSCcZZ/Gm'
            'cTC3EFzWqCjgOQmmeWLg6h9h3rZJ9rw/TO84xPNVBOUewRLeXDhN97oLjVeKTHAra/EdX6wBAAAA'
            'AAAAACMgUCnRgODF7XmNh3sa2pl3KYbBQiypMsQbLQQAAAAAAAB1AAEAAAAAAAAA/VMBAyAgIHVN'
            'MQFNZXRhbHMgd2VyZSBhbiBpbXBsaWNpdGx5IGFidXNpdmUgYWdyZWVtZW50LgpNb2Rlcm4gInBh'
            'cGVyIiBpcyBhIGZsYXdlZCB0b29sLCBpdHMgZW5naW5lZXJpbmcgaXMgYSBuZXN0IG9mIGxlZWNo'
            'ZXMuClRoZSBvbGQgbW9uZXkgaXMgb2Jzb2xldGUuCkxldCB0aGUgaW5kaXZpZHVhbCBtb25ldGl6'
            'ZSBpdHMgY3JlZGl0IHdpdGhvdXQgY2FydGVsIGludGVybWVkaWFyaWVzLgpHaXZlIHVzIGEgcmVu'
            'dC1sZXNzIGNhc2ggc28gd2UgY2FuIGJlIGZyZWUgZm9yIHRoZSBmaXJzdCB0aW1lLgpMZXQgdGhp'
            'cyBiZSB0aGUgYXdhaXRlZCBkYXduLnV2qRQO8PnRmmUwI1VBRqhmI4uIIryE34isAQAAAAAAAAD6'
            'CCAgICAgICAgdUzUIkxldCB1cyBjYWxjdWxhdGUsIHdpdGhvdXQgZnVydGhlciBhZG8sIGluIG9y'
            'ZGVyIHRvIHNlZSB3aG8gaXMgcmlnaHQuIiAtLUdvdHRmcmllZCBXaWxoZWxtIExlaWJuaXoKzr7C'
            'tO+9peKIgO+9pWDvvInjgIDjgIDjgIDjgIAgIG4K77+j44CA44CA44CAICDvvLzjgIDjgIAgIO+8'
            'iCBF77yJIGdvb2Qgam9iLCBtYWFrdSEK776M44CA44CA44CAICAv44O9IOODvV/vvI/vvI91dqkU'
            'wmvl7ICapL9rMKqJgjz/fO3DZ5qIrAEAAAAAAAAAXwYgICAgICB1PEljaCB3w7xuc2NoZSBGcmVp'
            'Y29pbiB2aWVsIEVyZm9sZyB6dW0gTnV0emVuIGRlciA5OSBQcm96ZW50IXV2qRQpOazWADcoGnCO'
            'sR5OntpFLAKeyoisAQAAAAAAAACYDSAgICAgICAgICAgICB1TG0iVGhlIHZhbHVlIG9mIGEgbWFu'
            'IHNob3VsZCBiZSBzZWVuIGluIHdoYXQgaGUgZ2l2ZXMgYW5kIG5vdCBpbiB3aGF0IGhlIGlzIGFi'
            'bGUgdG8gcmVjZWl2ZS4iIC0tQWxiZXJ0IEVpbnN0ZWludXapFPnKXKq0vaTcKLVVaqeaLuwER/C/'
            'iKwBAAAAAAAAAIAMICAgICAgICAgICAgdUxWIkFuIGFybXkgb2YgcHJpbmNpcGxlcyBjYW4gcGVu'
            'ZXRyYXRlIHdoZXJlIGFuIGFybXkgb2Ygc29sZGllcnMgY2Fubm90LiIgLS1UaG9tYXMgUGFpbmV1'
            'dqkUCPMgy7QaGuJbeU9hdflggGgZifOIrMxglIwLAAAAGXapFIXlQUTEAgpl+gqP26yLunXbwv0A'
            'iKwAAAAAAAAAAA=='
        ).decode('base64'),
        testnet = False,
        pubkey_hash_prefix = 0,
        script_hash_prefix = 5,
        secret_prefix = 128,
        max_value = 9999999999999999L,
        transient_reward = LinearArithmetic(50*100000000, 210000),
        transient_budget = lambda *args, **kwargs:(0, {}),
        perpetual_reward = Constant(0),
        perpetual_budget = lambda *args, **kwargs:(0, {}),
        fee_budget = lambda *args, **kwargs:(0, {}),
        maximum_target = target_from_compact(0x1d00ffff),
        next_target = lambda *args, **kwargs:0,
        alert_keys = [],
        checkpoints = {
            0:     0x000000000c29f26697c30e29039927ab4241b5fc2cc76db7e0dafa5e2612ad46L,
            10080: 0x00000000003ff9c4b806639ec4376cc9acafcdded0e18e9dbcc2fc42e8e72331L,
            15779: 0x000000000003eb31742b35f5efd8ffb5cdd19dcd8e82cdaad90e592c450363b6L,
        },
        features = {}),
    'testnet.freico.in' : ChainParameters(
        magic = '5ed67cf3'.decode('hex'),
        port = 18639,
        genesis = (
            'AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAvcj0mpGkU1oV92tIbMn+DXC9qogS'
            '9YzoC6Qel6obO/XQzdRQ//8AHfF1q7gBAgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAP////9NBP//AB0BBEVUZWxlZ3JhcGggMjcvSnVuLzIwMTIgQmFyY2xheXMgaGl0IHdpdGgg'
            'wqMyOTBtIGZpbmUgb3ZlciBMaWJvciBmaXhpbmf/////CIk0KO0FAAAAQ0EEZ4r9sP5VSCcZZ/Gm'
            'cTC3EFzWqCjgOQmmeWLg6h9h3rZJ9rw/TO84xPNVBOUewRLeXDhN97oLjVeKTHAra/EdX6wBAAAA'
            'AAAAACMgUCnRgODF7XmNh3sa2pl3KYbBQiypMsQbLQQAAAAAAAB1AAEAAAAAAAAA/VMBAyAgIHVN'
            'MQFNZXRhbHMgd2VyZSBhbiBpbXBsaWNpdGx5IGFidXNpdmUgYWdyZWVtZW50LgpNb2Rlcm4gInBh'
            'cGVyIiBpcyBhIGZsYXdlZCB0b29sLCBpdHMgZW5naW5lZXJpbmcgaXMgYSBuZXN0IG9mIGxlZWNo'
            'ZXMuClRoZSBvbGQgbW9uZXkgaXMgb2Jzb2xldGUuCkxldCB0aGUgaW5kaXZpZHVhbCBtb25ldGl6'
            'ZSBpdHMgY3JlZGl0IHdpdGhvdXQgY2FydGVsIGludGVybWVkaWFyaWVzLgpHaXZlIHVzIGEgcmVu'
            'dC1sZXNzIGNhc2ggc28gd2UgY2FuIGJlIGZyZWUgZm9yIHRoZSBmaXJzdCB0aW1lLgpMZXQgdGhp'
            'cyBiZSB0aGUgYXdhaXRlZCBkYXduLnV2qRQO8PnRmmUwI1VBRqhmI4uIIryE34isAQAAAAAAAAD6'
            'CCAgICAgICAgdUzUIkxldCB1cyBjYWxjdWxhdGUsIHdpdGhvdXQgZnVydGhlciBhZG8sIGluIG9y'
            'ZGVyIHRvIHNlZSB3aG8gaXMgcmlnaHQuIiAtLUdvdHRmcmllZCBXaWxoZWxtIExlaWJuaXoKzr7C'
            'tO+9peKIgO+9pWDvvInjgIDjgIDjgIDjgIAgIG4K77+j44CA44CA44CAICDvvLzjgIDjgIAgIO+8'
            'iCBF77yJIGdvb2Qgam9iLCBtYWFrdSEK776M44CA44CA44CAICAv44O9IOODvV/vvI/vvI91dqkU'
            'wmvl7ICapL9rMKqJgjz/fO3DZ5qIrAEAAAAAAAAAXwYgICAgICB1PEljaCB3w7xuc2NoZSBGcmVp'
            'Y29pbiB2aWVsIEVyZm9sZyB6dW0gTnV0emVuIGRlciA5OSBQcm96ZW50IXV2qRQpOazWADcoGnCO'
            'sR5OntpFLAKeyoisAQAAAAAAAACYDSAgICAgICAgICAgICB1TG0iVGhlIHZhbHVlIG9mIGEgbWFu'
            'IHNob3VsZCBiZSBzZWVuIGluIHdoYXQgaGUgZ2l2ZXMgYW5kIG5vdCBpbiB3aGF0IGhlIGlzIGFi'
            'bGUgdG8gcmVjZWl2ZS4iIC0tQWxiZXJ0IEVpbnN0ZWludXapFPnKXKq0vaTcKLVVaqeaLuwER/C/'
            'iKwBAAAAAAAAAIAMICAgICAgICAgICAgdUxWIkFuIGFybXkgb2YgcHJpbmNpcGxlcyBjYW4gcGVu'
            'ZXRyYXRlIHdoZXJlIGFuIGFybXkgb2Ygc29sZGllcnMgY2Fubm90LiIgLS1UaG9tYXMgUGFpbmV1'
            'dqkUCPMgy7QaGuJbeU9hdflggGgZifOIrMxglIwLAAAAGXapFIXlQUTEAgpl+gqP26yLunXbwv0A'
            'iKwAAAAAAAAAAA=='
        ).decode('base64'),
        testnet = False,
        pubkey_hash_prefix = 111,
        script_hash_prefix = 196,
        secret_prefix = 239,
        max_value = 9999999999999999L,
        transient_reward = LinearArithmetic(50*100000000, 210000),
        transient_budget = lambda *args, **kwargs:(0, {}),
        perpetual_reward = Constant(0),
        perpetual_budget = lambda *args, **kwargs:(0, {}),
        fee_budget = lambda *args, **kwargs:(0, {}),
        maximum_target = target_from_compact(0x1d00ffff),
        next_target = lambda *args, **kwargs:0,
        alert_keys = [],
        checkpoints = {
            0:     0x000000000c29f26697c30e29039927ab4241b5fc2cc76db7e0dafa5e2612ad46L,
            10080: 0x00000000003ff9c4b806639ec4376cc9acafcdded0e18e9dbcc2fc42e8e72331L,
            15779: 0x000000000003eb31742b35f5efd8ffb5cdd19dcd8e82cdaad90e592c450363b6L,
        },
        features = {}),
}

#
# End of File
#
