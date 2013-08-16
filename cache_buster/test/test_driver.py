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

from twisted.internet.defer import Deferred, succeed, fail
from twisted.python.failure import Failure
from twisted.trial import unittest

from cache_buster.driver import Driver
from cache_buster.keys import FormattingKeyThingy
from cache_buster.test.doubles import DummyLogger


class DriverTests(unittest.TestCase):
    def test_construct(self):
        Driver(FormattingKeyThingy({}), None, None)

    def test_invalidate_row_calls_cache_delete(self):
        cache = pretend.stub(
            delete=pretend.call_recorder(lambda key: succeed(None))
        )
        d = Driver(FormattingKeyThingy({
            "foo_table": ["bar", "baz"]
        }), cache, DummyLogger())
        d.invalidate_row("foo_table", {})
        self.assertEqual(cache.delete.calls, [pretend.call("bar"), pretend.call("baz")])

    def test_invalidate_row_returns_deferred(self):
        d = Driver(FormattingKeyThingy({}), None, DummyLogger())
        res = self.successResultOf(d.invalidate_row("foo_table", {}))
        self.assertIs(res, None)

    def test_invalidate_row_returns_deferred_fired_when_cache_delete_fires(self):
        d1 = Deferred()
        cache = pretend.stub(
            delete=lambda key: d1,
        )
        d = Driver(FormattingKeyThingy({
            "foo_table": ["bar"]
        }), cache, DummyLogger())
        invalidate_d = d.invalidate_row("foo_table", {})
        self.assertNoResult(invalidate_d)
        d1.callback(None)
        res = self.successResultOf(invalidate_d)
        self.assertIs(res, None)

    def test_invalidate_row_succeeds_on_cache_delete_failure(self):
        cache = pretend.stub(
            delete=lambda key: fail(Exception()),
        )
        d = Driver(FormattingKeyThingy({
            "foo_table": ["bar"]
        }), cache, DummyLogger())
        invalidate_d = d.invalidate_row("foo_table", {})
        res = self.successResultOf(invalidate_d)
        self.assertIs(res, None)

    def test_invalidate_row_logs_on_cache_delete_failure(self):
        f = Failure(Exception())
        cache = pretend.stub(
            delete=lambda key: fail(f),
        )
        logger = pretend.stub(
            err=pretend.call_recorder(lambda failure, table, key: None)
        )
        d = Driver(FormattingKeyThingy({
            "foo_table": ["bar"]
        }), cache, logger)
        d.invalidate_row("foo_table", {})
        self.assertEqual(logger.err.calls, [pretend.call(f, "foo_table", "bar")])
