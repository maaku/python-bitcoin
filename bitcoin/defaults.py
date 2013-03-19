#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

from .core import ChainParameters
from .utils import target_from_compact, Constant, LinearArithmetic, SteppedGeometric

LOCKTIME_THRESHOLD = 500000000

CHAIN_PARAMETERS = {
    'org.bitcoin' : ChainParameters(
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
    'org.bitcoin.testnet3' : ChainParameters(
        magic = 'fabfb5da'.decode('hex'),
        port = 18333,
        genesis = (
            'AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAO6Pt/Xp7ErJ6xyw+Z3aPYX/IG8OI'
            'ilEyOp+4qkseXkra5UlN//8AHRqkrhgBAQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAP////9NBP//AB0BBEVUaGUgVGltZXMgMDMvSmFuLzIwMDkgQ2hhbmNlbGxvciBvbiBicmlu'
            'ayBvZiBzZWNvbmQgYmFpbG91dCBmb3IgYmFua3P/////AQDyBSoBAAAAQ0EEZ4r9sP5VSCcZZ/Gm'
            'cTC3EFzWqCjgOQmmeWLg6h9h3rZJ9rw/TO84xPNVBOUewRLeXDhN97oLjVeKTHAra/EdX6wAAAAA'
        ).decode('base64'),
        testnet = True,
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
    'org.dot-bit.namecoin' : ChainParameters(
        magic = 'f9beb4fe'.decode('hex'),
        port = 8334,
        genesis = (
            'AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADcvT5vBhIVvzszg8jOLsIBvGWs3j'
            'JZVEmshokL0txkHBM6pN/38AHJKhHqIBAQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAP////9UBP9/ABwCCgJLLi4uIGNob29zZSB3aGF0IGNvbWVzIG5leHQuICBMaXZlcyBvZiB5'
            'b3VyIG93biwgb3IgYSByZXR1cm4gdG8gY2hhaW5zLiAtLSBW/////wEA8gUqAQAAAENBBLYgNpBQ'
            'zYmf+7xOjuUejEU0qFW7RjQ51j0jXUd5aF2Lb0hwojjPNlrJT6E++aKiLNmdDV7obcq8r842x6z0'
            'POWsAAAAAA=='
        ).decode('base64'),
        testnet = False,
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
            0:     0x000000000062b72c5e2ceb45fbc8587e807c155b0da735e6483dfba2f0a9c770L,
            2016:  0x0000000000660bad0d9fbde55ba7ee14ddf766ed5f527e3fbca523ac11460b92L,
            4032:  0x0000000000493b5696ad482deb79da835fe2385304b841beef1938655ddbc411L,
            6048:  0x000000000027939a2e1d8bb63f36c47da858e56d570f143e67e85068943470c9L,
            8064:  0x000000000003a01f708da7396e54d081701ea406ed163e519589717d8b7c95a5L,
            10080: 0x00000000000fed3899f818b2228b4f01b9a0a7eeee907abd172852df71c64b06L,
            12096: 0x0000000000006c06988ff361f124314f9f4bb45b6997d90a7ee4cedf434c670fL,
            14112: 0x00000000000045d95e0588c47c17d593c7b5cb4fb1e56213d1b3843c1773df2bL,
            16128: 0x000000000001d9964f9483f9096cf9d6c6c2886ed1e5dec95ad2aeec3ce72fa9L,
            18940: 0x00000000000087f7fc0c8085217503ba86f796fa4984f7e5a08b6c4c12906c05L,
            30240: 0xe1c8c862ff342358384d4c22fa6ea5f669f3e1cdcf34111f8017371c3c0be1daL,
            57000: 0xaa3ec60168a0200799e362e2b572ee01f3c3852030d07d036e0aa884ec61f203L,
        },
        features = {}),
    'in.freico' : ChainParameters(
        magic = 'c7d32389'.decode('hex'),
        port = 8639,
        genesis = (
            'AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtgN4/8leZxiafMA6JQwtK5IyLyLQ'
            'Y/Ya1KexQ5+r5D+QYlNQ//8AHecX/DcBAgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAP////9NBP//AB0BBEVUZWxlZ3JhcGggMjcvSnVuLzIwMTIgQmFyY2xheXMgaGl0IHdpdGgg'
            'wqMyOTBtIGZpbmUgb3ZlciBMaWJvciBmaXhpbmf/////AUeLBhg7BwAAQ0EEZ4r9sP5VSCcZZ/Gm'
            'cTC3EFzWqCjgOQmmeWLg6h9h3rZJ9rw/TO84xPNVBOUewRLeXDhN97oLjVeKTHAra/EdX6wAAAAA'
            'AAAAAA=='
        ).decode('base64'),
        testnet = False,
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
