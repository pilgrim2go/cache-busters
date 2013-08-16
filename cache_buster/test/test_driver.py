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

from twisted.internet.defer import succeed
from twisted.trial import unittest

from cache_buster.driver import Driver
from cache_buster.keys import FormattingKeyThingy


class DriverTests(unittest.TestCase):
    def test_construct(self):
        Driver(FormattingKeyThingy({}), None)

    def test_invalidate_row_calls_cache_delete(self):
        cache = pretend.stub(
            delete=pretend.call_recorder(lambda key: succeed(None))
        )
        d = Driver(FormattingKeyThingy({
            "foo_table": ["bar", "baz"]
        }), cache)
        d.invalidate_row("foo_table", {})
        self.assertEqual(cache.delete.calls, [pretend.call("bar"), pretend.call("baz")])
