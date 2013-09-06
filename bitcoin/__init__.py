# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

VERSION = (0,0,7, 'final', 0)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%spre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = "%s%s" % (version, VERSION[3])
            if VERSION[4] != 0:
                version = '%s%s' % (version, VERSION[4])
    return version

#
# End of File
#
