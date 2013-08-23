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

import textwrap

from twisted.trial.unittest import TestCase

from cache_buster.keys import FormattingKeyMaker


class KeyMakerTests(TestCase):
    def test_from_yaml(self):
        key_maker = FormattingKeyMaker.from_yaml(textwrap.dedent("""
        invalidations:
            foo_table:
                - column1
                - column2
        """))
        self.assertEqual(list(key_maker.keys_for_row("foo_table", {})), ["column1", "column2"])

    def test_keys_for_row_constant_string(self):
        key_maker = FormattingKeyMaker({"foo": ["the_big_cache"]})
        self.assertEqual(list(key_maker.keys_for_row("foo", {})), ["the_big_cache"])

    def test_keys_for_row_format_pattern(self):
        key_maker = FormattingKeyMaker({"foo": ["{user_id}"]})
        self.assertEqual(list(key_maker.keys_for_row("foo", {"user_id": "bob"})), ["bob"])

    def test_keys_for_row_invalid_format_key(self):
        key_maker = FormattingKeyMaker({"foo": ["{user_id}"]})
        self.assertEqual(list(key_maker.keys_for_row("foo", {})), [])

    def test_keys_for_row_does_not_stop_on_invalid_format(self):
        key_maker = FormattingKeyMaker({"foo": ["{user_id}", "bar"]})
        self.assertEqual(list(key_maker.keys_for_row("foo", {})), ["bar"])

    def test_keys_for_row_multiple_keys(self):
        key_maker = FormattingKeyMaker({"foo": ["abc", "def"]})
        self.assertEqual(list(key_maker.keys_for_row("foo", {})), ["abc", "def"])
