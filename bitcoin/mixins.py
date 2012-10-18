#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === bitcoin.mixins ------------------------------------------------------===
# Copyright © 2012 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
# ===----------------------------------------------------------------------===

__all__ = [
    'SerializableMixin',
]

# ===----------------------------------------------------------------------===

from types import MethodType

class SerializableMixin(object):
    def __init__(self, *args, **kwargs):
        super(SerializableMixin, self).__init__(*args, **kwargs)
        self.deserialize = MethodType(self.deserialize, self, self.__class__)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
