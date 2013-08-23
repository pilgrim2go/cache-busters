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

from cache_buster.driver import Driver, count_cache_results
from cache_buster.keys import FormattingKeyMaker
from cache_buster.test.doubles import DummyLogger


class DriverTests(unittest.TestCase):
    def test_construct(self):
        Driver(FormattingKeyMaker({}), None, None)

    def test_invalidate_row_calls_cache_delete(self):
        cache = pretend.stub(
            delete=pretend.call_recorder(lambda key: succeed(None))
        )
        d = Driver(FormattingKeyMaker({
            "foo_table": ["bar", "baz"]
        }), cache, DummyLogger())
        d.invalidate_row("foo_table", {})
        self.assertEqual(cache.delete.calls, [pretend.call("bar"), pretend.call("baz")])

    def test_invalidate_row_returns_deferred(self):
        d = Driver(FormattingKeyMaker({}), None, DummyLogger())
        res = self.successResultOf(d.invalidate_row("foo_table", {}))
        self.assertIs(res, None)

    def test_invalidate_row_returns_deferred_fired_when_cache_delete_fires(self):
        d1 = Deferred()
        cache = pretend.stub(
            delete=lambda key: d1,
        )
        d = Driver(FormattingKeyMaker({
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
        d = Driver(FormattingKeyMaker({
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
            msg=lambda s, **kwargs: None,
            err=pretend.call_recorder(lambda failure, table, key: None)
        )
        d = Driver(FormattingKeyMaker({
            "foo_table": ["bar"]
        }), cache, logger)
        d.invalidate_row("foo_table", {})
        self.assertEqual(logger.err.calls, [pretend.call(f, "foo_table", "bar")])

    def test_invalidate_row_logs_counts(self):
        cache = pretend.stub(
            delete=lambda key: succeed(True)
        )
        logger = pretend.stub(
            err=None,
            msg=pretend.call_recorder(lambda *args, **kwargs: None),
        )
        d = Driver(FormattingKeyMaker({
            "foo_table": ["bar", "baz"]
        }), cache, logger)
        d.invalidate_row("foo_table", {})
        self.assertEqual(logger.msg.calls, [
            pretend.call("cache_buster.driver.invalidated_rows",
                deletes=2, nonexistant=0, failures=0,
            )
        ])

    def test_invalidate_row_logs_nonexistant_counts(self):
        cache = pretend.stub(
            delete=lambda key: succeed(False)
        )
        logger = pretend.stub(
            err=None,
            msg=pretend.call_recorder(lambda *args, **kwargs: None)
        )
        d = Driver(FormattingKeyMaker({
            "foo_table": ["bar"]
        }), cache, logger)
        d.invalidate_row("foo_table", {})
        self.assertEqual(logger.msg.calls, [
            pretend.call("cache_buster.driver.invalidated_rows",
                deletes=0, nonexistant=1, failures=0,
            )
        ])

    def test_invalidate_row_logs_failure_counts(self):
        cache = pretend.stub(
            delete=lambda key: fail(Exception())
        )
        logger = pretend.stub(
            err=lambda failure, table, key: None,
            msg=pretend.call_recorder(lambda *args, **kwargs: None)
        )
        d = Driver(FormattingKeyMaker({
            "foo_table": ["bar"]
        }), cache, logger)
        d.invalidate_row("foo_table", {})
        self.assertEqual(logger.msg.calls, [
            pretend.call("cache_buster.driver.invalidated_rows",
                deletes=0, nonexistant=0, failures=1,
            )
        ])


class CountCacheResultsTests(unittest.TestCase):
    def test_many_results(self):
        deletes, nonexistant, failures = count_cache_results([
            True,
            False,
            None,
            False,
            True
        ])
        self.assertEqual(deletes, 2)
        self.assertEqual(nonexistant, 2)
        self.assertEqual(failures, 1)
