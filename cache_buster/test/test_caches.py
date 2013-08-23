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
import pretend

from twisted.internet.defer import succeed, Deferred
from twisted.internet.protocol import Factory
from twisted.trial.unittest import TestCase
from twisted.protocols.memcache import MemCacheProtocol

from cache_buster.caches import MemcachedCache


class MemcachedCacheTests(TestCase):
    def test_delete_connects_to_endpoint(self):
        protocol = pretend.stub(
            delete=lambda key: succeed(True),
            transport=pretend.stub(loseConnection=lambda: None)
        )
        endpoint = pretend.stub(
            connect=pretend.call_recorder(lambda factory: succeed(protocol))
        )

        cache = MemcachedCache(endpoint)
        d = cache.delete('foo')
        self.successResultOf(d)

        self.assertEqual(len(endpoint.connect.calls), 1)
        factory = endpoint.connect.calls[0].args[0]
        self.assertIsInstance(factory, Factory)
        self.assertIs(factory.protocol, MemCacheProtocol)

    def test_delete_calls_delete_on_protocol(self):
        protocol = pretend.stub(
            delete=pretend.call_recorder(lambda key: succeed(True)),
            transport=pretend.stub(loseConnection=lambda: None)
        )
        endpoint = pretend.stub(
            connect=lambda factory: succeed(protocol)
        )

        cache = MemcachedCache(endpoint)
        d = cache.delete('foo')
        self.successResultOf(d)
        self.assertEqual(protocol.delete.calls, [pretend.call('foo')])

    def test_delete_loses_connection_on_protocol(self):
        protocol = pretend.stub(
            delete=lambda key: succeed(True),
            transport=pretend.stub(
                loseConnection=pretend.call_recorder(lambda: None)
            )
        )
        endpoint = pretend.stub(
            connect=lambda factory: succeed(protocol)
        )

        cache = MemcachedCache(endpoint)
        d = cache.delete('foo')
        self.successResultOf(d)
        self.assertEqual(
            protocol.transport.loseConnection.calls,
            [pretend.call()]
        )

    def test_delete_loses_connection_after_delete_fires(self):
        d = Deferred()
        protocol = pretend.stub(
            delete=lambda key: d,
            transport=pretend.stub(
                loseConnection=pretend.call_recorder(lambda: None)
            )
        )
        endpoint = pretend.stub(
            connect=lambda factory: succeed(protocol)
        )

        cache = MemcachedCache(endpoint)
        d2 = cache.delete('foo')
        self.assertNoResult(d2)
        self.assertEqual(protocol.transport.loseConnection.calls, [])
        d.callback(True)
        self.assertEqual(
            protocol.transport.loseConnection.calls,
            [pretend.call()]
        )

    def test_delete_loses_connection_after_delete_fails(self):
        d = Deferred()
        protocol = pretend.stub(
            delete=lambda key: d,
            transport=pretend.stub(
                loseConnection=pretend.call_recorder(lambda: None)
            )
        )
        endpoint = pretend.stub(
            connect=lambda factory: succeed(protocol)
        )

        cache = MemcachedCache(endpoint)
        d2 = cache.delete('foo')
        self.assertNoResult(d2)
        self.assertEqual(protocol.transport.loseConnection.calls, [])

        d.errback(ValueError())

        self.assertEqual(
            protocol.transport.loseConnection.calls,
            [pretend.call()]
        )
        self.failureResultOf(d2, ValueError)
