# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import time
from random import randrange
from hashlib import sha1
import requests
import six

try:
    import json
except:
    try:
        import simplejson as json
    except:
        import django.utils.simplejson as json

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from .numeric import mpd

from .serialize import serialize_hash, deserialize_hash

__all__ = [
    'ResponseError',
    'Fault',
    'boolean',
    'Boolean',
    'True',
    'False',
    'RESPONSE',
    'dumps',
    'loads',
    'Proxy',
]

#
# :exc:`ResponseError` is raised in the case of a malformed response.
#
class ResponseError(Exception):
    "Indicates a broken response package."
    pass

#
# :exc:`Fault` represents a JSON-RPC fault code and descriptive string. It is
# used as an exception when a single request-response returns an error, and in
# batch processing and elsewhere as a representation of JSON-RPC fault codes.
#
class Fault(Exception):
    "Indicates an JSON-RPC error code."
    def __init__(self, faultCode=-1, faultString=None, faultDescription=None,
                 *args, **kwargs):
        if faultString is None: faultString = ''
        super(Fault, self).__init__(self, *args, **kwargs)
        self.faultCode = faultCode
        self.faultString = faultString
        self.faultDescription = faultDescription
    def __repr__(self):
        if self.faultDescription is None:
            return "<Fault %s: %s>" % (self.faultCode, repr(self.faultString))
        else:
            return "<Fault %s: %s (%s)>" % (self.faultCode,
                repr(self.faultString), repr(self.faultDescription))

#
# boolean(value)
#
# Convert any Python value to one of the JSON-RPC Boolean constants,
# :const:`True` or :const:`False`.
#
from sys import modules
mod_dict = modules[__name__].__dict__
boolean = Boolean = bool
mod_dict['True'] = True
mod_dict['False'] = False
del modules, mod_dict

#
# dumps(id, method, params)
#
# Convert *params* into a numbered JSON-RPC request, or into a response if
# *method* is :const:`RESPONSE`. *params* can be either a list, tuple, or
# dictionary of arguments, a single JSON-representable value, or an instance
# of the :exc:`Fault` exception class.
#
RESPONSE = object()
def dumps(id, method, params):
    jsonargs = dict(jsonrpc='2.0',id=id)
    if isinstance(params, Fault):
        jsonargs.update({'error': {
            'code': params.faultCode,
            'message': params.faultString,
        }})
        if params.faultDescription is not None:
            jsonargs['error'].update({'data': params.faultDescription})
    elif method is RESPONSE:
        jsonargs.update({'result': params})
    else:
        jsonargs.update({'method': method})
        jsonargs.update({'params': params})
    return json.dumps(jsonargs, ensure_ascii=False).encode('utf-8')

#
# loads(payload)
#
# Convert an JSON-RPC request or response into Python objects, an `(id,
# method, paramsresponse)` tuple.
#
def loads(payload):
    return json.loads(payload, parse_float=mpd)

#
# A proxy object manages communication with a remote bitcoind JSON-RPC server.
#
class Proxy(object):
    def __init__(self, uri, username=None, password=None, service=None,
                 timeout=15, *args, **kwargs):
        if username is None: username = 'rpcuser'
        if password is None: password = ''
        if isinstance(uri, six.text_type): uri = uri.encode('utf-8')
        if isinstance(password, six.text_type): password = password.encode('utf-8')
        if isinstance(username, six.text_type): username = username.encode('utf-8')
        if isinstance(service, six.text_type): service = service.encode('utf-8')
        super(Proxy, self).__init__(*args, **kwargs)
        self._ctr = 0
        self.uri = uri
        self.service = service
        self.username = username
        self.password = password
        self.timeout = timeout

    def __getattr__(self, name):
        if self.service is not None:
            name = '.'.join([self.service, name])
        return self.__class__(self.uri, self.username, self.password, name,
                              self.timeout)

    def __call__(self, *args, **kwargs):
        if args and kwargs:
            raise ValueError(
                u"JSON-RPC allows encoding of either positional or keyword "
                u"parameters, but not both")
        if self.service is None:
            raise ValueError(u"must specify JSON-RPC method")

        # Generate a pseudo-random numeric identifier for this request:
        self._ctr = (self._ctr+1) & 0xffffffff
        hash_ = sha1(b''.join([
            self.uri, self.service, self.username,
            serialize_hash(self._ctr, 4), time.ctime(),
            serialize_hash(randrange(2**32), 4)])).digest()
        id_ = deserialize_hash(StringIO(hash_[:4]), 4)

        # Execute the JSON-RPC call:
        payload = dumps(id_, self.service, kwargs or args)
        headers = {'Content-Type' : 'application/json'}
        reply = requests.post(self.uri, auth=(self.username, self.password),
                              data=payload, timeout=self.timeout)
        if reply.status_code >= 500:
            reply.raise_for_status()
        response = loads(reply.content)

        # Process the response object:
        #if 'jsonrpc' not in response:
        #    raise ResponseError(u"server reply was not JSON-RPC object")
        if 'id' not in response or response['id'] != id_:
            raise ResponseError(u"response id does not match request id")
        if ('error' in response and response['error'] is not None and
            'result' in response and response['result'] is not None):
            raise ResponseError(u"server reply may not contain both 'result' and 'error'")

        if 'error' in response and response['error'] is not None:
            raise Fault(
                'code'        in response['error'] and response['error']['code']        or -1,
                'message'     in response['error'] and response['error']['message']     or '',
                'description' in response['error'] and response['error']['description'] or None)
        elif 'result' in response and response['result'] is not None:
            return response['result']
        else:
            raise ResponseError(u"server reply must contain one of 'result' or 'error'")

#
# End of File
#
