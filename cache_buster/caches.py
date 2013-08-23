"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from twisted.internet.defer import succeed
from twisted.internet.protocol import Factory
from twisted.protocols.memcache import MemCacheProtocol


class InMemoryCache(object):
    def __init__(self, storage):
        self._storage = storage

    def delete(self, key):
        try:
            del self._storage[key]
        except KeyError:
            return succeed(False)
        else:
            return succeed(True)


class MemcachedCache(object):
    def __init__(self, endpoint):
        self._endpoint = endpoint
        self._factory = Factory.forProtocol(MemCacheProtocol)

    def delete(self, key):
        def when_deleted(result, protocol):
            protocol.transport.loseConnection()
            return result

        def when_connected(protocol):
            d2 = protocol.delete(key)
            d2.addBoth(when_deleted, protocol)
            return d2

        d = self._endpoint.connect(self._factory)
        d.addCallback(when_connected)
        return d
